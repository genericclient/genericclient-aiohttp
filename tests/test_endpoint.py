from aiohttp.test_utils import unittest_run_loop

from . import MockRoutesTestCase


# Create your tests here.
class EndpointTestCase(MockRoutesTestCase):
    @unittest_run_loop
    async def test_endpoint_all(self):
        with self.mock_response() as rsps:
            rsps.add('GET', '/users', data=[
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

            users = await self.generic_client.users.all()
            self.assertEqual(len(users), 3)

    @unittest_run_loop
    async def test_endpoint_filter(self):
        with self.mock_response() as rsps:
            rsps.add('GET', '/users', data=[
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

            users = await self.generic_client.users.filter(group="watchers")
            self.assertEqual(len(users), 2)

        with self.mock_response() as rsps:
            rsps.add('GET', '/users?group__in=watchers&group__in=contributors', data=[
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

            users = await self.generic_client.users.filter(group__in=["watchers", "contributors"])
            self.assertEqual(len(users), 2)

    @unittest_run_loop
    async def test_endpoint_get_id(self):
        with self.mock_response() as rsps:
            rsps.add('GET', '/users/2', data={
                'id': 2,
                'username': 'user2',
                'group': 'watchers',
            })

            user2 = await self.generic_client.users.get(id=2)
            self.assertEqual(user2.username, 'user2')

        with self.mock_response() as rsps:
            rsps.add('GET', '/users/9999', status=404)

            with self.assertRaises(self.generic_client.ResourceNotFound):
                await self.generic_client.users.get(id=9999)

    @unittest_run_loop
    async def test_endpoint_get_uuid(self):
        with self.mock_response() as rsps:
            rsps.add('GET', '/users/2', data={
                'uuid': 2,
                'username': 'user2',
                'group': 'watchers',
            })

            user2 = await self.generic_client.users.get(uuid=2)
            self.assertEqual(user2.username, 'user2')

        with self.mock_response() as rsps:
            rsps.add('GET', '/users/9999', status=404)

            with self.assertRaises(self.generic_client.ResourceNotFound):
                await self.generic_client.users.get(uuid=9999)

    @unittest_run_loop
    async def test_endpoint_get_params(self):
            with self.mock_response() as rsps:
                rsps.add('GET', '/users', data=[
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

            with self.mock_response() as rsps:
                rsps.add('get', '/users', data=[])

                with self.assertRaises(self.generic_client.ResourceNotFound):
                    await self.generic_client.users.get(group='cookie_monster')

            with self.mock_response() as rsps:
                rsps.add('get', '/users', data=[
                    {
                        'id': 3,
                        'username': 'user3',
                        'group': 'admin',
                    },
                ])

                admin = await self.generic_client.users.get(role='admin')
                self.assertEqual(admin.username, 'user3')
