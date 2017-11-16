from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web

from genericclient_aiohttp import GenericClient


class RequestClientTestCase(AioHTTPTestCase):
    async def get_application(self):
        return web.Application()

    @unittest_run_loop
    async def test_host(self):
        client = await GenericClient(url='http://dummy.org')
        self.assertEqual(client.host, 'dummy.org')

        client = await GenericClient(url='http://dummy.org:8000')
        self.assertEqual(client.host, 'dummy.org:8000')

        client = await GenericClient(url='http://dummy.org:8000/api')
        self.assertEqual(client.host, 'dummy.org:8000')

        client = await GenericClient(url='http://dummy.org/api')
        self.assertEqual(client.host, 'dummy.org')
