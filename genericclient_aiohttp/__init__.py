from genericclient_base import BaseEndpoint, BaseGenericClient, BaseResource, exceptions, utils

from . import routes

import aiohttp


_version = "0.0.2"
__version__ = VERSION = tuple(map(int, _version.split('.')))


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

    async def http_request(self, client, method, *args, **kwargs):
        async with client.request(method, *args, **kwargs) as response:
            if self.status_code(response) == 403:
                raise exceptions.NotAuthenticatedError(response, "Cannot authenticate user `{}` on the API".format(self.api.session.auth.login))
            elif self.status_code(response) == 400:
                text = await response.text()
                raise exceptions.BadRequestError(
                    response,
                    "Bad Request 400: {}".format(text)
                )
            return response

    async def request(self, method, *args, **kwargs):
        if self.api.ainit is False:
            await self.api.__ainit__()
        response = await self.http_request(self.api.session, method, *args, **kwargs)
        return response

    async def filter(self, **kwargs):
        response = await self.request('get', self.url, params=kwargs)
        results = await self.api.hydrate_json(response)
        return [self.resource_class(self, **result) for result in results]

    async def all(self):
        return await self.filter()

    async def get(self, **kwargs):
        try:
            pk = utils.find_pk(kwargs)
            url = self._urljoin(pk)
            response = await self.request('get', url)
        except exceptions.UnknownPK:
            url = self.url
            response = await self.request('get', url, params=kwargs)

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
            return await self.resource_class(self, **payload).save()

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
    ainit = False

    def set_session(self, session, auth):
        self._session = session
        self._auth = auth

    async def __ainit__(self):
        await self.aset_session()
        self.ainit = True
        return self

    async def aset_session(self):
        if self._session is None:
            client_kwargs = {
                'auth': self._auth,
                'headers': {
                    'Content-Type': 'application/json',
                }
            }
            async with aiohttp.ClientSession(**client_kwargs) as session:
                self.session = session
        else:
            self.session = self._session
        return self

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
