import json

from tornado.web import RequestHandler, MissingArgumentError

__author__ = 'James Stidard'


class BaseHandler(RequestHandler):

    @property
    def control(self):
        return self.application.settings.get('control')

    def write(self, chunk, format=None):
        if format.lower() == 'json':
            chunk = json.dumps(chunk)
        super().write(chunk)

    def prepare(self):
        if self.request.headers.get("Content-Type") == "application/json" and self.request.body != b'':
            self.json_arguments = json.loads( self.request.body.decode('utf-8' ))

    _ARG_DEFAULT = []

    def get_json_argument(self, name: str, default=_ARG_DEFAULT):
        try:
            return self.json_arguments[name]
        except KeyError:
            if default is self._ARG_DEFAULT:
                raise MissingArgumentError(name)
            else:
                return default
