from unittest import TestCase

from aiohttp import web

from genericclient_aiohttp import GenericClient


class RequestClientTestCase(TestCase):
    async def get_application(self):
        return web.Application()

    def test_host(self):
        client = GenericClient(url='http://dummy.org')
        self.assertEqual(client.host, 'dummy.org')

        client = GenericClient(url='http://dummy.org:8000')
        self.assertEqual(client.host, 'dummy.org:8000')

        client = GenericClient(url='http://dummy.org:8000/api')
        self.assertEqual(client.host, 'dummy.org:8000')

        client = GenericClient(url='http://dummy.org/api')
        self.assertEqual(client.host, 'dummy.org')
