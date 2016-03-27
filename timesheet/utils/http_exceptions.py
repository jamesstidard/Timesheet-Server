from tornado.web import HTTPError

from timesheet.utils.str_list import str_list


class MissingArgumentsError(HTTPError):
    """
    Exception raised by `BaseHandler` argument getters.

    This is a subclass of `HTTPError`, so if it is uncaught a 400 response
    code will be used instead of 500 (and a stack trace will not be logged).
    """

    def __init__(self, *arg_names):
        arg_names  = list(arg_names)
        arg_list   = str_list(*arg_names, quote=True)
        single_arg = len(arg_names) == 1
        message    = 'Missing argument' if single_arg else 'Missing arguments'
        message    = '{}: {}'.format(message, arg_list)

        super(MissingArgumentsError, self).__init__(400, log_message=message, reason=message)
        self.arg_names = arg_names
