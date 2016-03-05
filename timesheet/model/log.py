from datetime import datetime

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Text, Integer, DateTime, BigInteger
from sqlalchemy.orm import relationship

from timesheet.model.base import Base
from timesheet.utils.date_helpers import parse_unix_time


class Log(Base):
    id            = Column(Integer, primary_key=True)
    discriminator = Column('type', String(50))
    project_id    = Column(BigInteger)
    task          = Column(String(255))
    _start        = Column('start', DateTime, default=datetime.utcnow)
    _end          = Column('end', DateTime)
    notes         = Column(Text)
    user_id       = Column(Integer, ForeignKey('user.id'))
    user          = relationship('User',
                                 uselist=False,
                                 primaryjoin='Log.user_id==User.id',
                                 remote_side='User.id',
                                 back_populates='logs')

    __mapper_args__ = {'polymorphic_on': discriminator}

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
        raise NotImplementedError()

    @property
    def integration_format(self):
        raise NotImplementedError()
