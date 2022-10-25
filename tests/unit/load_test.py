import os

import pytest
import sqlalchemy as sa

import traded


@pytest.fixture
def this_file_dir():
    this_file = os.path.realpath(__file__)
    this_file_dir = os.path.dirname(this_file)
    return this_file_dir


@pytest.fixture
def coa_file(this_file_dir):
    filename = this_file_dir + "/test_coa.yml"
    return filename


@pytest.fixture
def asset_file(this_file_dir):
    filename = this_file_dir + "/test_assets.yml"
    return filename


@pytest.fixture
def asset_file_2(this_file_dir):
    filename = this_file_dir + "/test_assets_2.yml"
    return filename


def test_when_load_chart_of_accounts_then_returns_account_object(
    coa_file, session
):
    resp = traded.load.chart_of_accounts(filename=coa_file, session=session)
    assert isinstance(resp, traded.models.Account)


def test_when_load_chart_of_accounts_then_account_count_increase_by_15(
    session, coa_file
):
    stmt = sa.select(sa.func.count(traded.models.Account.id))
    count_before = session.scalar(stmt)

    traded.load.chart_of_accounts(filename=coa_file, session=session)
    session.commit()

    count_after = session.scalar(stmt)
    assert count_after == count_before + 16


def test_when_load_chart_of_accounts_then_account_dividends_exists(
    session, coa_file
):
    traded.load.chart_of_accounts(filename=coa_file, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "Dividends")
    acc = session.scalar(stmt)
    assert acc.name == "Dividends"


def test_when_load_chart_of_accounts_then_account_root_exists(
    session, coa_file
):
    traded.load.chart_of_accounts(filename=coa_file, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "root")
    acc = session.scalar(stmt)
    assert acc.name == "root"


def test_when_load_chart_of_accounts_then_account_dividends_has_revenue_parent(
    session, coa_file
):
    traded.load.chart_of_accounts(filename=coa_file, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "Dividends")
    acc = session.scalar(stmt)

    assert acc.parent.name == "Revenue"


def test_when_load_chart_of_accounts_then_account_root_has_revenue_child(
    session, coa_file
):
    traded.load.chart_of_accounts(filename=coa_file, session=session)
    session.commit()

    Acc = traded.models.Account
    stmt = sa.select(Acc).where(Acc.name == "root")
    acc = session.scalar(stmt)

    assert "Revenue" in [child.name for child in acc.children]


def test_when_load_assets_then_return_list(session, asset_file):
    r = traded.load.assets(filename=asset_file, session=session)
    assert isinstance(r, list)


def test_when_load_assets_then_list_has_4_elements(session, asset_file):
    r = traded.load.assets(filename=asset_file, session=session)
    assert len(r) == 4


def test_when_load_assets_then_list_elements_are_assets(session, asset_file):
    r = traded.load.assets(filename=asset_file, session=session)
    for elem in r:
        assert isinstance(elem, traded.models.Asset)


def test_when_load_assets_then_asset_count_increase_by_4(session, asset_file):
    stmt = sa.select(sa.func.count(traded.models.Asset.id))
    count_before = session.scalar(stmt)

    traded.load.assets(filename=asset_file, session=session)
    session.commit()

    count_after = session.scalar(stmt)
    assert count_after == count_before + 4


def test_when_load_assets_then_BRL_is_available(session, asset_file):
    traded.load.assets(filename=asset_file, session=session)
    session.commit()

    Asset = traded.models.Asset
    stmt = sa.select(Asset).where(Asset.name == "BRL")
    result = session.scalar(stmt)

    assert isinstance(result, Asset)
    assert result.name == "BRL"


def test_given_loaded_assets_when_get_assets_then_itsa4_price_asset_is_brl(
    session, asset_file
):
    traded.load.assets(filename=asset_file, session=session)
    session.commit()

    Asset = traded.models.Asset
    stmt = sa.select(Asset).where(Asset.name == "ITSA4")
    result = session.scalar(stmt)

    assert result.price_asset.name == "BRL"


def test_given_load_assets_1_when_load_assets_2_then_assets_count_increase_2(
    session, asset_file, asset_file_2
):
    traded.load.assets(filename=asset_file, session=session)
    session.commit()

    stmt = sa.select(sa.func.count(traded.models.Asset.id))
    count_before = session.scalar(stmt)

    traded.load.assets(filename=asset_file_2, session=session)
    session.commit()

    count_after = session.scalar(stmt)
    assert count_after == count_before + 2


def test_given_load_assets_1_when_load_assets_2_then_bbdc4_price_asset_is_brl(
    session, asset_file, asset_file_2
):
    traded.load.assets(filename=asset_file, session=session)
    session.commit()
    traded.load.assets(filename=asset_file_2, session=session)
    session.commit()

    bbdc4 = traded.models.Asset.get_from_name(name="BBDC4", session=session)
    assert bbdc4.price_asset.name == "BRL"
