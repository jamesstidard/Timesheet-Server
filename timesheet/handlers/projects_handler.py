import json

from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler

from timesheet.utils.dot_dict import DotDict

__author__ = 'James Stidard'


class ProjectsHandler(RequestHandler):
    BASE_URL  = "https://projectsapi.zoho.com/restapi"
    PORTAL_ID = 20557707
    API_TOKEN = "c7a2105c8c9c8a23d27b0d839c6fbd76"

    async def get(self):
        query  = self.get_argument('query', '')
        client = AsyncHTTPClient()
        url    = '{}/portal/{}/projects/?authtoken={}'.format(self.BASE_URL, self.PORTAL_ID, self.API_TOKEN)
        result = await client.fetch(url)

        body     = json.loads(result.body.decode('utf-8'))
        projects = [DotDict(p) for p in body['projects']]
        projects = [{
              'id': p.id,
            'name': p.name,
        } for p in projects if query.lower() in p.name.lower()]

        result = json.dumps(projects)
        self.write(result)
