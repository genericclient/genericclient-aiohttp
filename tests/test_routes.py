from test_aiohttp import RouteManager

from . import MockRoutesTestCase


async def request_callback(request):
    return (200, {}, 'ok')


class EndpointTestCase(MockRoutesTestCase):

    async def test_endpoint_detail_route(self):
        with RouteManager() as rsps:
            rsps.add_callback(
                'POST', self.API_URL + '/users/2/notify',
                callback=request_callback,
                content_type='application/json',
            )

            response = await self.generic_client.users(id=2).notify(unread=3)
            self.assertEqual(await response.text(), 'ok')

        with RouteManager() as rsps:
            rsps.add_callback(
                'GET', self.API_URL + '/users/2/notify',
                callback=request_callback,
                content_type='application/json',
            )

            response = await self.generic_client.users(_method='get', id=2).notify(unread=3)
            self.assertEqual(await response.text(), 'ok')

    async def test_endpoint_list_route(self):
        with RouteManager() as rsps:

            rsps.add_callback(
                'POST', self.API_URL + '/users/notify',
                callback=request_callback,
                content_type='application/json',
            )

            response = await self.generic_client.users().notify(unread=3)
            self.assertEqual(await response.text(), 'ok')

        with RouteManager() as rsps:
            rsps.add_callback(
                'GET', self.API_URL + '/users/notify',
                callback=request_callback,
                content_type='application/json',
            )

            response = await self.generic_client.users(_method='get').notify(unread=3)
            self.assertEqual(await response.text(), 'ok')
