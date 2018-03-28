import pytest

from mocket.plugins.httpretty import HTTPretty
from mocket import Mocketizer

from genericclient_aiohttp import GenericClient
from genericclient_aiohttp.pagination import link_header


@pytest.mark.asyncio
async def test_paginate(api_url, register_json):
    generic_client = GenericClient(url=api_url, autopaginate=link_header)

    with Mocketizer():
        register_json(
            HTTPretty.GET, '/users', json=[{'id': 1}],
            link='<{api_url}/users?page=2>; rel=next'.format(api_url=api_url)
        )
        register_json(
            HTTPretty.GET, '/users?page=2', json=[{'id': 2}],
            link='<{api_url}/users>; rel=previous, <{api_url}/users?page=3>; rel=next'.format(api_url=api_url)
        )
        register_json(
            HTTPretty.GET, '/users?page=3', json=[{'id': 3}],
            link='<{api_url}/users?page=2>; rel=previous'.format(api_url=api_url)
        )
        users = await generic_client.users.all()

        assert len(users) == 3
        assert users[0].id == 1
        assert users[1].id == 2
        assert users[2].id == 3
