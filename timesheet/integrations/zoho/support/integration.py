from sqlalchemy.schema import Column
from sqlalchemy.types import String

from timesheet.model.integration import Integration
from timesheet.integrations.zoho.support.log import ZohoSupportLog
from timesheet.integrations.zoho.utils import HasRegion, HasPortal


class ZohoSupportIntegration(HasRegion, HasPortal, Integration):
    __tablename__   = None
    __mapper_args__ = {'polymorphic_identity': 'Zoho Support'}

    department = Column(String(255))
    agent_name = Column(String(255))

    @classmethod
    def Log(cls, **kwargs):
        return ZohoSupportLog(**kwargs)
