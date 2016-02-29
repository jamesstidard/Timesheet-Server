import json
from urllib.parse import urlencode

from timesheet.model.model import Log
from timesheet.utils.dot_dict import DotDict
from tornado.httpclient import AsyncHTTPClient

from timesheet.handlers.base_handler import BaseHandler
from timesheet.utils.user_session import async_user_session

__author__ = 'James Stidard'


class IncompleteLogException(ValueError):
    pass


class LogHandler(BaseHandler):

    BASE_URL  = "https://projectsapi.zoho.com/restapi"

    @async_user_session
    async def get(self, session, user):
        logs = session.query(Log).filter(Log.user_id == user.id).all()
        self.write([l.client_format for l in logs], format='json')

    @async_user_session
    async def post(self, session, user):
        log = Log(
            project_id=self.get_json_argument('project_id'),
            task=self.get_json_argument('task'),
            start=self.get_json_argument('start', None),
            end=self.get_json_argument('end', None),
            billable=self.get_json_argument('billable', True),
            notes=self.get_json_argument('notes', ''),
            user=user,
            session=session,
        )
        session.commit()

        try:
            log.zoho_id = await LogHandler.insert_zoho_log(log)
        except IncompleteLogException:
            pass
        else:
            session.commit()
            self.write(log.client_format, format='json')

    @async_user_session
    async def put(self, session, user):
        id  = self.get_json_argument('id')
        log = session.query(Log).filter(Log.user_id == user.id).get(id)

        for property_key in ['project_id', 'task', 'start', 'end', 'billable', 'notes']:
            if property_key in self.json_arguments:
                value = self.get_json_argument(property_key)
                log.__setattr__(property_key, value)

        if not log.zoho_id:
            try:
                log.id = await LogHandler.insert_zoho_log(log)
            except IncompleteLogException:
                pass
        else:
            try:
                log.id = await LogHandler.update_zoho_log(log)
            except IncompleteLogException:
                await LogHandler.delete_zoho_log(log)
                pass

        session.commit()
        self.write(log.client_format, format='json')

    @async_user_session
    async def delete(self, session, user):
        id  = self.get_argument('id')
        log = session.query(Log).filter(Log.user_id == user.id).get(id)

        if log.zoho_id:
            await LogHandler.delete_zoho_log(log)

        session.delete(log)
        session.commit()

        self.write("Success")

    @staticmethod
    async def insert_zoho_log(log):
        if not log.completed:
            raise IncompleteLogException('Incomplete log entry. Cannot be submitted to Zoho.')

        client = AsyncHTTPClient()
        item   = urlencode(log.zoho_format)
        url    = '{base_url}/portal/{portal_id}/projects/{project_id}/logs/?authtoken={token}&{item}'.format(
            base_url=LogHandler.BASE_URL,
            portal_id=log.user.portal_id,
            project_id=log.project_id,
            token=log.user.projects_token,
            item=item
        )

        result = await client.fetch(url, method='POST', allow_nonstandard_methods=True)
        body = json.loads(result.body.decode('utf-8'))

        zoho_log = DotDict(body['timelogs']['generallogs'][0])
        return zoho_log.id

    @staticmethod
    async def update_zoho_log(log):
        if not log.completed and log.zoho_id:
            raise IncompleteLogException('Incomplete log entry. Cannot be submitted to Zoho.')

        client = AsyncHTTPClient()
        item   = urlencode(log.zoho_format)
        url    = '{base_url}/portal/{portal_id}/projects/{project_id}/logs/{log_id}?authtoken={token}&{item}'.format(
            base_url=LogHandler.BASE_URL,
            portal_id=log.user.portal_id,
            project_id=log.project_id,
            log_id=log.zoho_id,
            token=log.user.projects_token,
            item=item,
        )

        result = await client.fetch(url, method='POST', allow_nonstandard_methods=True)
        body = json.loads(result.body.decode('utf-8'))

        zoho_log = DotDict(body['timelogs']['generallogs'][0])
        return zoho_log.id

    @staticmethod
    async def delete_zoho_log(log):
        client = AsyncHTTPClient()
        url    = '{base_url}/portal/{portal_id}/projects/{project_id}/logs/{log_id}?authtoken={token}&{item}'.format(
            base_url=LogHandler.BASE_URL,
            portal_id=log.user.portal_id,
            project_id=log.project_id,
            log_id=log.zoho_id,
            token=log.user.projects_token,
        )
        result = await client.fetch(url, method='POST')
        assert result.code == 200
