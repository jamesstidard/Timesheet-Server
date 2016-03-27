from timesheet.handlers.resource_handler import ResourceHandler
from timesheet.utils.user_session import user_session


class UserHandler(ResourceHandler):

    @user_session
    def get(self, user, session):
        self.write(user.client_format)

    @user_session
    def put(self, user, session):
        for property_key in ['username', 'settings']:
            if property_key in self.json_arguments:
                current = getattr(user, property_key)
                value   = self.get_json_argument(property_key, current)
                setattr(user, property_key, value)

        session.flush()
        self.write(user.client_format)
