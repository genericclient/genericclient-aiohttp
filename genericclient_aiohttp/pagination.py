async def link_header(endpoint, params):
    results = []
    lookup = params.copy()
    url = endpoint.url

    while True:
        response = await endpoint.request('get', url, params=lookup)
        results += response.data
        links = response.links
        link = links.get('next')
        if link is not None:
            lookup = {}
            url = link['url']
        else:
            break

    return response, results
