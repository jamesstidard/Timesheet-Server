import json

from sqlalchemy.types import String, Integer, Text
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.orm import relationship

from timesheet.model.base import Base
from timesheet.model.log import Log


class Integration(Base):
    id            = Column(Integer, primary_key=True)
    discriminator = Column('service', String(50))
    name          = Column(String(255))
    token         = Column(String(255))
    _maps         = Column('maps', Text)
    user_id       = Column(Integer, ForeignKey('user.id'))
    user          = relationship('User',
                                 uselist=False,
                                 primaryjoin='Integration.user_id==User.id',
                                 remote_side='User.id',
                                 back_populates='integrations')
    logs          = relationship('Log',
                                 uselist=True,
                                 primaryjoin='Integration.id==Log.integration_id',
                                 remote_side='Log.integration_id',
                                 back_populates='integration',
                                 cascade='all, delete-orphan')

    __mapper_args__ = {'polymorphic_on': discriminator}

    @classmethod
    def Log(cls, **kwargs):
        return Log(**kwargs)

    @property
    def maps(self):
        return json.loads(self._maps)

    @maps.setter
    def maps(self, value):
        self._maps = json.dumps(value)
