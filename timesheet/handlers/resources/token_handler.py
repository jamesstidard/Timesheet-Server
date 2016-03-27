from tornado.web import HTTPError

from utilise.password_helper import PasswordHelper as PWH

from timesheet.handlers.base_handler import BaseHandler
from timesheet.model.user import User
from timesheet.model.token import Token

__author__ = 'James Stidard'


class TokenHandler(BaseHandler):

    def put(self):
        try:
            user_id = self.get_current_user()
        except ValueError:
            kwargs = self.get_json_arguments('username', 'password', 'name')
        else:
            kwargs = self.get_json_arguments('name')

        with self.control.session as session:
            if user_id:
                user = session.query(User).get(user_id)
            else:
                try:
                    user = session.query(User)\
                                  .filter(User.username == kwargs.username)\
                                  .one()
                    user.authenticate(kwargs.password)
                    session.commit()
                except ValueError:
                    raise HTTPError(400, reason='Incorrect username of password')

            secret = Token.create_secret()
            token  = Token(
                name=kwargs.name,
                value=PWH.create_password(secret),
                user=user
            )
            session.add(token)
            session.commit()

            self.write({
                "token_id": token.id,
                "token_secret": secret
            })
