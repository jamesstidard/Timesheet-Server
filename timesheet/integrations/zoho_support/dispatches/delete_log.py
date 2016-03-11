from tornado.httpclient import AsyncHTTPClient

from timesheet.dispatches.delete_log import delete_log
from timesheet.integrations.zoho_support.integration import ZohoSupportIntegration
from timesheet.integrations.zoho_support.utils import BASE_URL

__author__ = 'James Stidard'


@delete_log.register(ZohoSupportIntegration)
async def delete_log(log):
    client = AsyncHTTPClient()
    result = await client.fetch('{base_url}/requests/deleterecords?authtoken={token}&department={department}&portal={portal}&id={log_id}'.format(
        base_url=BASE_URL,
        department=log.integration.department,
        portal_id=log.integration.portal_id,
        log_id=log.zoho_id
    ))
    assert result.code == 200
