import json
import pytest

from timesheet.integrations.zoho.support.control import _unwrap_projects

def test_success_projects_response_unwrap():
    with open('tests/integrations/zoho/support/data/get_projects_success.json', 'r') as data_file:
        data   = json.load(data_file)
        result = _unwrap_projects(data, {
               'CASEID': 'id',
            'Ticket Id': 'ticket_id',
              'Subject': 'name'
        })
