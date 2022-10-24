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
    o = traded.models.EntryLine.new(account=acc, value=10)
    assert isinstance(o, traded.models.EntryLine)


def test_entry_line_from_dict_return_entryline_object():
    acc = traded.models.Account.new(name="aaa")
    d = {"account": acc, "value": 10}
    o = traded.models.EntryLine.from_dict(d)
    assert isinstance(o, traded.models.EntryLine)


def test_given_unbalanced_entries_when_create_entry_raise_value_error():
    acc = traded.models.Account.new(name="aaa")
    entries = [traded.models.EntryLine.new(account=acc, value=10)]
    with pytest.raises(ValueError):
        traded.models.Entry(entries=entries)


def test_given_balanced_entries_when_new_entry_return_entry_object():
    acc = traded.models.Account.new(name="aaa")
    entries = [
        traded.models.EntryLine.new(account=acc, value=10),
        traded.models.EntryLine.new(account=acc, value=-3),
        traded.models.EntryLine.new(account=acc, value=-7),
    ]
    o = traded.models.Entry.new(entries=entries)
    assert isinstance(o, traded.models.Entry)


def test_given_balanced_entries_and_dict_when_new_entry_return_entry_object():
    acc = traded.models.Account.new(name="aaa")
    entries = [
        traded.models.EntryLine.new(account=acc, value=10),
        traded.models.EntryLine.new(account=acc, value=-7),
        {"account": acc, "value": -3},
    ]
    o = traded.models.Entry.new(entries=entries)
    assert isinstance(o, traded.models.Entry)
