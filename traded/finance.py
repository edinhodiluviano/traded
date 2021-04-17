import datetime as dt
from decimal import Decimal
from typing import Optional, List

import sqlalchemy as sa
from fastapi import APIRouter, Path

from ._classes import NoExtraModel
from .dependencies import sess
from .db import models


router = APIRouter(
    prefix="/finance",
    tags=["finance"],
)


class Account(NoExtraModel):
    id: int
    name: str
    balance: Decimal
    parent_id: Optional[int]
    childs: List["Account"]


Account.update_forward_refs()


@router.get("/balancesheet/{fund_id}", response_model=Account)
def get_balance_sheet(
    fund_id: int = Path(..., ge=1),
    datetime: dt.datetime = None,
    session: sa.orm.Session = sess,
):
    """
    Returns the balance sheet for a given fund
    The datetime default value is "now"

    A sample response would be:
    {
        "id": 1,
        "name": "root",
        "balance": 0.0,
        "parent_id": None,
        "childs": [
            {
                "id": 2,
                "name": "Assets",
                "balance": 1000.0,
                "parent_id": 1,
                "childs": [
                    {
                        "id": 3,
                        "name": "Cash",
                        "balance": 500.0,
                        "parent_id": 2,
                        "childs": [],
                    },
                    {
                        "id": 4,
                        "name": "Receivables",
                        "balance": 500.0,
                        "parent_id": 2,
                        "childs": [],
                    },
                    {
                        "id": 5,
                        "name": "Inventory",
                        "balance": 0,
                        "parent_id": 2,
                        "childs": [],
                    },
                ],
            },
            {
                "id": 6,
                "name": "Liabilities",
                "balance": -1000.0,
                "parent_id": 1,
                "childs": [
                    {
                        "id": 7,
                        "name": "Payables",
                        "balance": 0,
                        "parent_id": 6,
                        "childs": [],
                    },
                    {
                        "id": 8,
                        "name": "Shares Issued",
                        "balance": -1000.0,
                        "parent_id": 6,
                        "childs": [],
                    },
                    {
                        "id": 9,
                        "name": "Retained Earnings",
                        "balance": 0,
                        "parent_id": 6,
                        "childs": [],
                    },
                ],
            },
            {
                "id": 10,
                "name": "Income",
                "balance": 0,
                "parent_id": 1,
                "childs": [
                    {
                        "id": 11,
                        "name": "Trade",
                        "balance": 0,
                        "parent_id": 10,
                        "childs": [],
                    },
                    {
                        "id": 12,
                        "name": "Interest",
                        "balance": 0,
                        "parent_id": 10,
                        "childs": [],
                    },
                ],
            },
            {
                "id": 13,
                "name": "Expenses",
                "balance": 0,
                "parent_id": 1,
                "childs": [
                    {
                        "id": 14,
                        "name": "Fees",
                        "balance": 0,
                        "parent_id": 13,
                        "childs": [
                            {
                                "id": 15,
                                "name": "Broker",
                                "balance": 0,
                                "parent_id": 14,
                                "childs": [],
                            },
                            {
                                "id": 16,
                                "name": "Administration",
                                "balance": 0,
                                "parent_id": 14,
                                "childs": [],
                            },
                        ],
                    },
                    {
                        "id": 17,
                        "name": "Tax",
                        "balance": 0,
                        "parent_id": 13,
                        "childs": [],
                    },
                    {
                        "id": 18,
                        "name": "Other",
                        "balance": 0,
                        "parent_id": 13,
                        "childs": [],
                    },
                ],
            },
        ],
    }
    """

    if datetime is None:
        datetime = dt.datetime.utcnow()

    # get all accounts that have a balance
    s = (
        sa.select(
            [models.Account.id, sa.func.sum(models.Entry.value).label("value")]
        )
        .select_from(
            sa.join(
                models.Account,
                models.Entry,
                models.Account.id == models.Entry.account_id,
            )
        )
        .group_by(models.Account.id)
        .where(models.Entry.datetime <= datetime)
    )
    accounts_balance = session.execute(s).fetchall()
    accounts_balance = {a.id: a.value for a in accounts_balance}

    # get all accounts
    accounts_list = (
        session.query(models.Account)
        .order_by(models.Account.parent_id.desc())
        .all()
    )
    accounts_list = [
        Account(
            id=acc.id,
            name=acc.name,
            balance=accounts_balance.get(acc.id, Decimal(0)),
            childs=[],
            parent_id=acc.parent_id,
        )
        for acc in accounts_list
    ]

    accounts_tree = _create_acc_tree(accounts_list)
    return accounts_tree


def _create_acc_tree(accounts: list[Account]) -> Account:
    accounts_dict = {acc.id: acc for acc in accounts}
    for acc in accounts:
        if acc.parent_id is None:
            continue
        accounts_dict[acc.parent_id].childs.append(acc)
        accounts_dict[acc.parent_id].balance += acc.balance
    return accounts_dict[1]
