from tornado.web import HTTPError

from utilise.password_helper import PasswordHelper as PWH

from timesheet.handlers.resources.base_handler import BaseHandler
from timesheet.model.user import User
from timesheet.model.token import Token

__author__ = 'James Stidard'


class TokenHandler(BaseHandler):

    def put(self):
        username = self.get_json_argument('username')
        password = self.get_json_argument('password')
        name     = self.get_json_argument('name')

        with self.control.session as session:
            try:
                user = session.query(User)\
                              .filter(User.username == username).one()
                user.authenticate(password)
                session.commit()
            except ValueError:
                raise HTTPError(400, reason='Incorrect username or password.')
            else:
                secret = Token.create_secret()
                token  = Token(
                    name=name,
                    value=PWH.create_password(secret),
                    user=user
                )
                session.add(token)
                session.commit()

                self.write({
                    "token_id": token.id,
                    "token_secret": secret
                })
