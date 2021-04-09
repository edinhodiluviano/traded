import pytest

import traded


@pytest.fixture(scope="function")
def sess():
    engine = traded.database.create_engine(traded.database.DATABASE_URL)
    SessionLocal = traded.database.sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = SessionLocal()
    traded.database.Base.metadata.create_all(bind=engine)
    traded.account.create_default_coa(session)

    try:
        yield session
    finally:
        session.close()


def test_should_always_pass():
    pass


def test_asset_table_starts_with_no_rows(sess):
    assets = traded.asset.get(sess)
    assert len(assets) == 0


def test_asset_insert(sess):
    test_asset_table_starts_with_no_rows(sess)

    asset1 = traded.asset.AssetCreate(name="USD", type="currency")
    asset2 = traded.asset.insert(sess, asset1)

    asset3 = traded.asset.get_by_name(sess, asset2.name)
    assert asset2 == asset3

    assets = traded.asset.get(sess)
    assert len(assets) == 1
    return assets[0]


def test_asset_create_with_type_as_str():
    for asset in ["currency", "stock"]:
        _ = traded.asset.AssetCreate(name="a", type=asset)


def test_asset_create_with_bogus_type():
    for asset in ["aaa", "", None, 1, "lakmsdclaksmdc"]:
        with pytest.raises(ValueError):
            _ = traded.asset.AssetCreate(name="a", type=asset)


def test_asset_create_with_enum():
    _ = traded.asset.AssetCreate(
        name="a", type=traded.asset.AssetTypes.currency
    )


def test_asset_edit(sess):
    asset_old = test_asset_insert(sess)
    asset_new = traded.asset.edit(
        sess, asset_old.id, field="name", new_value="Dolar"
    )
    assert asset_new.name == "Dolar"
    assert asset_new.id == asset_old.id

    assets = traded.asset.get(sess)
    assert len(assets) == 1
    assert assets[0] == asset_new


def test_get_with_non_existing_name(sess):
    asset = traded.asset.get_by_name(sess, name="xxx")
    assert asset is None


def test_create_default_assets(sess):
    assets = traded.asset.create_default_assets(sess)
    assert len(assets) >= 18
