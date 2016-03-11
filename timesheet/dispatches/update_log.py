from functools import singledispatch


@singledispatch
def update_log(integration):
    raise NotImplementedError()


from timesheet.integrations.zoho_projects.dispatches.update_log import update_log as update_projects_log
from timesheet.integrations.zoho_support.dispatches.update_log import update_log as update_support_log
