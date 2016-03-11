import json
from urllib.parse import urlencode

from tornado.httpclient import AsyncHTTPClient

from timesheet.dispatches.insert_log import insert_log
from timesheet.integrations.zoho_projects.integration import ZohoProjectsIntegration
from timesheet.integrations.zoho_projects.utils import BASE_URL
from timesheet.utils.log_exceptions import IncompleteLogException
from timesheet.utils.dot_dict import DotDict

__author__ = 'James Stidard'


@insert_log.register(ZohoProjectsIntegration)
async def insert_log(log):
    if not log.completed:
        raise IncompleteLogException('Incomplete log entry. \
                                      Cannot be submitted to Zoho.')

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
