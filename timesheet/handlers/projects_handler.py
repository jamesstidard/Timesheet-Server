import json
from itertools import chain
from functools import singledispatch

from tornado.gen import multi

from timesheet.handlers.base_handler import BaseHandler
from timesheet.utils.user_session import async_user_session
from timesheet.model import ZohoProjectsIntegration, ZohoSupportIntegration
from timesheet.integrations.zoho.projects.control import get_projects as get_projects_projects
from timesheet.integrations.zoho.support.control import get_projects as get_support_projects

__author__ = 'James Stidard'


class ProjectsHandler(BaseHandler):

    BASE_URL  = "https://projectsapi.zoho.com/restapi"

    @async_user_session
    async def get(self, session, user):
        query   = self.get_argument('query', '')
        sources = [get_projects(i) for i in user.integrations]
        results = await multi(sources)

        projects = [{
              'id': p.id,  # TODO: concat id with with support or projects prefix
            'name': p.name,
        } for p in chain(*results) if query.lower() in p.name.lower()]

        result = json.dumps(projects)
        self.write(result)


@singledispatch
def get_projects(integration):
    raise NotImplementedError()


@get_projects.register(ZohoProjectsIntegration)
def _(integration):
    return get_projects_projects(integration)


@get_projects.register(ZohoSupportIntegration)
def _(integration):
    return get_support_projects(integration)
