import json

from tornado.httpclient import AsyncHTTPClient

from timesheet.dispatches.insert_log import insert_log
from timesheet.integrations.zoho_support.integration import ZohoSupportIntegration
from timesheet.integrations.zoho_support.utils import wrap_logs
from timesheet.integrations.zoho_support.utils import BASE_URL
from timesheet.utils.log_exceptions import IncompleteLogException

__author__ = 'James Stidard'


@insert_log.register(ZohoSupportIntegration)
async def insert_log(log):
    if not log.completed:
        raise IncompleteLogException('Incomplete log entry. \
                                      Cannot be submitted to Zoho.')

    client = AsyncHTTPClient()
    result = await client.fetch('{base_url}/timeentry/addrecords?authtoken={token}&department={department}&portal={portal}&xml={item}'.format(
        base_url=BASE_URL,
        department=log.integration.department,
        portal_id=log.integration.portal_id,
        item=wrap_logs(log)
    ))

    result  = result.body.decode('utf-8')
    result  = json.loads(result)

    return result['response']['result']['responsedata']['TimeEntry']['record']['id']
