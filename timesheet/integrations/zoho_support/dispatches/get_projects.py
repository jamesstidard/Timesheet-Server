import json

from tornado.httpclient import AsyncHTTPClient

from timesheet.dispatches.get_projects import get_projects
from timesheet.integrations.zoho_support.integration import ZohoSupportIntegration
from timesheet.integrations.zoho_support.utils import unwrap_projects
from timesheet.integrations.zoho_support.utils import BASE_URL
from timesheet.utils.dot_dict import DotDict

__author__ = 'James Stidard'


@get_projects.register(ZohoSupportIntegration)
async def get_projects(integration):
    client = AsyncHTTPClient()
    result = await client.fetch('{base_url}/Cases/getrecords?authtoken={token}&portal={portal}&department={department}'.format(
        base_url=BASE_URL,
        portal=integration.portal_id,
        token=integration.token,
        department=integration.department,
    ))

    result  = result.body.decode('utf-8')
    result  = json.loads(result)
    mapping = integration.maps.get('project')
    result  = unwrap_projects(result, mapping)

    for p in result:
        p['integration_id'] = integration.id
        p['name'] = p['name'] + ' - ' + p.pop('subject')

    return [DotDict(p) for p in result]
