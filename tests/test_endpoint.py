from test_aiohttp import RouteManager

from . import MockRoutesTestCase


# Create your tests here.
class EndpointTestCase(MockRoutesTestCase):
    async def test_endpoint_all(self):
        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users', json=[
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

            async with self.generic_client as session:
                users = await session.users.all()
                self.assertEqual(len(users), 3)

    async def test_endpoint_filter(self):
        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users', json=[
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

            async with self.generic_client as session:
                users = await session.users.filter(group="watchers")
            self.assertEqual(len(users), 2)

        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users?group__in=watchers&group__in=contributors', json=[
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
            ], match_querystring=True)

            async with self.generic_client as session:
                users = await session.users.filter(group__in=["watchers", "contributors"])
            self.assertEqual(len(users), 2)

        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users?id__in=1&id__in=2', json=[
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
            ], match_querystring=True)

            users = await self.generic_client.users.filter(id__in=[1, 2])
            self.assertEqual(len(users), 2)

    async def test_endpoint_get_id(self):
        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users/2', json={
                'id': 2,
                'username': 'user2',
                'group': 'watchers',
            })
            rsps.add('GET', self.API_URL + '/users/9999', status=404)

            async with self.generic_client as session:
                user2 = await session.users.get(id=2)
                self.assertEqual(user2.username, 'user2')

                with self.assertRaises(self.generic_client.ResourceNotFound):
                    await session.users.get(id=9999)

    async def test_endpoint_get_uuid(self):
        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users/2', json={
                'uuid': 2,
                'username': 'user2',
                'group': 'watchers',
            })

            user2 = await self.generic_client.users.get(uuid=2)
            self.assertEqual(user2.username, 'user2')

        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users/9999', status=404)

            with self.assertRaises(self.generic_client.ResourceNotFound):
                await self.generic_client.users.get(uuid=9999)

    async def test_endpoint_get_params(self):
            with RouteManager() as rsps:
                rsps.add('GET', self.API_URL + '/users', json=[
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

                with self.assertRaises(self.generic_client.MultipleResourcesFound):
                    await self.generic_client.users.get(group='watchers')

            with RouteManager() as rsps:
                rsps.add('get', self.API_URL + '/users', json=[])

                with self.assertRaises(self.generic_client.ResourceNotFound):
                    await self.generic_client.users.get(group='cookie_monster')

            with RouteManager() as rsps:
                rsps.add('get', self.API_URL + '/users', json=[
                    {
                        'id': 3,
                        'username': 'user3',
                        'group': 'admin',
                    },
                ])

                admin = await self.generic_client.users.get(role='admin')
                self.assertEqual(admin.username, 'user3')

    async def test_endpoint_links(self):
        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users?page=2', json=[
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
            ], headers={
                'Link': '<http://example.com/users?page=3>; rel=next,<http://example.com/users?page=1>; rel=previous'
            }, match_querystring=True)
            users = await self.generic_client.users.filter(page=2)

        self.assertEqual(users.response.links, {
            'next': {'url': 'http://example.com/users?page=3', 'rel': 'next'},
            'previous': {'url': 'http://example.com/users?page=1', 'rel': 'previous'}
        })
