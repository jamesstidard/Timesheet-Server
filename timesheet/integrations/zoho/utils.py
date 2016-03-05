from sqlalchemy.schema import Column
from sqlalchemy.types import String
from sqlalchemy.ext.declarative.api import declared_attr


class HasPortal:
    @declared_attr
    def portal_id(cls):
        return cls.__table__.c.get('portal_id', Column(String(255)))


class HasRegion:
    @declared_attr
    def region(cls):
        return cls.__table__.c.get('region', Column(String(255)))


class ZohoResource(HasRegion):
    @declared_attr
    def zoho_id(cls):
        return cls.__table__.c.get('zoho_id', Column(String(255)))
