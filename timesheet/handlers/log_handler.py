import json

from timesheet.model.model import Log
from timesheet.utils.dot_dict import DotDict
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler

__author__ = 'James Stidard'


class LogHandler(RequestHandler):

    BASE_URL  = "https://projectsapi.zoho.com/restapi"
    PORTAL_ID = 20557707
    API_TOKEN = "c7a2105c8c9c8a23d27b0d839c6fbd76"

    @property
    def control(self):
        return self.application.settings.get('control')

    def prepare(self):
        self.request.body = json.loads(self.request.body.decode('utf-8'))

    async def post(self):
        with self.control.session as session:
            log = Log(
                project_id=self.get_argument('project_id'),
                task=self.get_argument('task'),
                start=self.get_argument('start'),
                end=self.get_argument('end', None),
                billable=self.get_argument('billable', True),
                notes=self.get_argument('notes', ''),
                session=session,
            )
            session.commit()

            if log.completed:
                client = AsyncHTTPClient()
                url    = '{base_url}/portal/{portal_id}/projects/{project_id}/logs/?authtoken={token}'.format(
                    base_url=self.BASE_URL,
                    portal_id=self.PORTAL_ID,
                    project_id=log.project_id,
                    token=self.API_TOKEN,
                )

                result = await client.fetch(url, method='POST', body=log.zoho_json)
                body   = json.loads(result.body.decode('utf-8'))

                zoho_log    = DotDict(body['timelogs'])
                log.zoho_id = zoho_log.id
                session.commit()

            self.write(log.json)
