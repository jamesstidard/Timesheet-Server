from itertools import chain

from tornado.gen import multi
from fuzzywuzzy import fuzz

from timesheet.handlers.base_handler import BaseHandler
from timesheet.utils.user_session import async_user_session
from timesheet.dispatches.get_projects import get_projects

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
        def fuzzy_score(project):
            return fuzz.partial_ratio(query, project.name)

        projects = sorted(projects, key=fuzzy_score, reverse=True)
        projects = projects[:limit]

        self.write(projects)
