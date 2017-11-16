from aiohttp.test_utils import unittest_run_loop

from . import MockRoutesTestCase


async def request_callback(request):
    return (200, {}, await request.text())


class EndpointTestCase(MockRoutesTestCase):

    @unittest_run_loop
    async def test_endpoint_detail_route(self):
        with self.mock_response() as rsps:
            rsps.add_callback(
                'POST', '/users/2/notify',
                callback=request_callback,
                content_type='application/json',
            )

            response = await self.generic_client.users(id=2).notify(unread=3)
            self.assertEqual(await response.json(), {'unread': 3})

        with self.mock_response() as rsps:
            rsps.add_callback(
                'GET', '/users/2/notify',
                callback=request_callback,
                content_type='application/json',
            )

            response = await self.generic_client.users(_method='get', id=2).notify(unread=3)
            self.assertEqual(await response.json(), {'unread': 3})

    @unittest_run_loop
    async def test_endpoint_list_route(self):
        with self.mock_response() as rsps:

            rsps.add_callback(
                'POST', '/users/notify',
                callback=request_callback,
                content_type='application/json',
            )

            response = await self.generic_client.users().notify(unread=3)
            self.assertEqual(await response.json(), {'unread': 3})

        with self.mock_response() as rsps:
            rsps.add_callback(
                'GET', '/users/notify',
                callback=request_callback,
                content_type='application/json',
            )

            response = await self.generic_client.users(_method='get').notify(unread=3)
            self.assertEqual(await response.json(), {'unread': 3})
