from tornado.web import HTTPError
from sqlalchemy.orm.exc import NoResultFound

from timesheet.handlers.base_handler import BaseHandler
from timesheet.model.user import User
from timesheet.utils.user_session import user_session

__author__ = 'James Stidard'


class SignInHandler(BaseHandler):

    def post(self):
        username, password = self.get_json_arguments('username', 'password')

        with self.control.session as session:
            try:
                user = session.query(User)\
                              .filter(User.username == username).one()
                user.authenticate(password)
                session.commit()
            except (NoResultFound, ValueError):
                raise HTTPError(400, reason='Incorrect username or password')
            else:
                self.set_secure_cookie('user_id', str(user.id))
                self.write(user.client_format)

    @user_session
    def delete(self, session, user):
        self.clear_cookie('user_id')
