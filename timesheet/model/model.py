import re
import json
from numbers import Integral
from datetime import datetime

from sqlalchemy.types import String, Text, Integer, Boolean, DateTime, BigInteger
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative.api import declared_attr, has_inherited_table, declarative_base
from utilise.password_helper import PasswordHelper as PWH

from timesheet.utils.date_helpers import to_unix_time, parse_unix_time


class _Base_(object):
    """
    This class allows us to base the tablename off the class name.

    We also check for has_inherited_table, so as not to redeclare.
    We make the table name to lower case and underscored.

    We don't implement the primary key in base as some classes will use
    a foreign key to a parent table as their primary key.

    see: http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/declarative.html#augmenting-the-base
    """

    @declared_attr
    def __tablename__(self):
        if has_inherited_table(self):
            return None
        name = self.__name__
        return (
            name[0].lower() +
            re.sub(r'([A-Z])', lambda m: "_" + m.group(0).lower(), name[1:])
        )

    __table_args__ = {'mysql_engine': 'InnoDB'}


Base = declarative_base(cls=_Base_)


class User(Base):
    id             = Column(Integer, primary_key=True)
    username       = Column(String(255))
    password       = Column(String(255))
    token          = Column(String(255))
    portal_id      = Column(BigInteger)
    projects_token = Column(String(255))
    logs           = relationship('Log',
                                  uselist=True,
                                  primaryjoin='User.id==Log.user_id',
                                  remote_side='Log.user_id',
                                  back_populates='user',
                                  cascade='all, delete-orphan')

    def auth_password(self, password: str):
        success, updated_password = PWH.validate_password(self.password, password)
        if not success:
            raise ValueError('Incorrect password')

        self.password = updated_password

    def auth_token(self, token: str):
        success, updated_token = PWH.validate_token(self.token, token)
        if not success:
            raise ValueError('Incorrect token')

        self.token = updated_token

    def change_password(self, old_password: str, new_password: str):
        success, self.password = PWH.change_password(self.password, old_password, new_password)
        return success


class Log(Base):
    id         = Column(Integer, primary_key=True)
    zoho_id    = Column(BigInteger)
    project_id = Column(BigInteger)
    task       = Column(String(255))
    _start     = Column('start', DateTime, default=datetime.utcnow)
    _end       = Column('end', DateTime)
    billable   = Column(Boolean, default=True)
    notes      = Column(Text)
    user_id    = Column(Integer, ForeignKey('user.id'))
    user       = relationship('User',
                              uselist=False,
                              primaryjoin='Log.user_id==User.id',
                              remote_side='User.id',
                              back_populates='logs')

    def __init__(self, session=None, **kwargs):
        [self.__setattr__(k, v) for k, v in kwargs.items()]

        if session:
            session.add(self)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        try:
            self._start = parse_unix_time(value)
        except ValueError:
            self._start = value
            pass

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        try:
            self._end = parse_unix_time(value)
        except ValueError:
            self._end = value
            pass

    @property
    def completed(self):
        return self.project_id and self.task and self.start and self.end and self.billable

    @property
    def client_format(self):
        return {
                    'id': self.id,
            'project_id': self.project_id,
                  'task': self.task,
                 'start': to_unix_time(self.start),
                   'end': to_unix_time(self.end),
              'billable': self.billable,
                 'notes': self.notes,
        }

    @property
    def zoho_format(self):
        delta   = self.end - self.start
        hours   = delta.seconds // 3600
        minutes = (delta.seconds // 60) % 60

        return {
                   'name': self.task,
                   'date': self.start.strftime('%m-%d-%Y'),
            'bill_status': 'Billable' if self.billable else 'Non Billable',
                  'hours': '{hours:02d}:{minutes:02d}'.format(hours=hours, minutes=minutes),
                  'notes': self.notes
        }
