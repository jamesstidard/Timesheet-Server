from contextlib import contextmanager

from blueshed.model_helpers.base_control import BaseControl

from timesheet.utils.orm_utils import connect


class Control(BaseControl):
    """
    Public Interface Definition and Implementation.

    Encapsulates a database connection and provides a session interface
    can generate passwords, contains a list of websocket clients and
    will broadcast state changes to interested client.
    """

    def __init__(self, db_url: str, echo: bool=False, pool_recycle=None):
        """
        Initialiser.

        :param db_url: requires a sqlalchemy db_url
        """
        BaseControl.__init__(self, db_url, echo, pool_recycle)

        self._engine, self._Session = connect(db_url, echo, pool_recycle)
        self._clients = []
        self._pending = []

    def _flush(self, error=None):
        """Called by clients after completing work."""
        if not error:
            for args in self._pending:
                self._broadcast(*args)
        self._pending = []

    @property
    @contextmanager
    def session(self):
        """Self closing session for use by with statements."""
        session = self._Session()

        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def ping(self, client):
        """Keep-alive Endpoint."""
        return "pong"
