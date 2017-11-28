from genericclient_base import (
    BaseEndpoint, BaseGenericClient, BaseResource, exceptions, utils,
)

from . import routes
from .links import parse_response_links

import aiohttp


_version = "0.0.10"
__version__ = VERSION = tuple(map(int, _version.split('.')))


def convert_lookup(lookup):
    items = lookup.items()
    multi_dict = []
    for k, v in items:
        if isinstance(v, (tuple, list)):
            for item in v:
                multi_dict.append((k, str(item)))
        else:
            multi_dict.append((k, str(v)))
    return multi_dict


class Resource(BaseResource):
    async def save(self):
        if self.pk is not None:
            url = self._urljoin(self.pk)
            try:
                response = await self._endpoint.request('put', url, json=self.payload)
            except exceptions.BadRequestError:
                response = await self._endpoint.request('patch', url, json=self.payload)
            results = await self._endpoint.api.hydrate_json(response)
        else:
            response = await self._endpoint.request('post', url, json=self.payload)
            results = await self._endpoint.api.hydrate_json(response)
        self.payload = results
        return self

    async def delete(self):
        url = self._urljoin(self.pk)
        await self._endpoint.request('delete', url)


class Endpoint(BaseEndpoint):
    resource_class = Resource
    detail_route_class = routes.DetailRoute
    list_route_class = routes.ListRoute

    def __call__(self, _method='post', **kwargs):
        if kwargs:
            return self.detail_route_class(self, _method, **kwargs)
        else:
            return self.list_route_class(self, _method)

    def status_code(self, response):
        return response.status

    def convert_lookup(self, lookup):
        return convert_lookup(lookup)

    async def http_request(self, session, method, url, *args, **kwargs):
        async with session.request(method, url, *args, **kwargs) as response:
            if self.status_code(response) == 403:
                if self.api.auth:
                    msg = "Failed request to `{}`. Cannot authenticate user `{}` on the API.".format(
                        url, self.api.auth.login,
                    )
                else:
                    msg = "Failed request to `{}`. User is not authenticated.".format(
                        url,
                    )
                    raise exceptions.NotAuthenticatedError(response, "User is not authenticated on the API")
                raise exceptions.NotAuthenticatedError(
                    response, msg,
                )

            elif self.status_code(response) == 400:
                text = await response.text()
                raise exceptions.BadRequestError(
                    response,
                    "Bad Request 400: {}".format(text)
                )
            return response

    async def request(self, method, url, *args, **kwargs):
        if self.api.session is not None and not self.api.session.closed:
            response = await self.http_request(self.api.session, method, url, *args, **kwargs)
        else:
            async with self.api.make_session() as session:
                response = await self.http_request(session, method, url, *args, **kwargs)
        response.links = parse_response_links(response)
        return response

    async def filter(self, **kwargs):
        params = self.convert_lookup(kwargs)
        response = await self.request('get', self.url, params=params)
        results = await self.api.hydrate_json(response)
        return self.resource_set_class(response, [self.resource_class(self, **result) for result in results])

    async def all(self):
        return await self.filter()

    async def get(self, **kwargs):
        try:
            pk = utils.find_pk(kwargs)
            url = self._urljoin(pk)
            response = await self.request('get', url)
        except exceptions.UnknownPK:
            url = self.url
            params = self.convert_lookup(kwargs)
            response = await self.request('get', url, params=params)

        if self.status_code(response) == 404:
            raise exceptions.ResourceNotFound("No `{}` found for {}".format(self.name, kwargs))

        result = await self.api.hydrate_json(response)

        if isinstance(result, list):
            if len(result) == 0:
                raise exceptions.ResourceNotFound("No `{}` found for {}".format(self.name, kwargs))
            if len(result) > 1:
                raise exceptions.MultipleResourcesFound("Found {} `{}` for {}".format(len(result), self.name, kwargs))

            return self.resource_class(self, **result[0])

        return self.resource_class(self, **result)

    async def create(self, payload):
        response = await self.request('post', self.url, json=payload)
        if self.status_code(response) != 201:
            raise exceptions.HTTPError(response)

        result = await self.api.hydrate_json(response)
        return self.resource_class(self, **result)

    async def get_or_create(self, **kwargs):
        defaults = kwargs.pop('defaults', {})
        try:
            resource = await self.get(**kwargs)
            return resource
        except exceptions.ResourceNotFound:
            params = {k: v for k, v in kwargs.items()}
            params.update(defaults)
            return await self.create(params)

    async def create_or_update(self, payload):
        if 'id' in payload or 'uuid' in payload:
            resource = self.resource_class(self, **payload)
            return await resource.save()

        return await self.create(payload)

    async def delete(self, pk):
        url = self._urljoin(pk)

        response = await self.request('delete', url)

        if self.status_code(response) == 404:
            raise exceptions.ResourceNotFound("No `{}` found for pk {}".format(self.name, pk))

        if self.status_code(response) != 204:
            raise exceptions.HTTPError(response)

        return None


class GenericClient(BaseGenericClient):
    endpoint_class = Endpoint

    def set_session(self, session, auth):
        if auth is not None and not isinstance(auth, aiohttp.BasicAuth):
            auth = aiohttp.BasicAuth(*auth)
        self.session = None
        self.auth = auth

    def make_session(self):
        return aiohttp.ClientSession(auth=self.auth, headers={
            'Content-Type': 'application/json',
        })

    async def __aenter__(self):
        session = self.make_session()
        self.session = session
        return self

    async def __aexit__(self, *args, **kwargs):
        if self.session is not None:
            await self.session.__aexit__(*args, **kwargs)
            self.session = None

    async def hydrate_json(self, response):
        try:
            result = await response.json()
            return result
        except ValueError:
            text = await response.text()
            raise ValueError(
                "Response from server is not valid JSON. Received {}: {}".format(
                    response.status,
                    text,
                ),
            )
