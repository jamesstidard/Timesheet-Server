from tornado.web import HTTPError

from timesheet.handlers.resources.base_handler import BaseHandler
from timesheet.utils.user_session import user_session

__author__ = 'James Stidard'


class ChangePasswordHandler(BaseHandler):

    @user_session
    def put(self, user, session):
        old_password, new_password = self.get_json_arguments(
            'old_password',
            'new_password'
        )

        try:
            user.change_password(old_password, new_password=new_password)
        except ValueError:
            raise HTTPError(400, 'Incorrect old password')
        else:
            self.write('Success')
