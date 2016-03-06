import json
from urllib.parse import urlencode
from functools import singledispatch

from tornado.httpclient import AsyncHTTPClient

from timesheet.dispatches.get_projects import get_projects
from timesheet.integrations.zoho.projects.integration import ZohoProjectsIntegration
from timesheet.utils.dot_dict import DotDict
from timesheet.utils.log_exceptions import IncompleteLogException

__author__ = 'James Stidard'


BASE_URL = "https://projectsapi.zoho.com/restapi"


@get_projects.register(ZohoProjectsIntegration)
async def get_projects(integration):
    client = AsyncHTTPClient()
    result = await client.fetch('{base_url}/portal/{portal_id}/projects/?authtoken={token}'.format(
        base_url=BASE_URL,
        portal_id=integration.portal_id,
        token=integration.token)
    )

    body    = json.loads(result.body.decode('utf-8'))
    mapping = integration.maps.get('project')
    result  = [{mapping.get(key): value for key, value in p.items() if key in mapping} for p in body['projects']]
    result  = [DotDict(p) for p in result]

    for p in result:
        p['integration_id'] = integration.id

    return result


async def insert_project_log(log):
    if not log.completed:
        raise IncompleteLogException('Incomplete log entry. Cannot be submitted to Zoho.')

    client = AsyncHTTPClient()
    item   = urlencode(log.integration_format)
    url    = '{base_url}/portal/{portal_id}/projects/{project_id}/logs/?authtoken={token}&{item}'.format(
        base_url=BASE_URL,
        portal_id=log.integration.portal_id,
        project_id=log.project_id,
        token=log.integration.token,
        item=item
    )

    result = await client.fetch(url, method='POST', allow_nonstandard_methods=True)
    body = json.loads(result.body.decode('utf-8'))

    zoho_log = DotDict(body['timelogs']['generallogs'][0])
    return zoho_log.id


async def update_project_log(log):
    if not log.completed:
        raise IncompleteLogException('Incomplete log entry. Cannot be submitted to Zoho.')

    client = AsyncHTTPClient()
    item   = urlencode(log.integration_format)
    url    = '{base_url}/portal/{portal_id}/projects/{project_id}/logs/{log_id}?authtoken={token}&{item}'.format(
        base_url=BASE_URL,
        portal_id=log.integration.portal_id,
        project_id=log.project_id,
        log_id=log.zoho_id,
        token=log.integration.token,
        item=item,
    )

    result = await client.fetch(url, method='POST', allow_nonstandard_methods=True)
    body = json.loads(result.body.decode('utf-8'))

    zoho_log = DotDict(body['timelogs']['generallogs'][0])
    return zoho_log.id


async def delete_project_log(log):
    client = AsyncHTTPClient()
    url    = '{base_url}/portal/{portal_id}/projects/{project_id}/logs/{log_id}?authtoken={token}&{item}'.format(
        base_url=BASE_URL,
        portal_id=log.integration.portal_id,
        project_id=log.project_id,
        log_id=log.zoho_id,
        token=log.integration.token,
    )
    result = await client.fetch(url, method='POST')
    assert result.code == 200
