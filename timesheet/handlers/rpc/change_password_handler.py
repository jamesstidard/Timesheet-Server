from tornado.web import HTTPError

from timesheet.handlers.base_handler import BaseHandler
from timesheet.utils.user_session import user_session

__author__ = 'James Stidard'


class ChangePasswordHandler(BaseHandler):

    @user_session
    def put(self, user, session):
        old, new = self.get_json_arguments('old_password', 'new_password')

        try:
            user.change_password(old, new_password=new)
        except ValueError:
            raise HTTPError(400, 'Incorrect old password')
        else:
            self.write('Success')
