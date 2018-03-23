import pytest

from mocket.plugins.httpretty import HTTPretty
from mocket import Mocketizer


@pytest.mark.asyncio
async def test_endpoint_all(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.GET, '/users', json=[
           {
                'id': 1,
                'username': 'user1',
                'group': 'watchers',
            },
            {
                'id': 2,
                'username': 'user2',
                'group': 'watchers',
            },
            {
                'id': 3,
                'username': 'user3',
                'group': 'admin',
            },
        ])
        async with generic_client as session:
            users = await session.users.all()
        assert len(users) == 3


@pytest.mark.asyncio
async def test_endpoint_create(generic_client, register_json):
    user = {
        'id': 1,
        'username': 'user1',
        'group': 'watchers',
    }

    with Mocketizer():
        register_json(HTTPretty.POST, '/users', json=user, status=201)

        async with generic_client as session:
            user_resource = await session.users.create(user)
        assert user_resource.id == 1
        assert user_resource.username == 'user1'


@pytest.mark.asyncio
async def test_endpoint_create_or_update(generic_client, register_json):
    user = {
        'id': 1,
        'username': 'user1',
        'group': 'watchers',
    }

    with Mocketizer():
        register_json(HTTPretty.PUT, '/users/1', json=user, status=200)

        async with generic_client as session:
            user_resource = await session.users.create_or_update(user)
        assert user_resource.id == 1
        assert user_resource.username == 'user1'

    payload = user.copy()
    del payload['id']
    with Mocketizer():
        register_json(HTTPretty.POST, '/users', json=user, status=201)

        async with generic_client as session:
            user_resource = await session.users.create_or_update(payload)
        assert user_resource.id == 1
        assert user_resource.username == 'user1'


@pytest.mark.asyncio
async def test_endpoint_get_or_create(generic_client, register_json):
    user = {
        'id': 1,
        'username': 'user1',
        'group': 'watchers',
    }

    with Mocketizer():
        register_json(HTTPretty.GET, '/users/user1', json=user, status=200)
        async with generic_client as session:
            user_resource = await session.users.get_or_create(
                username='user1',
                defaults={'group': 'watchers'}
            )
        assert user_resource.id == 1
        assert user_resource.username == 'user1'


@pytest.mark.asyncio
async def test_endpoint_get_or_create2(generic_client, register_json):
    user = {
        'id': 1,
        'username': 'user1',
        'group': 'watchers',
    }
    with Mocketizer():
        register_json(HTTPretty.GET, '/users/user1', status=404)
        register_json(HTTPretty.POST, '/users', json=user, status=201)

        async with generic_client as session:
            user_resource = await session.users.get_or_create(
                username='user1',
                defaults={'group': 'watchers'}
            )
        assert user_resource.id == 1
        assert user_resource.username == 'user1'


@pytest.mark.asyncio
async def test_endpoint_create_httperror(generic_client, register_json):
    user = {
        'id': 1,
        'username': 'user1',
        'group': 'watchers',
    }

    with Mocketizer():
        register_json(HTTPretty.POST, '/users', json=user, status=500)

        with pytest.raises(generic_client.HTTPError):
            async with generic_client as session:
                await session.users.create(user)


@pytest.mark.asyncio
async def test_endpoint_delete(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.DELETE, '/users/1', status=204)

        async with generic_client as session:
            await session.users.delete(1)


@pytest.mark.asyncio
async def test_endpoint_delete_404(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.DELETE, '/users/1', status=404)

        with pytest.raises(generic_client.ResourceNotFound):
            async with generic_client as session:
                await session.users.delete(1)


@pytest.mark.asyncio
async def test_endpoint_delete_httperror(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.DELETE, '/users/1', status=500)

        with pytest.raises(generic_client.HTTPError):
            async with generic_client as session:
                await session.users.delete(1)

            
@pytest.mark.asyncio
async def test_endpoint_filter(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.GET, '/users?group=watchers', json=[
            {
                'id': 1,
                'username': 'user1',
                'group': 'watchers',
            },
            {
                'id': 2,
                'username': 'user2',
                'group': 'watchers',
            },
        ])

        async with generic_client as session:
            users = await session.users.filter(group="watchers")
        assert len(users) == 2

        register_json(HTTPretty.GET, '/users?group__in=watchers&group__in=contributors', json=[
            {
                'id': 1,
                'username': 'user1',
                'group': 'watchers',
            },
            {
                'id': 2,
                'username': 'user2',
                'group': 'contributors',
            },
        ])

        async with generic_client as session:
            users = await session.users.filter(group__in=["watchers", "contributors"])
        assert len(users) == 2

        register_json(HTTPretty.GET, '/users?id__in=1&id__in=2', json=[
            {
                'id': 1,
                'username': 'user1',
                'group': 'watchers',
            },
            {
                'id': 2,
                'username': 'user2',
                'group': 'contributors',
            },
        ])

        users = await generic_client.users.filter(id__in=[1, 2])
        assert len(users) == 2


@pytest.mark.asyncio
async def test_endpoint_get_id(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.GET, '/users/2', json={
            'id': 2,
            'username': 'user2',
            'group': 'watchers',
        })
        register_json(HTTPretty.GET, '/users/9999', status=404)

        async with generic_client as session:
            user2 = await session.users.get(id=2)
            assert user2.username == 'user2'

            with pytest.raises(generic_client.ResourceNotFound):
                await session.users.get(id=9999)


@pytest.mark.asyncio
async def test_endpoint_get_uuid(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.GET, '/users/2', json={
            'uuid': 2,
            'username': 'user2',
            'group': 'watchers',
        })

        user2 = await generic_client.users.get(uuid=2)
        assert user2.username == 'user2'

        register_json(HTTPretty.GET, '/users/9999', status=404)

        with pytest.raises(generic_client.ResourceNotFound):
            await generic_client.users.get(uuid=9999)


@pytest.mark.asyncio
async def test_endpoint_get_params(generic_client, register_json):
    with Mocketizer():
        register_json(HTTPretty.GET, '/users?group=watchers', json=[
            {
                'id': 1,
                'username': 'user1',
                'group': 'watchers',
            },
            {
                'id': 2,
                'username': 'user2',
                'group': 'watchers',
            },
        ])

        with pytest.raises(generic_client.MultipleResourcesFound):
            await generic_client.users.get(group='watchers')

        register_json(HTTPretty.GET, '/users?group=cookie_monster', json=[])

        with pytest.raises(generic_client.ResourceNotFound):
            await generic_client.users.get(group='cookie_monster')

        register_json(HTTPretty.GET, '/users?role=admin', json=[
            {
                'id': 3,
                'username': 'user3',
                'group': 'admin',
            },
        ])

        admin = await generic_client.users.get(role='admin')
        assert admin.username == 'user3'


@pytest.mark.asyncio
async def test_endpoint_links(generic_client, register_json):
    with Mocketizer():
        register_json(
            HTTPretty.GET, '/users?page=2',
            json=[
                {
                    'id': 3,
                    'username': 'user1',
                    'group': 'watchers',
                },
                {
                    'id': 4,
                    'username': 'user2',
                    'group': 'watchers',
                },
            ],
            link='<http://example.com/users?page=3>; rel=next,<http://example.com/users?page=1>; rel=previous',
        )
        users = await generic_client.users.filter(page=2)

        assert users.response.links == {
            'next': {'url': 'http://example.com/users?page=3', 'rel': 'next'},
            'previous': {'url': 'http://example.com/users?page=1', 'rel': 'previous'}
        }

