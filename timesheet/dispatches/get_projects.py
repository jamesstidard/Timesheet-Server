from functools import singledispatch


@singledispatch
def get_projects(integration):
    raise NotImplementedError()


from timesheet.integrations.zoho.projects.control import get_projects as get_projects_projects
from timesheet.integrations.zoho.support.control import get_projects as get_support_projects
