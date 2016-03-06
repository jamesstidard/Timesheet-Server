import json
from urllib.parse import urlencode

from tornado.httpclient import AsyncHTTPClient

from timesheet.utils.dot_dict import DotDict

__author__ = 'James Stidard'


BASE_URL = 'https://support.zoho.com/api/json/Cases'


async def get_projects(integration):
    client = AsyncHTTPClient()
    result = await client.fetch('{base_url}/getrecords?authtoken={token}&portal={portal}&department={department}'.format(
        base_url=BASE_URL,
        portal=integration.portal_id,
        token=integration.token,
        department=integration.department,
    ))

    result  = result.body.decode('utf-8')
    result  = json.loads(result)
    mapping = integration.maps.get('project')
    result  = _unwrap_projects(result, mapping)

    for p in result:
        p['integration_id'] = integration.id

    return [DotDict(p) for p in result]


def _unwrap_projects(result, mapping):
    cases = result['response']['result']['Cases']['row']
    return [{mapping[kv['val']]: kv['content'] for kv in c['fl'] if kv['val'] in mapping} for c in cases]


async def insert_ticket_log(log, integration):
    client = AsyncHTTPClient()
    query  = urlencode({
        "authtoken": integration.token,
        "portal": integration.portal_id,
        "department": integration.department,
        "xml": None
    })
    result = await client.fetch('{base_url}/addrecords?{query}'.format(
        base_url=BASE_URL,
        query=query
    ))

    return []


async def update_ticket_log(log, integration):
    client = AsyncHTTPClient()
    query  = urlencode({
        "authtoken": integration.token,
        "portal": integration.portal_id,
        "department": integration.department,
        "xml": None,
        "id": log.zoho_id
    })
    result = await client.fetch('{base_url}/updaterecords?{query}'.format(
        base_url=BASE_URL,
        query=query
    ))
    return []


async def delete_ticket_log(log, integration):
    client = AsyncHTTPClient()
    query  = urlencode({
        "authtoken": integration.token,
        "portal": integration.portal_id,
        "department": integration.department,
        "id": log.zoho_id
    })
    result = await client.fetch('{base_url}/deleterecords?{query}'.format(
        base_url=BASE_URL,
        query=query
    ))
    return []
