from timesheet.model.log import Log
from timesheet.integrations.zoho.utils import ZohoResource


class ZohoSupportLog(ZohoResource, Log):
    __tablename__   = None
    __mapper_args__ = {'polymorphic_identity': 'Zoho Support Ticket'}
