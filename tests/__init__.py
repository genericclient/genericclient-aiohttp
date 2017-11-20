from genericclient_aiohttp import GenericClient


from test_aiohttp import AioLoopTestCase


class MockRoutesTestCase(AioLoopTestCase):
    API_URL = 'http://example.org'

    def setUp(self):
        super(MockRoutesTestCase, self).setUp()
        self.generic_client = self.setUpGenericClient(url=self.API_URL)

    def setUpGenericClient(self, url):
        return GenericClient(url=url)
