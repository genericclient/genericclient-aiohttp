from genericclient_aiohttp import GenericClient


from test_aiohttp.rsps import MockRoutesTestCase as _MockRoutesTestCase


class MockRoutesTestCase(_MockRoutesTestCase):
    def setUp(self):
        super(MockRoutesTestCase, self).setUp()
        server_url = "http://{}:{}".format(self.server.host, self.server.port)
        self.generic_client = self.setUpGenericClient(url=server_url, session=self.client.session)

    def setUpGenericClient(self, url, session):
        return GenericClient(url=url, session=session)
