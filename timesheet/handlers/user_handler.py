from timesheet.handlers.base_handler import BaseHandler
from timesheet.utils.user_session import user_session


class UserHandler(BaseHandler):

    @user_session
    def get(self, user, session):
        self.write(user.client_format)

    # @user_session
    # def put(self, user, session):
    #     for property_key in ['username', 'settings']:
    #         if property_key in self.json_arguments:
    #             current = user.__getattr__(property_key)
    #             value = self.get_json_argument(property_key, current)
    #             user.__setattr__(property_key, value)
    #
    #     session.flush()
    #     self.write(user.client_format)
