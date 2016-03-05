from timesheet.model.integration import Integration
from timesheet.integrations.zoho.utils import HasRegion, HasPortal


class ZohoProjectsIntegration(HasRegion, HasPortal, Integration):
    __tablename__   = None
    __mapper_args__ = {'polymorphic_identity': 'Zoho Projects'}
