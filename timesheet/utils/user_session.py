from functools import wraps

from timesheet.model.user import User

__author__ = 'James Stidard'


def user_session(f):
    @wraps(f)
    def call(self, *args, **kwargs):
        with self.control.session as session:
            id     = self.get_current_user()
            user   = session.query(User).get(id)
            result = f(self, user, session, *args, **kwargs)
        return result
    return call


def async_user_session(f):
    @wraps(f)
    async def call(self, *args, **kwargs):
        with self.control.session as session:
            id     = self.get_current_user()
            user   = session.query(User).get(id)
            result = await f(self, user, session, *args, **kwargs)
        return result
    return call
