from genericclient_aiohttp import GenericClient

from asynctest import TestCase


class MockRoutesTestCase(TestCase):
    API_URL = 'http://example.org'

    def setUp(self):
        super(MockRoutesTestCase, self).setUp()
        self.generic_client = self.setUpGenericClient(url=self.API_URL)

    def setUpGenericClient(self, url):
        return GenericClient(url=url)
