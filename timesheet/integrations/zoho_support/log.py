from timesheet.model.log import Log
from timesheet.integrations.utils import ZohoResource


class ZohoSupportLog(ZohoResource, Log):
    __tablename__   = None
    __mapper_args__ = {'polymorphic_identity': 'Zoho Support Ticket'}

    @property
    def integration_format(self):
        delta   = self.end - self.start
        hours   = delta.seconds // 3600
        minutes = (delta.seconds // 60) % 60

        return \
            '<fl val="CASEID">{case_id}</fl>'\
            '<fl val="Executed Time">{start_time}</fl>'\
            '<fl val="Ticket Charge Type">Service and Maintenance</fl>'\
            '<fl val="TimeEntry Owner">{agent_name}</fl>'\
            '<fl val="Hours Spent">{hours}</fl>'\
            '<fl val="Minutes Spent">{minutes}</fl>'\
            '<fl val="Description">{notes}</fl>'.format(
                case_id=self.project_id,
                start_time=self.start.strftime('%m/%d/%Y %H:%M:%S'),
                agent_name=self.integration.agent_name,
                hours=hours,
                minutes=minutes,
                notes=self.notes
            )

        @property
        def completed(self):
            return all([
                self.project_id,
                self.task,
                self.start,
                self.end
            ])
