from functools import singledispatch


@singledispatch
def update_log(integration):
    raise NotImplementedError()


from timesheet.integrations.zoho.projects.control import update_log as update_projects_log
from timesheet.integrations.zoho.support.control import update_log as update_support_log
