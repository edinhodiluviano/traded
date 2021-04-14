import sqlalchemy as sa

from . import models


def all(session: sa.orm.Session):
    _insert_default_coa(session)
    _insert_default_assets(session)


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
            acc = models.Account(name=obj, parent=[parent_obj])
            session.add(acc)
            return acc
        elif isinstance(obj, dict):
            for k, v in obj.items():
                assert isinstance(v, list)
                if parent_obj is None:
                    acc = models.Account(name=k)
                else:
                    acc = models.Account(name=k, parent=[parent_obj])
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
