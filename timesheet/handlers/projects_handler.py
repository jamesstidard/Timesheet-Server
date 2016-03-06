import json
from itertools import chain
from functools import singledispatch, partial

from tornado.gen import multi
from fuzzywuzzy import fuzz

from timesheet.handlers.base_handler import BaseHandler
from timesheet.utils.user_session import async_user_session
from timesheet.model import ZohoProjectsIntegration, ZohoSupportIntegration
from timesheet.integrations.zoho.projects.control import get_projects as get_projects_projects
from timesheet.integrations.zoho.support.control import get_projects as get_support_projects

__author__ = 'James Stidard'


class ProjectsHandler(BaseHandler):

    @async_user_session
    async def get(self, user, _):
        query = self.get_argument('query', default='')
        limit = self.get_argument('limit', default=None, cast=int)

        # Fetch projects from all user's integrations
        sources  = (get_projects(i) for i in user.integrations)
        results  = await multi(sources)
        projects = chain(*results)

        # Sort by fuzzy string match score on project name and limit
        fuzzy_score = partial(fuzz.ratio, query)
        projects    = sorted(projects, key=fuzzy_score, reverse=True)
        projects    = projects[:limit]

        self.write(projects)


@singledispatch
def get_projects(integration):
    raise NotImplementedError()


@get_projects.register(ZohoProjectsIntegration)
def _(integration):
    return get_projects_projects(integration)


@get_projects.register(ZohoSupportIntegration)
def _(integration):
    return get_support_projects(integration)
