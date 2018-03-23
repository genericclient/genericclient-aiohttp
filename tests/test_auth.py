from mocket.plugins.httpretty import HTTPretty
from mocket import Mocketizer
import pytest


from genericclient_aiohttp import GenericClient


@pytest.mark.asyncio
async def test_403(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.GET, '/users', status=403)
        with pytest.raises(generic_client.NotAuthenticatedError):
            async with generic_client as session:
                await session.users.all()


@pytest.mark.asyncio
async def test_403_auth(api_url, register_json):
    generic_client = GenericClient(
        url=api_url,
        auth=('username', 'password'),
    )
    with Mocketizer():
        register_json(HTTPretty.GET, '/users', status=403)
        with pytest.raises(generic_client.NotAuthenticatedError) as excinfo:
            async with generic_client as session:
                await session.users.all()

        assert 'username' in str(excinfo.value)
