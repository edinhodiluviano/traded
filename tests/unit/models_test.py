import pytest
import sqlalchemy as sa

import traded


def test_account_new_return_account_obj():
    acc_obj = traded.models.Account.new(name="aaa")
    assert isinstance(acc_obj, traded.models.Account)


def test_when_save_new_account_then_count_increase_by_one(session):
    stmt = sa.select(sa.func.count(traded.models.Account.id))
    count_before = session.scalar(stmt)

    acc_obj = traded.models.Account.new(name="aaa")
    session.add(acc_obj)
    session.commit()

    count_after = session.scalar(stmt)
    assert count_after == count_before + 1


def test_entry_line_new_return_entryline_objects():
    acc = traded.models.Account.new(name="aaa")
    asset = traded.models.Asset(name="BRL", type="currency", price_asset=None)
    o = traded.models.EntryLine.new(
        account=acc, value=10, asset=asset, quantity=1
    )
    assert isinstance(o, traded.models.EntryLine)


def test_entry_line_from_dict_return_entryline_object():
    acc = traded.models.Account.new(name="aaa")
    asset = traded.models.Asset(name="BRL", type="currency", price_asset=None)
    d = {"account": acc, "value": 10, "asset": asset, "quantity": 1}
    o = traded.models.EntryLine.from_dict(d)
    assert isinstance(o, traded.models.EntryLine)


def test_given_unbalanced_entries_when_create_entry_raise_value_error():
    acc = traded.models.Account.new(name="aaa")
    asset = traded.models.Asset(name="BRL", type="currency", price_asset=None)
    entries = [
        traded.models.EntryLine.new(
            account=acc, value=10, asset=asset, quantity=1
        )
    ]
    with pytest.raises(ValueError):
        traded.models.Entry(entries=entries)


def test_given_balanced_entries_when_new_entry_return_entry_object():
    acc = traded.models.Account.new(name="aaa")
    asset = traded.models.Asset(name="BRL", type="currency", price_asset=None)
    new_entry = traded.models.EntryLine.new
    entries = [
        new_entry(account=acc, value=10, asset=asset, quantity=1),
        new_entry(account=acc, value=-3, asset=asset, quantity=1),
        new_entry(account=acc, value=-7, asset=asset, quantity=1),
    ]
    o = traded.models.Entry.new(entries=entries, note="unit tests")
    assert isinstance(o, traded.models.Entry)


def test_given_balanced_entries_and_dict_when_new_entry_return_entry_object():
    acc = traded.models.Account.new(name="aaa")
    asset = traded.models.Asset(name="BRL", type="currency", price_asset=None)
    new_entry = traded.models.EntryLine.new
    entries = [
        new_entry(account=acc, value=10, asset=asset, quantity=1),
        new_entry(account=acc, value=-7, asset=asset, quantity=1),
        {"account": acc, "value": -3, "asset": asset, "quantity": 1},
    ]
    o = traded.models.Entry.new(entries=entries, note="unit tests")
    assert isinstance(o, traded.models.Entry)


def test_given_new_entry_when_save_then_entry_count_increase_by_one(session):
    stmt = sa.select(sa.func.count(traded.models.Entry.id))
    count_before = session.scalar(stmt)

    acc = traded.models.Account.new(name="aaa")
    asset = traded.models.Asset(name="BRL", type="currency", price_asset=None)
    new_entry = traded.models.EntryLine.new
    entries = [
        new_entry(account=acc, value=10, asset=asset, quantity=1),
        new_entry(account=acc, value=-3, asset=asset, quantity=1),
        new_entry(account=acc, value=-7, asset=asset, quantity=1),
    ]
    o = traded.models.Entry.new(entries=entries, note="unit tests")
    session.add(o)
    session.commit()

    count_after = session.scalar(stmt)
    assert count_after == count_before + 1


def test_given_entry_with_3_lines_when_save_then_entry_lines_increase_by_3(
    session,
):
    stmt = sa.select(sa.func.count(traded.models.EntryLine.id))
    count_before = session.scalar(stmt)

    acc = traded.models.Account.new(name="aaa")
    asset = traded.models.Asset(name="BRL", type="currency", price_asset=None)
    new_entry = traded.models.EntryLine.new
    entries = [
        new_entry(account=acc, value=10, asset=asset, quantity=1),
        new_entry(account=acc, value=-3, asset=asset, quantity=1),
        new_entry(account=acc, value=-7, asset=asset, quantity=1),
    ]
    o = traded.models.Entry.new(entries=entries, note="unit tests")
    session.add(o)
    session.commit()

    count_after = session.scalar(stmt)
    assert count_after == count_before + 3


def test_account_object_has_no_balance_attribute():
    acc = traded.models.Account.new(name="aaa")
    assert not hasattr(acc, "balance")


def test_when_asset_get_from_name_with_non_existing_asset_then_return_none(
    session,
):
    resp = traded.models.Asset.get_from_name(name="aaa", session=session)
    assert resp is None


def test_when_asset_get_from_name_with_existing_asset_then_return_asset(
    session,
):
    asset1 = traded.models.Asset(name="BRL", type="currency", price_asset=None)
    session.add(asset1)
    session.commit()
    asset2 = traded.models.Asset.get_from_name(name="BRL", session=session)
    assert asset1 == asset2
