import uuid
import hmac
from hashlib import sha256

from sqlalchemy.types import String, DateTime
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import func

from utilise.password_helper import PasswordHelper as PWH

from timesheet.model.base import Base
from timesheet.model.custom_types.uuid import UUID


class Token(Base):
    id      = Column(UUID, primary_key=True, default=uuid.uuid4)
    name    = Column(String(255), nullable=False)
    _value  = Column('value', String(255), nullable=False)
    created = Column(DateTime, nullable=False, default=func.now())
    user_id = Column(UUID, ForeignKey('user.id'), nullable=False)
    user    = relationship('User',
                           uselist=False,
                           primaryjoin='Token.user_id==User.id',
                           remote_side='User.id',
                           back_populates='tokens')

    @staticmethod
    def create_secret():
        key  = uuid.uuid4().bytes
        return hmac.new(key, digestmod=sha256).hexdigest()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = PWH.create_password(value)

    def authenticate(self, token: str):
        success, updated_token = PWH.validate_password(self.value, token)
        if not success:
            raise ValueError('Incorrect token')

        self._value = updated_token
        return True
