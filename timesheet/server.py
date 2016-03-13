import os
import logging
from dotenv import load_dotenv

from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define, options
from tornado.web import Application

from timesheet.control import Control
from timesheet.handlers.login_handler import LoginHandler
from timesheet.handlers.user_handler import UserHandler
from timesheet.handlers.token_handler import TokenHandler
from timesheet.handlers.projects_handler import ProjectsHandler
from timesheet.handlers.log_handler import LogHandler
from timesheet.utils.orm_utils import heroku_db_url

DEBUG_COOKIE = 'timesheet-secret-please-dont-guess'

define('cookie_secret', DEBUG_COOKIE, str, help='key used to sign cookies')
define('debug', False, bool, help='run in debug mode')
define('port', 8888, int, help='port to listen on')
define('db_url', help='database url')
define('cors_origins', '', str, help='comma sepertated list of cor origins')


def main():
    if os.path.isfile('.env'):
        load_dotenv('.env')

    parse_command_line()

    secret  = os.environ.get('COOKIE_SECRET', options.cookie_secret)
    debug   = os.environ.get('DEBUG', options.debug)
    port    = os.environ.get('PORT', options.port)
    db_url  = os.environ.get('CLEARDB_DATABASE_URL', options.db_url)
    db_url  = heroku_db_url(db_url)

    origins = os.environ.get('CORS_ORIGINS', options.cors_origins)
    origins = [o.strip() for o in origins.split(',')]

    if not debug and secret == DEBUG_COOKIE:
        raise ValueError('Trying to use debug cookie for production.')

    handlers = [
        (r'/v1/rpc/login/?', LoginHandler),
        (r'/v1/resources/users/?', UserHandler),
        (r'/v1/resources/tokens/?', TokenHandler),
        (r'/v1/resources/projects/?', ProjectsHandler),
        (r'/v1/resources/logs/?', LogHandler),
    ]
    settings = {
              'control': Control(db_url, pool_recycle=60),
        'cookie_secret': secret,
          'cookie_name': 'timesheet',
         'cors_origins': origins,
                'debug': debug
    }
    application = Application(handlers, **settings)

    application.listen(int(port))
    logging.info('listening on port %s', port)
    if debug:
        logging.info('running in debug mode')
    IOLoop.current().start()


if __name__ == '__main__':
    main()
