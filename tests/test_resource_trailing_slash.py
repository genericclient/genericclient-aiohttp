import pytest

from mocket.plugins.httpretty import HTTPretty
from mocket import Mocketizer

from genericclient_aiohttp import GenericClient

@pytest.fixture
def generic_client(api_url):
    return GenericClient(
        url=api_url,
        trailing_slash=True,
    )

@pytest.mark.asyncio
async def test_resource_delete(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.GET, '/users/1/', json={
            'id': 1,
            'username': 'user1',
            'group': 'watchers',
        })

        user1 = await generic_client.users.get(id=1)
        assert user1.username == 'user1'

    with Mocketizer():
        register_json(HTTPretty.DELETE, '/users/1/', status=204)

        await user1.delete()


@pytest.mark.asyncio
async def test_resource_delete_uuid(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.GET, '/users/1/', json={
            'uuid': 1,
            'username': 'user1',
            'group': 'watchers',
        })

        user1 = await generic_client.users.get(uuid=1)
        assert user1.username == 'user1'

    with Mocketizer():
        register_json(HTTPretty.DELETE, '/users/1/', status=204)

        await user1.delete()


@pytest.mark.asyncio
async def test_resource_save(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.GET, '/users/1/', json={
            'id': 1,
            'username': 'user1',
            'group': 'watchers',
        })

        user1 = await generic_client.users.get(id=1)
        assert user1.username == 'user1'

    with Mocketizer():
        register_json(HTTPretty.PUT, '/users/1/', json={
            'id': 1,
            'username': 'user1',
            'group': 'admins',
        })

        user1.group = 'admins'
        await user1.save()


@pytest.mark.asyncio
async def test_resource_save_uuid(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.GET, '/users/1/', json={
            'uuid': 1,
            'username': 'user1',
            'group': 'watchers',
        })

        user1 = await generic_client.users.get(uuid=1)
        assert user1.username == 'user1'

    with Mocketizer():
        register_json(HTTPretty.PUT, '/users/1/', json={
            'uuid': 1,
            'username': 'user1',
            'group': 'admins',
        })

        user1.group = 'admins'
        await user1.save()
