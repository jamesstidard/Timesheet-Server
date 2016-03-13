from datetime import datetime

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Text, Integer, DateTime, BigInteger
from sqlalchemy.orm import relationship

from timesheet.model.base import Base
from timesheet.model.custom_types.uuid import UUID
from timesheet.utils.date_helpers import parse_unix_time, to_unix_time


class Log(Base):
    id             = Column(Integer, primary_key=True)
    discriminator  = Column('type', String(50), nullable=False)
    project_id     = Column(BigInteger)
    task           = Column(String(255))
    _start         = Column('start', DateTime, default=datetime.utcnow)
    _end           = Column('end', DateTime)
    notes          = Column(Text)
    integration_id = Column(Integer, ForeignKey('integration.id'), nullable=False)
    integration    = relationship('Integration',
                                  uselist=False,
                                  primaryjoin='Log.integration_id==Integration.id',
                                  remote_side='Integration.id',
                                  back_populates='logs')
    user_id        = Column(UUID, ForeignKey('user.id'), nullable=False)
    user           = relationship('User',
                                  uselist=False,
                                  primaryjoin='Log.user_id==User.id',
                                  remote_side='User.id',
                                  back_populates='logs')

    __mapper_args__ = {'polymorphic_on': discriminator}

    @property
    def client_format(self):
        start = to_unix_time(self._start) if self._start else None
        end   = to_unix_time(self._end) if self._end else None

        return {
            'id': self.id,
            'type': self.discriminator,
            'project_id': self.project_id,
            'task': self.task,
            'start': start,
            'end': end,
            'notes': self.notes
        }

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        try:
            self._start = parse_unix_time(value)
        except TypeError:
            self._start = value
            pass

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        try:
            self._end = parse_unix_time(value)
        except TypeError:
            self._end = value
            pass

    @property
    def completed(self):
        raise NotImplementedError()

    @property
    def integration_format(self):
        raise NotImplementedError()
