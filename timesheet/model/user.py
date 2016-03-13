import uuid
import json

from sqlalchemy.types import String, Text
from sqlalchemy.schema import Column
from sqlalchemy.orm import relationship

from utilise.password_helper import PasswordHelper as PWH

from timesheet.model.base import Base
from timesheet.model.custom_types.uuid import UUID


class User(Base):
    id           = Column(UUID, primary_key=True, default=uuid.uuid4)
    username     = Column(String(255), nullable=False, unique=True)
    _password    = Column('password', String(255), nullable=False)
    settings     = Column(Text, nullable=False, default="{}")
    tokens       = relationship('Token',
                                uselist=True,
                                primaryjoin='User.id==Token.user_id',
                                remote_side='Token.user_id',
                                back_populates='user',
                                cascade='all, delete-orphan')
    integrations = relationship('Integration',
                                uselist=True,
                                primaryjoin='User.id==Integration.user_id',
                                remote_side='Integration.user_id',
                                back_populates='user',
                                cascade='all, delete-orphan')
    logs         = relationship('Log',
                                uselist=True,
                                primaryjoin='User.id==Log.user_id',
                                remote_side='Log.user_id',
                                back_populates='user',
                                cascade='all, delete-orphan')

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = PWH.create_password(password)

    def authenticate(self, password: str=None):
        success, updated_password = PWH.validate_password(self.password, password)
        if not success:
            raise ValueError('Incorrect password')

        self._password = updated_password
        return success

    def change_password(self, password: str, *, new_password: str):
        success, self._password = PWH.change_password(self.password, password, new_password)
        if not success:
            raise ValueError('Incorrect password')
        return success

    @property
    def client_format(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'settings': json.loads(self.settings)
        }
