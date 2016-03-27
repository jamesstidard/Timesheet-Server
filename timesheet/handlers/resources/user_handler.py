from timesheet.handlers.resource_handler import ResourceHandler
from timesheet.utils.user_session import user_session


class UserHandler(ResourceHandler):

    @user_session
    def get(self, user, session):
        self.write(user.client_format)

    @user_session
    def put(self, user, session):
        self._update_resource(user, 'username', 'settings')
        self.write(user.client_format)
