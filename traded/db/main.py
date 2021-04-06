import os as _os

import sqlalchemy as sa

from . import models


DATABASE_URL = _os.environ["DATABASE_URL"]


engine = sa.create_engine(DATABASE_URL)
SessionLocal = sa.orm.sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def setup(session: sa.orm.Session):
    "Create tables and insert basic entries"
    create_tables()
    populate(session)


def create_tables():
    "Create tables"
    models.Base.metadata.create_all(bind=engine)


def populate(session: sa.orm.Session):
    "Insert basic entries"
    _create_default_coa(session)


def clear(session: sa.orm.Session):
    "Just delete entries for all tables"
    for table in models.Base.metadata.tables.values():
        session.query(table).delete()
    session.commit()


def reset(session: sa.orm.Session):
    "Delete entries for all tables insert basic entries"
    clear(session)
    populate(session)


def _create_default_coa(session: sa.orm.Session):  # noqa: C901
    coa = {
        "root": [
            {
                "Assets": [
                    "Cash",
                    "Receivables",
                    "Inventory",
                ],
            },
            {
                "Liabilities": [
                    "Payables",
                    "Shares Issued",
                    "Retained Earnings",
                ],
            },
            {
                "Income": [
                    "Trade",
                    "Carry",
                ],
            },
            {
                "Expenses": [
                    {
                        "Fees": [
                            "Broker",
                            "Administration",
                        ],
                    },
                    "Tax",
                    "Other",
                ],
            },
        ],
    }

    def _traverse_and_insert_coa(obj, parent_obj, session):
        if isinstance(obj, str):
            acc = models.Account(name=obj, postable=True, parent=[parent_obj])
            session.add(acc)
            return acc
        elif isinstance(obj, dict):
            for k, v in obj.items():
                assert isinstance(v, list)
                if parent_obj is None:
                    acc = models.Account(name=k, postable=False)
                else:
                    acc = models.Account(
                        name=k, postable=False, parent=[parent_obj]
                    )
                session.add(acc)
                for item in v:
                    _traverse_and_insert_coa(item, acc, session)

    _traverse_and_insert_coa(coa, None, session)
    session.commit()
