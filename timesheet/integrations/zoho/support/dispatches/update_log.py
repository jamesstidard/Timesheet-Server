import json

from tornado.httpclient import AsyncHTTPClient

from timesheet.dispatches.update_log import update_log
from timesheet.integrations.zoho.support.integration import ZohoSupportIntegration
from timesheet.integrations.zoho.support.utils import wrap_logs
from timesheet.integrations.zoho.support.utils import BASE_URL
from timesheet.utils.log_exceptions import IncompleteLogException

__author__ = 'James Stidard'


@update_log.register(ZohoSupportIntegration)
async def update_log(log):
    if not log.completed:
        raise IncompleteLogException('Incomplete log entry. \
                                      Cannot be submitted to Zoho.')

    client = AsyncHTTPClient()
    result = await client.fetch('{base_url}/timeentry/addrecords?authtoken={token}&department={department}&portal={portal}&xml={item}&id={log_id}'.format(
        base_url=BASE_URL,
        department=log.integration.department,
        portal_id=log.integration.portal_id,
        item=wrap_logs(log),
        log_id=log.zoho_id
    ))

    result  = result.body.decode('utf-8')
    result  = json.loads(result)

    return result['response']['result']['responsedata']['TimeEntry']['record']['id']
