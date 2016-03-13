from sqlalchemy.types import String, Integer
from sqlalchemy.schema import Column
from sqlalchemy.orm import relationship

from utilise.password_helper import PasswordHelper as PWH

from timesheet.model.base import Base


class User(Base):
    id           = Column(Integer, primary_key=True)
    username     = Column(String(255))
    password     = Column(String(255))
    token        = Column(String(255))
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

    def auth_password(self, password: str):
        success, updated_password = PWH.validate_password(self.password, password)
        if not success:
            raise ValueError('Incorrect password')

        self.password = updated_password

    def auth_token(self, token: str):
        success, updated_token = PWH.validate_password(self.token, token)
        if not success:
            raise ValueError('Incorrect token')

        self.token = updated_token

    def change_password(self, old_password: str, new_password: str):
        success, self.password = PWH.change_password(self.password, old_password, new_password)
        return success
