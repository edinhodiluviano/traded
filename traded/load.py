from pathlib import Path

import sqlalchemy as sa
import yaml

from . import models


def chart_of_accounts(filename: Path, session: sa.orm.session):
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
    match account:
        case str():
            yield models.Account.new(name=account, parent=parent)
        case list():
            for item in account:
                yield from _traverse_accounts(item, parent)
        case dict():
            for key, value in account.items():
                acc = models.Account.new(name=key, parent=parent, entry=False)
                yield acc
                yield from _traverse_accounts(value, acc)


def assets(filename: Path, session: sa.orm.session) -> list[models.Asset]:
    """
    Load an Asset yaml file.

    Example:
    USD:
        type: currency
    BRL:
        type: currency
        price_asset: USD
    ITSA4:
        type: stock
        price_asset: BRL
    """
    with open(filename) as f:
        assets_dict = yaml.safe_load(f)
    assets = {}
    for asset_name, asset_attrs in assets_dict.items():
        asset_price_obj = _get_asset_price(asset_attrs, assets, session)
        assets[asset_name] = models.Asset(
            name=asset_name,
            type=asset_attrs["type"],
            price_asset=asset_price_obj,
        )
    asset_list = list(assets.values())
    session.add_all(asset_list)
    return asset_list


def _get_asset_price(asset_attrs, assets, session):
    if "price_asset" not in asset_attrs:
        return None
    price_asset = asset_attrs["price_asset"]
    price_asset_in_db = models.Asset.get_from_name(
        name=price_asset, session=session
    )
    if price_asset_in_db is not None:
        return price_asset_in_db
    return assets.get(price_asset, None)
