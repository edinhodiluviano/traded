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
    resp = traded.load.chart_of_accounts(filename=coa, session=session)
    assert isinstance(resp, traded.models.Account)


def test_when_load_chart_of_accounts_then_account_count_increase_by_15(
    session, coa
):
    stmt = sa.select(sa.func.count(traded.models.Account.id))
    count_before = session.scalar(stmt)

    traded.load.chart_of_accounts(filename=coa, session=session)
    session.commit()

    count_after = session.scalar(stmt)
    assert count_after == count_before + 16


def test_when_load_chart_of_accounts_then_account_dividends_exists(
    session, coa
):
    traded.load.chart_of_accounts(filename=coa, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "Dividends")
    acc = session.scalar(stmt)
    assert acc.name == "Dividends"


def test_when_load_chart_of_accounts_then_account_root_exists(session, coa):
    traded.load.chart_of_accounts(filename=coa, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "root")
    acc = session.scalar(stmt)
    assert acc.name == "root"


def test_when_load_chart_of_accounts_then_account_dividends_has_revenue_parent(
    session, coa
):
    traded.load.chart_of_accounts(filename=coa, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "Dividends")
    acc = session.scalar(stmt)

    assert acc.parent.name == "Revenue"


def test_when_load_chart_of_accounts_then_account_root_has_revenue_child(
    session, coa
):
    traded.load.chart_of_accounts(filename=coa, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "root")
    acc = session.scalar(stmt)

    assert "Revenue" in [child.name for child in acc.children]
