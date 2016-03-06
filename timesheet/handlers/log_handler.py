from timesheet.model.log import ZohoProjectsLog
from timesheet.handlers.base_handler import BaseHandler
from timesheet.utils.user_session import async_user_session
from timesheet.utils.log_exceptions import IncompleteLogException
from timesheet.zoho.projects import insert_project_log, update_project_log, delete_project_log
from timesheet.zoho.support import insert_ticket_log, update_ticket_log, delete_ticket_log

__author__ = 'James Stidard'


class LogHandler(BaseHandler):

    @async_user_session
    async def get(self, user, session):
        logs = session.query(ZohoProjectsLog).filter(ZohoProjectsLog.user_id == user.id).all()
        self.write([l.client_format for l in logs], format='json')

    @async_user_session
    async def post(self, user, session):
        log = ZohoProjectsLog(
            project_id=self.get_json_argument('project_id'),
            task=self.get_json_argument('task'),
            start=self.get_json_argument('start', None),
            end=self.get_json_argument('end', None),
            billable=self.get_json_argument('billable', True),
            notes=self.get_json_argument('notes', ''),
            user=user,
            session=session,
        )
        session.commit()

        try:
            log.zoho_id = await insert_project_log(log)
        except IncompleteLogException:
            pass
        else:
            session.commit()
            self.write(log.integration_format)

    @async_user_session
    async def put(self, user, session):
        id  = self.get_json_argument('id')
        log = session.query(ZohoProjectsLog).filter(ZohoProjectsLog.user_id == user.id).get(id)

        for property_key in ['project_id', 'task', 'start', 'end', 'billable', 'notes']:
            if property_key in self.json_arguments:
                value = self.get_json_argument(property_key)
                log.__setattr__(property_key, value)

        if not log.zoho_id:
            try:
                log.id = await insert_project_log(log)
            except IncompleteLogException:
                pass
        else:
            try:
                log.id = await update_project_log(log)
            except IncompleteLogException:
                await delete_project_log(log)
                pass

        session.commit()
        self.write(log.client_format)

    @async_user_session
    async def delete(self, user, session):
        id  = self.get_argument('id')
        log = session.query(ZohoProjectsLog).filter(ZohoProjectsLog.user_id == user.id).get(id)

        if log.zoho_id:
            await delete_project_log(log)

        session.delete(log)
        session.commit()

        self.write('Success')
