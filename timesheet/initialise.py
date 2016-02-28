import os
import logging
from dotenv import load_dotenv

from tornado.options import parse_command_line, define
from utilise.password_helper import PasswordHelper as PWH

from timesheet.control import Control
from timesheet.utils.orm_utils import drop_all, create_all, heroku_db_url
from timesheet.model.model import Base
from timesheet.model.model import User

__author__ = 'James Stidard'


define("db_url", help="database url")


def main():
    if os.path.isfile('.env'):
        load_dotenv('.env')
    parse_command_line()

    db_url  = heroku_db_url(os.environ.get("CLEARDB_DATABASE_URL"))
    logging.info("db: %s", db_url)

    control = Control(db_url)
    with control.session as session:
        drop_all(session)
        session.commit()

    create_all(Base, control._engine)

    for u in [{  "email": "james@stidard.com",
              "password": PWH.create_password("password"),
             "portal_id": 20557707,
        "projects_token": "c7a2105c8c9c8a23d27b0d839c6fbd76"}]:
        user = User(**u)
        session.add(user)

    session.commit()


if __name__ == "__main__":
    main()
