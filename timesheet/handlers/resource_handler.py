from timesheet.handlers.base_handler import BaseHandler
from timesheet.utils.http_exceptions import UnknownArgumentsError


class ResourceHandler(BaseHandler):

    def _update_resource(self, resource, *allowed):
        unknown = [k for k in self.json_arguments if k not in allowed]
        if unknown:
            raise UnknownArgumentsError(*unknown)

        for property_key in allowed:
            if property_key in self.json_arguments:
                value = self.get_json_argument(property_key)
                setattr(resource, property_key, value)
