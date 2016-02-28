import json

from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler

from timesheet.handlers.base_handler import BaseHandler
from timesheet.utils.dot_dict import DotDict
from timesheet.utils.user_session import user_session

__author__ = 'James Stidard'


class ProjectsHandler(BaseHandler):

    BASE_URL  = "https://projectsapi.zoho.com/restapi"

    @user_session
    async def get(self, session, user):
        query  = self.get_argument('query', '')
        client = AsyncHTTPClient()
        result = await client.fetch('{base_url}/portal/portal_id{}/projects/?authtoken={token}'.format(
            base_url=self.BASE_URL,
            portal_id=user.portal_id,
            token=user.projects_token)
        )

        body     = json.loads(result.body.decode('utf-8'))
        projects = [DotDict(p) for p in body['projects']]
        projects = [{
              'id': p.id,
            'name': p.name,
        } for p in projects if query.lower() in p.name.lower()]

        result = json.dumps(projects)
        self.write(result)
