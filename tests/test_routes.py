import pytest

from mocket.plugins.httpretty import HTTPretty
from mocket import Mocketizer


@pytest.fixture
def generic_response():
    return {
        'json': 'ok',
    }


@pytest.mark.asyncio
async def test_endpoint_detail_route(generic_client, register_json, generic_response):
    with Mocketizer():
        register_json(
            HTTPretty.POST,
            '/users/2/notify',
            **generic_response
        )

        response = await generic_client.users(id=2).notify(unread=3)
        assert response.data == 'ok'

    with Mocketizer():
        register_json(
            HTTPretty.GET,
            '/users/2/notify',
            **generic_response

        )

        response = await generic_client.users(_method='get', id=2).notify(unread=3)
        assert response.data == 'ok'


@pytest.mark.asyncio
async def test_endpoint_list_route(generic_client, register_json, generic_response):
    with Mocketizer():

        register_json(
            HTTPretty.POST,
            '/users/notify',
            **generic_response

        )

        response = await generic_client.users().notify(unread=3)
        assert response.data == 'ok'

    with Mocketizer():
        register_json(
            HTTPretty.GET,
            '/users/notify',
            **generic_response

        )

        response = await generic_client.users(_method='get').notify(unread=3)
        assert response.data == 'ok'
