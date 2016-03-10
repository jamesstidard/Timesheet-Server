import json

from tornado.httpclient import AsyncHTTPClient

from timesheet.dispatches.get_projects import get_projects
from timesheet.dispatches.insert_log import insert_log
from timesheet.dispatches.update_log import update_log
from timesheet.dispatches.delete_log import delete_log
from timesheet.integrations.zoho.support.integration import ZohoSupportIntegration
from timesheet.utils.dot_dict import DotDict
from timesheet.utils.log_exceptions import IncompleteLogException
from timesheet.integrations.zoho.support.utils import wrap_logs, unwrap_projects

__author__ = 'James Stidard'


BASE_URL = 'https://support.zoho.com/api/json'


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


@insert_log.register(ZohoSupportIntegration)
async def insert_log(log):
    if not log.completed:
        raise IncompleteLogException('Incomplete log entry. Cannot be submitted to Zoho.')

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


@update_log.register(ZohoSupportIntegration)
async def update_log(log):
    if not log.completed:
        raise IncompleteLogException('Incomplete log entry. Cannot be submitted to Zoho.')

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
