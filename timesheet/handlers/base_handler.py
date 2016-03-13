import json
import urlparse

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

    def get_origin_whitelist(self):
        return self.control.settings.get('cors_origins')

    def get_request_origin(self):
        url = self.request.headers.get("Referer")
        if url:
            o = urlparse(url)
            origin = o.scheme + "://" + o.hostname
            if o.port:
                origin = "{}:{}".format(origin, o.port)
            if origin in self.cors_origin:
                return origin

    def write(self, chunk):
        super().write({
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

    def options(self, path=None):
        origin = self.get_request_origin()
        if origin in self.cors_origin:
            self.set_header("Access-Control-Allow-Origin", origin)
            self.set_header('Access-Control-Allow-Methods', 'POST,OPTIONS')
            self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Key, Cache-Control')
            self.set_header('Access-Control-Max-Age', 3000)
            self.set_status(204)
            self.finish()
        else:
            super().options()
