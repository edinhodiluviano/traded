from pathlib import Path

import sqlalchemy as sa
import yaml

from . import models


def load_chart_of_accounts(filename: Path, session: sa.orm.session):
    """
    Load a Chart of Account defined in a yaml file.

    Example of a yaml file:
    ASSET:
        - Cash
        - Inventory
    LIABILITY:
        - Accounts Payable
    EQUITY:
        - Shareholder Capital
        - Earnings
    REVENUE:
        - Sales
        - Costs of good solds
    EXPENSE:
        - Marketing
    """
    with open(filename) as f:
        file_contents = yaml.safe_load(f)
    root_acc = models.Account.new(name="root", entry=False)
    accounts = _traverse_accounts(file_contents, root_acc)
    session.add(root_acc)
    for account in accounts:
        session.add(account)
    return root_acc


def _traverse_accounts(account, parent):
    if isinstance(account, str):
        yield models.Account.new(name=account, parent=parent)
    elif isinstance(account, list):
        for item in account:
            yield from _traverse_accounts(item, parent)
    elif isinstance(account, dict):
        for key, value in account.items():
            acc = models.Account.new(name=key, parent=parent, entry=False)
            yield acc
            yield from _traverse_accounts(value, acc)
