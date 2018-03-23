import pytest

from mocket.plugins.httpretty import HTTPretty
from mocket import Mocketizer

from genericclient_aiohttp import GenericClient


def test_host():
    client = GenericClient(url='http://dummy.org')
    assert client.host == 'dummy.org'

    client = GenericClient(url='http://dummy.org:8000')
    assert client.host == 'dummy.org:8000'

    client = GenericClient(url='http://dummy.org:8000/api')
    assert client.host == 'dummy.org:8000'

    client = GenericClient(url='http://dummy.org/api')
    assert client.host == 'dummy.org'


@pytest.mark.asyncio
async def test_invalid_data(generic_client, api_url):
    with Mocketizer():
        HTTPretty.register_uri(
            HTTPretty.GET, api_url + '/users', body='[not json]',
            content_type='application/json',
        )
        with pytest.raises(ValueError) as excinfo:
            await generic_client.users.all()

        assert '[not json]' in str(excinfo.value)

