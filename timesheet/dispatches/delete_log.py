from functools import singledispatch


@singledispatch
def delete_log(integration):
    raise NotImplementedError()


from timesheet.integrations.zoho.projects.control import delete_log as delete_projects_log
from timesheet.integrations.zoho.support.control import delete_log as delete_support_log
