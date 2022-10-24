import os

import pytest
import sqlalchemy as sa

import traded


@pytest.fixture
def coa():
    this_file = os.path.realpath(__file__)
    this_file_dir = os.path.dirname(this_file)
    filename = this_file_dir + "/test_coa.yml"
    return filename


def test_when_load_chart_of_accounts_then_returns_account_object(coa, session):
    resp = traded.accounts.load_chart_of_accounts(
        filename=coa, session=session
    )
    assert isinstance(resp, traded.models.Account)


def test_when_load_chart_of_accounts_then_account_count_increase_by_15(
    session, coa
):
    stmt = sa.select(sa.func.count(traded.models.Account.id))
    count_before = session.scalar(stmt)

    traded.accounts.load_chart_of_accounts(filename=coa, session=session)
    session.commit()

    count_after = session.scalar(stmt)
    assert count_after == count_before + 16


def test_when_load_chart_of_accounts_then_account_dividends_exists(
    session, coa
):
    traded.accounts.load_chart_of_accounts(filename=coa, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "Dividends")
    acc = session.scalar(stmt)
    assert acc.name == "Dividends"


def test_when_load_chart_of_accounts_then_account_root_exists(session, coa):
    traded.accounts.load_chart_of_accounts(filename=coa, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "root")
    acc = session.scalar(stmt)
    assert acc.name == "root"


def test_when_load_chart_of_accounts_then_account_dividends_has_revenue_parent(
    session, coa
):
    traded.accounts.load_chart_of_accounts(filename=coa, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "Dividends")
    acc = session.scalar(stmt)

    assert acc.parent.name == "Revenue"


def test_when_load_chart_of_accounts_then_account_root_has_revenue_child(
    session, coa
):
    traded.accounts.load_chart_of_accounts(filename=coa, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "root")
    acc = session.scalar(stmt)

    assert "Revenue" in [child.name for child in acc.children]


def test_when_add_entry_then_cash_balance_reflects_new_entries(session, coa):
    traded.accounts.load_chart_of_accounts(filename=coa, session=session)
    session.commit()

    stmt = sa.select(traded.models.Account)
    accounts = session.scalars(stmt).unique()
    accounts = {a.name: a for a in accounts}

    cash_acc = accounts["Cash"]
    share_acc = accounts["Shareholders"]

    entries = [
        traded.models.EntryLine.new(account=cash_acc, value=10),
        traded.models.EntryLine.new(account=share_acc, value=-10),
    ]
    traded.models.Entry.new(entries=entries, note="unit tests")
    session.commit()

    assert cash_acc.balance == 10


def test_when_add_entry_then_asset_balance_reflects_new_entries(session, coa):
    traded.accounts.load_chart_of_accounts(filename=coa, session=session)
    session.commit()

    stmt = sa.select(traded.models.Account)
    accounts = session.scalars(stmt).unique()
    accounts = {a.name: a for a in accounts}

    cash_acc = accounts["Cash"]
    share_acc = accounts["Shareholders"]
    asset_acc = accounts["Asset"]

    entries = [
        traded.models.EntryLine.new(account=cash_acc, value=10),
        traded.models.EntryLine.new(account=share_acc, value=-10),
    ]
    traded.models.Entry.new(entries=entries, note="unit tests")
    session.commit()

    assert asset_acc.balance == 10


def test_when_add_entry_then_root_balance_remains_zero(session, coa):
    root_acc = traded.accounts.load_chart_of_accounts(
        filename=coa, session=session
    )
    session.commit()

    stmt = sa.select(traded.models.Account)
    accounts = session.scalars(stmt).unique()
    accounts = {a.name: a for a in accounts}

    cash_acc = accounts["Cash"]
    share_acc = accounts["Shareholders"]
    payable_acc = accounts["Accounts Payable"]

    entries = [
        traded.models.EntryLine.new(account=cash_acc, value=10),
        traded.models.EntryLine.new(account=share_acc, value=-7),
        traded.models.EntryLine.new(account=payable_acc, value=-3),
    ]
    traded.models.Entry.new(entries=entries, note="unit tests")
    session.commit()

    assert root_acc.balance == 0
