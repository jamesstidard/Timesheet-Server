import json
from urllib.parse import urlencode

from timesheet.model.model import Log
from timesheet.utils.dot_dict import DotDict
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler, MissingArgumentError

__author__ = 'James Stidard'


class IncompleteLogException(ValueError):
    pass


class LogHandler(RequestHandler):

    BASE_URL  = "https://projectsapi.zoho.com/restapi"
    PORTAL_ID = 20557707
    API_TOKEN = "c7a2105c8c9c8a23d27b0d839c6fbd76"

    @property
    def control(self):
        return self.application.settings.get('control')

    def prepare(self):
        if self.request.headers.get( "Content-Type" ) == "application/json":
            self.json_arguments = json.loads(self.request.body.decode('utf-8'))

    _ARG_DEFAULT = []

    def get_json_argument(self, name: str, default=_ARG_DEFAULT):
        try:
            return self.json_arguments[name]
        except KeyError:
            if default is self._ARG_DEFAULT:
                raise MissingArgumentError(name)
            else:
                return default

    async def post(self):
        with self.control.session as session:
            log = Log(
                project_id=self.get_json_argument('project_id'),
                task=self.get_json_argument('task'),
                start=self.get_json_argument('start'),
                end=self.get_json_argument('end', None),
                billable=self.get_json_argument('billable', True),
                notes=self.get_json_argument('notes', ''),
                session=session,
            )
            session.commit()

            try:
                log.zoho_id = await self.insert_zoho_log(log)
            except IncompleteLogException:
                pass
            else:
                session.commit()
                self.write(log.json)

    async def insert_zoho_log(self, log):
        if not log.completed:
            raise IncompleteLogException('Incomplete log entry. Cannot be submitted to Zoho.')

        client = AsyncHTTPClient()
        item   = urlencode(log.zoho_format)
        url    = '{base_url}/portal/{portal_id}/projects/{project_id}/logs/?authtoken={token}&{item}'.format(
            base_url=self.BASE_URL,
            portal_id=self.PORTAL_ID,
            project_id=log.project_id,
            token=self.API_TOKEN,
            item=item
        )

        result = await client.fetch( url, method='POST', allow_nonstandard_methods=True )
        body = json.loads(result.body.decode('utf-8'))

        zoho_log = DotDict(body['timelogs']['generallogs'][0])
        return zoho_log.id

    async def update_zoho_log(self, log):
        if not log.completed and log.zoho_id:
            raise IncompleteLogException('Incomplete log entry. Cannot be submitted to Zoho.')

        client = AsyncHTTPClient()
        item   = urlencode(log.zoho_format)
        url    = '{base_url}/portal/{portal_id}/projects/{project_id}/logs/{log_id}?authtoken={token}&{item}'.format(
            base_url=self.BASE_URL,
            portal_id=self.PORTAL_ID,
            project_id=log.project_id,
            log_id=log.zoho_id,
            token=self.API_TOKEN,
            item=item,
        )

        result = await client.fetch(url, method='POST', allow_nonstandard_methods=True)
        body   = json.loads(result.body.decode('utf-8'))

        zoho_log = DotDict(body['timelogs']['generallogs'][0])
        return zoho_log.id

    async def delete_zoho_log(self, log):
        client = AsyncHTTPClient()
        url    = '{base_url}/portal/{portal_id}/projects/{project_id}/logs/{log_id}?authtoken={token}&{item}'.format(
            base_url=self.BASE_URL,
            portal_id=self.PORTAL_ID,
            project_id=log.project_id,
            log_id=log.zoho_id,
            token=self.API_TOKEN,
        )
        result = await client.fetch(url, method='POST', allow_nonstandard_methods=True)
        assert result.code == 200

    async def put(self):
        with self.control.session as session:
            id  = self.get_json_argument('id')
            log = session.query(Log).get(id)

            for property_key in ['project_id', 'task', 'start', 'end', 'billable', 'notes']:
                if property_key in self.json_arguments:
                    value = self.get_json_argument(property_key)
                    log.__setattr__(property_key, value)

            if log.zoho_id:
                try:
                    log.id = await self.update_zoho_log(log)
                except IncompleteLogException:
                    self.delete_zoho_log(log)
                    pass
            else:
                try:
                    log.id = await self.insert_zoho_log(log)
                except IncompleteLogException:
                    pass

            session.commit()
            self.write(log.json)

    async def delete(self):
        with self.control.session as session:
            id  = self.get_json_argument('id')
            log = session.query(Log).get(id)

            if log.zoho_id:
                self.delete_zoho_log(log.zoho_id)

            session.delete(log)
            session.commit()

            self.write("Success")
