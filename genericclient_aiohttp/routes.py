from genericclient_base import routes


class Action(routes.Action):

    async def __call__(self, **kwargs):
        return await self.endpoint.request(self.method, self.url, json=kwargs)


class ListAction(Action):
    pass


class DetailAction(routes.DetailAction):
    async def __call__(self, **kwargs):
        return await self.endpoint.request(self.method, self.url, json=kwargs)


class ListRoute(routes.ListRoute):
    action_class = ListAction


class DetailRoute(routes.DetailRoute):
    action_class = DetailAction
