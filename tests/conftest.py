import json as jsonlib

from mocket.plugins.httpretty import HTTPretty
import pytest

from genericclient_aiohttp import GenericClient


API_URL = 'http://localhost'


@pytest.fixture
def api_url():
    return API_URL


@pytest.fixture
def generic_client():
    return GenericClient(url=API_URL)


@pytest.fixture
def register_json(api_url):
    def fn(method, url, json=None, **kwargs):
        if json is not None:
            body = jsonlib.dumps(json)
        else:
            body = ''
        kwargs.setdefault('content-type', 'application/json')
        kwargs.setdefault('match_querystring', True)
        return HTTPretty.register_uri(method, api_url + url, body, **kwargs)
    return fn
