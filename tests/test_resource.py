from test_aiohttp import RouteManager

from . import MockRoutesTestCase


# Create your tests here.
class ResourceTestCase(MockRoutesTestCase):
    async def test_resource_delete(self):
        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users/1', json={
                'id': 1,
                'username': 'user1',
                'group': 'watchers',
            })

            user1 = await self.generic_client.users.get(id=1)
            self.assertEqual(user1.username, 'user1')

        with RouteManager() as rsps:
            rsps.add('DELETE', self.API_URL + '/users/1', status=204)

            await user1.delete()

    async def test_resource_delete_uuid(self):
        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users/1', json={
                'uuid': 1,
                'username': 'user1',
                'group': 'watchers',
            })

            user1 = await self.generic_client.users.get(uuid=1)
            self.assertEqual(user1.username, 'user1')

        with RouteManager() as rsps:
            rsps.add('DELETE', self.API_URL + '/users/1', status=204)

            await user1.delete()

    async def test_resource_save(self):
        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users/1', json={
                'id': 1,
                'username': 'user1',
                'group': 'watchers',
            })

            user1 = await self.generic_client.users.get(id=1)
            self.assertEqual(user1.username, 'user1')

        with RouteManager() as rsps:
            rsps.add('PUT', self.API_URL + '/users/1', json={
                'id': 1,
                'username': 'user1',
                'group': 'admins',
            })

            user1.group = 'admins'
            await user1.save()

    async def test_resource_save_uuid(self):
        with RouteManager() as rsps:
            rsps.add('GET', self.API_URL + '/users/1', json={
                'uuid': 1,
                'username': 'user1',
                'group': 'watchers',
            })

            user1 = await self.generic_client.users.get(uuid=1)
            self.assertEqual(user1.username, 'user1')

        with RouteManager() as rsps:
            rsps.add('PUT', self.API_URL + '/users/1', json={
                'uuid': 1,
                'username': 'user1',
                'group': 'admins',
            })

            user1.group = 'admins'
            await user1.save()
