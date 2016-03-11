import json

from tornado.httpclient import AsyncHTTPClient

from timesheet.dispatches.get_projects import get_projects
from timesheet.integrations.zoho_projects.integration import ZohoProjectsIntegration
from timesheet.integrations.zoho_projects.utils import BASE_URL
from timesheet.utils.dot_dict import DotDict

__author__ = 'James Stidard'


@get_projects.register(ZohoProjectsIntegration)
async def get_projects(integration):
    client = AsyncHTTPClient()
    result = await client.fetch('{base_url}/portal/{portal_id}/projects/?authtoken={token}'.format(
        base_url=BASE_URL,
        portal_id=integration.portal_id,
        token=integration.token
    ))

    body    = json.loads(result.body.decode('utf-8'))
    mapping = integration.maps.get('project')
    result  = [{mapping.get(key): value for key, value in p.items() if key in mapping} for p in body['projects']]
    result  = [DotDict(p) for p in result]

    for p in result:
        p['integration_id'] = integration.id

    return result
