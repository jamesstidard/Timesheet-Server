from functools import singledispatch


@singledispatch
def insert_log(integration):
    raise NotImplementedError()


from timesheet.integrations.zoho_projects.dispatches.insert_log import insert_log as insert_projects_log
from timesheet.integrations.zoho_support.dispatches.insert_log import insert_log as insert_support_log
