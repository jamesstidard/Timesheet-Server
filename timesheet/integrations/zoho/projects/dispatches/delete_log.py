from tornado.httpclient import AsyncHTTPClient

from timesheet.dispatches.delete_log import delete_log
from timesheet.integrations.zoho.projects.integration import ZohoProjectsIntegration
from timesheet.integrations.zoho.projects.utils import BASE_URL

__author__ = 'James Stidard'


@delete_log.register(ZohoProjectsIntegration)
async def delete_log(log):
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
