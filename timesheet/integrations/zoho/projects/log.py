from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean

from timesheet.model.log import Log


class ZohoProjectsLog(Log):
    __tablename__   = None
    __mapper_args__ = {'polymorphic_identity': 'Zoho Project Log'}

    billable      = Column(Boolean, default=True)

    @property
    def integration_format(self):
        delta   = self.end - self.start
        hours   = delta.seconds // 3600
        minutes = (delta.seconds // 60) % 60

        return {
                   'name': self.task,
                   'date': self.start.strftime('%m-%d-%Y'),
            'bill_status': 'Billable' if self.billable else 'Non Billable',
                  'hours': '{hours:02d}:{minutes:02d}'.format(hours=hours, minutes=minutes),
                  'notes': self.notes
        }

    @property
    def completed(self):
        return self.project_id and self.task and self.start and self.end and self.billable
