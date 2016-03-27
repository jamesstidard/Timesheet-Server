from tornado.web import HTTPError

from timesheet.utils.str_list import str_list


class ArgumentsError(HTTPError):
    """
    Exception raised by `BaseHandler` argument getters.

    This is a subclass of `HTTPError`, so if it is uncaught a 400 response
    code will be used instead of 500 (and a stack trace will not be logged).
    """

    def __init__(self, *arg_names):
        arg_names  = list(arg_names)
        arg_list   = str_list(*arg_names, quote=True)
        message    = self.message(*arg_names)
        message    = '{}: {}'.format(message, arg_list)

        super(ArgumentsError, self).__init__(400, log_message=message, reason=message)
        self.arg_names = arg_names

    def message(self, *arguments):
        raise NotImplementedError()


class MissingArgumentsError(ArgumentsError):

    def message(self, *arguments):
        single_arg = len(arguments) == 1
        return 'Missing argument' if single_arg else 'Missing arguments'


class UnknownArgumentsError(ArgumentsError):

    def message(self, *arguments):
        single_arg = len(arguments) == 1
        return 'Unknown argument' if single_arg else 'Unknown arguments'
