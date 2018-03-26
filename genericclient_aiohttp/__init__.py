import logging

from genericclient_base import (
    ParsedResponse,
    BaseEndpoint, BaseGenericClient, BaseResource, exceptions, utils,
)

from . import routes

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError
from failsafe import Failsafe, RetryPolicy, CircuitBreaker


_version = "1.1.5"
__version__ = VERSION = tuple(map(int, _version.split('.')))


logger = logging.getLogger(__name__)


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
        else:
            response = await self._endpoint.request('post', self._endpoint.url, json=self.payload)
        self.payload = response.data
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

    def convert_lookup(self, lookup):
        return convert_lookup(lookup)

    async def http_request(self, method, url, *args, **kwargs):
        async with self.api.session as session:
            async with session.request(method, url, *args, **kwargs) as response:
                if response.status == 403:
                    if self.api.auth:
                        msg = "Failed request to `{}`. Cannot authenticate user `{}` on the API.".format(
                            url, self.api.auth.login,
                        )
                        raise exceptions.NotAuthenticatedError(
                            response, msg,
                        )
                    else:
                        raise exceptions.NotAuthenticatedError(response, "User is not authenticated on the API")

                elif response.status == 400:
                    text = await response.text()
                    raise exceptions.BadRequestError(
                        response,
                        "Bad Request 400: {}".format(text)
                    )
                status = response.status
                headers = response.headers
                data = await self.api.hydrate_data(response)
        return ParsedResponse(status_code=status, headers=headers, data=data)

    async def request(self, method, url, *args, **kwargs):
        response = await self.api.failsafe.run(lambda: self.http_request(method, url, *args, **kwargs))
        return response

    async def filter(self, **kwargs):
        params = self.convert_lookup(kwargs)
        response = await self.request('get', self.url, params=params)
        return self.resource_set_class(response, [self.resource_class(self, **result) for result in response.data])

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

        if response.status_code == 404:
            raise exceptions.ResourceNotFound("No `{}` found for {}".format(self.name, kwargs))

        result = response.data

        if isinstance(result, list):
            if len(result) == 0:
                raise exceptions.ResourceNotFound("No `{}` found for {}".format(self.name, kwargs))
            if len(result) > 1:
                raise exceptions.MultipleResourcesFound("Found {} `{}` for {}".format(len(result), self.name, kwargs))

            return self.resource_class(self, **result[0])

        return self.resource_class(self, **result)

    async def create(self, payload):
        response = await self.request('post', self.url, json=payload)
        if response.status_code != 201:
            raise exceptions.HTTPError(response)

        return self.resource_class(self, **response.data)

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

        if response.status_code == 404:
            raise exceptions.ResourceNotFound("No `{}` found for pk {}".format(self.name, pk))

        if response.status_code != 204:
            raise exceptions.HTTPError(response)

        return None


class GenericClient(BaseGenericClient):
    endpoint_class = Endpoint

    def __init__(self, url, auth=None, session=None, trailing_slash=False, retries=6):
        if auth is not None and not isinstance(auth, aiohttp.BasicAuth):
            auth = aiohttp.BasicAuth(*auth)
        super(GenericClient, self).__init__(url, auth, session, trailing_slash)
        max_failures = retries - 1
        circuit_breaker = CircuitBreaker(maximum_failures=max_failures)
        retry_policy = RetryPolicy(
            allowed_retries=retries,
            retriable_exceptions=[ClientConnectionError],
            abortable_exceptions=[
                exceptions.BadRequestError,
                exceptions.NotAuthenticatedError,
                exceptions.ResourceNotFound,
                exceptions.MultipleResourcesFound,
                exceptions.HTTPError,
                ValueError,
            ],
        )
        self.failsafe = Failsafe(circuit_breaker=circuit_breaker, retry_policy=retry_policy)

    def make_session(self):
        return aiohttp.ClientSession(auth=self.auth, headers={
            'Content-Type': 'application/json',
        })

    def get_or_create_session(self):
        if self._session is None or self._session.closed:
            logger.debug('Creating new session.')
            self._session = self.make_session()
        return self._session

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._session.__aexit__(*args, **kwargs)

    async def hydrate_data(self, response):
        if response.status == 204:
            return None
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
