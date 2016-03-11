from functools import singledispatch


@singledispatch
def get_projects(integration):
    raise NotImplementedError()


from timesheet.integrations.zoho_projects.dispatches.get_projects import get_projects as get_projects_projects
from timesheet.integrations.zoho_support.dispatches.get_projects import get_projects as get_support_projects
