

def unwrap_projects(result, mapping):
    cases = result['response']['result']['Cases']['row']
    return [{mapping[kv['val']]: kv['content'] for kv in c['fl'] if kv['val'] in mapping} for c in cases]


def wrap_logs(*logs):
    rows = ['<row no="{}">{}</row>'.format(index + 1, log.integration_format)
            for index, log in enumerate(logs)]
    return '<timeentry>{}</timeentry>'.format(rows)
