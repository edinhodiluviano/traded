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
    _insert_default_coa(session)
    _insert_default_assets(session)


def clear(session: sa.orm.Session):
    "Just delete entries for all tables"
    for table in models.Base.metadata.tables.values():
        session.query(table).delete()
    session.commit()


def reset(session: sa.orm.Session):
    "Delete entries for all tables insert basic entries"
    clear(session)
    populate(session)


def _insert_default_coa(session: sa.orm.Session):  # noqa: C901 - too complex
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


def _insert_default_assets(session: sa.orm.Session):
    assets = [
        # currencies
        ("USD", "US Dolar", True, "currency"),
        ("EUR", "Euros", True, "currency"),
        ("JPY", "Japanese Yen", True, "currency"),
        ("CNY", "Chinese Yuan", True, "currency"),
        ("CHF", "Swiss Franc", True, "currency"),
        ("BRL", "Brazilian Real", True, "currency"),
        ("BTC", "Bitcoin", True, "currency"),
        ("ETH", "Ethereum", True, "currency"),
        ("XMR", "Monero", True, "currency"),
        ("ADA", "Cardano", True, "currency"),
        ("USDT", "Tether", True, "currency"),
        # indexes
        ("SP500", "S&P 500", True, "index"),
        ("NASDAQ", "Nasdaq", True, "index"),
        ("IBOVESPA", "Ibovespa", True, "index"),
        ("DJIA", "Down Jones Industrial Average", True, "index"),
        ("VIX", "CBOE Volatility Index", True, "index"),
        # rates
        dict(
            name="fed_funds",
            description="Fed Fund Rates",
            is_active=True,
            type="rate",
            rate_frequency="daily",
            rate_day_count="Actual/360",
        ),
        dict(
            name="br_cdi",
            description="Certificado de Deposito Interbancario - BRL",
            is_active=True,
            type="rate",
            rate_frequency="daily",
            rate_day_count="252",
        ),
    ]

    for asset_item in assets:
        if isinstance(asset_item, tuple):
            asset_item = {
                k: v
                for k, v in zip(
                    ("name", "description", "is_active", "type"), asset_item
                )
            }
        asset_db = models.Asset(**asset_item)
        session.add(asset_db)

    session.commit()
