import json

from tornado.web import RequestHandler, MissingArgumentError

from timesheet.model.token import Token

__author__ = 'James Stidard'


class BaseHandler(RequestHandler):

    @property
    def control(self):
        return self.application.settings.get('control')

    def get_current_user(self):
        try:
            return self.get_secure_cookie("user_id")
        except TypeError:
            try:
                token_id     = self.request.headers.get('token-id')
                token_secret = self.request.headers.get('token-secret')
                with self.control.session as session:
                    token = session.query(Token)\
                                   .filter(Token.id == token_id)\
                                   .one()
                    token.authenticate(token_secret)
                    session.commit()
                    return token.user_id
            except ValueError:
                raise MissingArgumentError('Not already logged in or incorrect\
                                            auth id and token provided.')

    def write(self, chunk):
        super(RequestHandler, self).write({
            'result': chunk
        })

    def prepare(self):
        content_type = self.request.headers.get('Content-Type')

        if content_type == 'application/json' and self.request.body != b'':
            self.json_arguments = json.loads(self.request.body.decode('utf-8'))

    def get_json_argument(self,
                          name: str,
                          default=RequestHandler._ARG_DEFAULT):
        try:
            return self.json_arguments[name]
        except KeyError:
            if default is RequestHandler._ARG_DEFAULT:
                raise MissingArgumentError(name)
            else:
                return default

    def get_argument(self,
                     name: str,
                     default=RequestHandler._ARG_DEFAULT,
                     strip: bool=True,
                     cast: type=None):
        try:
            value = super().get_argument(name, strip=True)
            return cast(value) if cast else value
        except MissingArgumentError:
            if default is RequestHandler._ARG_DEFAULT:
                raise MissingArgumentError(name)
            else:
                return default
