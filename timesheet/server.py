import os
import logging
from dotenv import load_dotenv

from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define, options
from tornado.web import Application

from timesheet.control import Control
from timesheet.handlers.projects_handler import ProjectsHandler
from timesheet.handlers.log_handler import LogHandler
from timesheet.utils.orm_utils import heroku_db_url

define("debug", False, bool, help="run in debug mode")
define("port", 8888, int, help="port to listen on")
define("db_url", help="database url")


def main():
    if os.path.isfile('.env'):
        load_dotenv('.env')

    parse_command_line()

    debug  = os.environ.get("DEBUG", options.debug)
    port   = int(os.environ.get("PORT", options.port))
    db_url = os.environ.get("CLEARDB_DATABASE_URL", options.db_url)
    db_url = heroku_db_url(db_url)

    handlers = [
        (r"/v1/resources/projects/?", ProjectsHandler),
        (r"/v1/resources/logs/?", LogHandler),
    ]
    settings = {
              "control": Control(db_url, pool_recycle=60),
        "cookie_secret": 'timesheet-secret-please-dont-guess',
          "cookie_name": 'timesheet',
                "debug": debug
    }
    application = Application(handlers, **settings)

    application.listen(port)
    logging.info("db: %s", db_url)
    logging.info("listening on port %s", port)
    if debug:
        logging.info("running in debug mode")
    IOLoop.current().start()


if __name__ == "__main__":
    main()
