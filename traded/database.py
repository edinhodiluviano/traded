import os

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.environ["DATABASE_URL"]


engine = sa.create_engine(DATABASE_URL)
SessionLocal = sa.orm.sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base = sa.ext.declarative.declarative_base()


def setup(session: sa.orm.Session):
    "Create tables and insert basic entries"
    create_tables()
    populate(session)


def create_tables():
    "Create tables"
    Base.metadata.create_all(bind=engine)


def populate(session: sa.orm.Session):
    "Insert basic entries"
    _create_default_coa(session)


def clear(session: sa.orm.Session):
    "Just delete entries for all tables"
    for table in Base.metadata.tables.values():
        session.delete(table).all()
    session.commit()


def reset(session: sa.orm.Session):
    "Delete entries for all tables insert basic entries"
    clear(session)
    populate(session)


def _create_default_coa(session: sa.orm.Session):
    from .account import AccountDb
    coa = """
    root
        Assets
            Cash
            Receivables
            Inventory
        Liabilities
            Payables
            Shares Issued
            Retained Earnings
        Income/Expense
            Trade
            Interest
            Fees
                Broker
                Administration
            Tax
            Other
    """
    root = AccountDb(name="root", postable=False, parent=None)
    asset = AccountDb(name="Asset", postable=False, parent=root)
    session.commit()
