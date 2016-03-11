from functools import singledispatch

__author__ = 'James Stidard'


@singledispatch
def delete_log(integration):
    raise NotImplementedError()


from timesheet.integrations.zoho_projects.dispatches.delete_log import delete_log as delete_projects_log
from timesheet.integrations.zoho_support.dispatches.delete_log import delete_log as delete_support_log
