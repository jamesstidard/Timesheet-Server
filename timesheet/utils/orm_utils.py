'''
Created on 3 Mar 2015

@author: peterb
'''
from sqlalchemy.engine import reflection, create_engine
from sqlalchemy.sql.schema import MetaData, ForeignKeyConstraint, Table
from sqlalchemy.sql.ddl import DropConstraint, DropTable
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.types import UserDefinedType


_SESSION_EXTENSIONS_ = []
_SESSION_KWARGS_ = {"autoflush": False}
_pool_recycle_ = 3600


def connect(db_url, echo=False, pool_recycle=None):

    params = dict(echo=echo)
    if 'mysql' in db_url:
        params['encoding'] = 'utf-8'
        params['pool_recycle'] = pool_recycle if pool_recycle else _pool_recycle_
        params['isolation_level'] = 'READ COMMITTED'

    engine = create_engine(db_url, **params)
    Session = sessionmaker(bind=engine,
                           extension=_SESSION_EXTENSIONS_,
                           **_SESSION_KWARGS_)

    return engine, Session


def create_all(Base, engine):
    Base.metadata.create_all(engine)


def drop_all(session):

    inspector = reflection.Inspector.from_engine(session.bind)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.

    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(
                ForeignKeyConstraint((), (), name=fk['name'])
            )
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        session.execute(DropConstraint(fkc))

    for table in tbs:
        session.execute(DropTable(table))

    session.commit()


def heroku_db_url(db_url):
    if db_url.startswith("mysql://"):
        db_url = "mysql+pymysql://" + db_url[len("mysql://"):]
        if db_url.endswith("?reconnect=true"):
            db_url = db_url[:-len("?reconnect=true")]
    return db_url
