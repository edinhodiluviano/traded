import pytest
import sqlalchemy as sa

import traded


@pytest.fixture(scope="function", autouse=True)
def patch():
    engine = sa.create_engine(traded.db.main.DATABASE_URL)
    SessionLocal = sa.orm.sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    traded.db.main.engine = engine
    traded.db.main.SessionLocal = SessionLocal
    yield engine, SessionLocal


def test_assert_patch_is_patching(patch):
    assert traded.db.main.engine is patch[0]
    assert traded.db.main.SessionLocal is patch[1]


def test_database_starts_with_no_tables():
    m = sa.MetaData()
    m.reflect(traded.db.main.engine)
    assert len(m.tables) == 0


def test_database_create_tables():
    m = sa.MetaData()
    m.reflect(traded.db.main.engine)
    assert len(m.tables) == 0
    traded.db.main.create_tables()
    m.reflect(traded.db.main.engine)
    assert len(m.tables) > 0


def test_database_create_tables_second_run():
    """Asserts above test is not flaky"""
    m = sa.MetaData()
    m.reflect(traded.db.main.engine)
    assert len(m.tables) == 0
    traded.db.main.create_tables()
    m.reflect(traded.db.main.engine)
    assert len(m.tables) > 0


@pytest.fixture(scope="function")
def session(patch):
    session = traded.db.main.SessionLocal()
    try:
        yield session
    finally:
        session.close()


def tables():
    m = sa.MetaData()
    m.reflect(traded.db.main.engine)
    t = list(m.tables.values())
    return t


def test_database_create_tables_doesnt_create_entries(session):
    traded.db.main.create_tables()
    for table in tables():
        entries = session.query(table).count()
        assert entries == 0


def test_database_populate_create_entries(session):
    test_database_create_tables_doesnt_create_entries(session)
    traded.db.main.populate(session)
    total_entries = 0
    for table in tables():
        entries = session.query(table).count()
        total_entries += entries
    assert total_entries > 0


def test_database_clear_delete_entries(session):
    test_database_populate_create_entries(session)
    traded.db.main.clear(session)
    for table in tables():
        entries = session.query(table).count()
        assert entries == 0


def test_database_reset_ends_in_the_same_place_as_start(session):
    traded.db.main.setup(session)
    entries_before = [session.query(table).all() for table in tables()]
    assert len(entries_before) > 0
    traded.db.main.reset(session)
    entries_after = [session.query(table).all() for table in tables()]
    assert len(entries_before) == len(entries_after)
    for n in range(len(entries_before)):
        eb = entries_before[n]
        ef = entries_after[n]
        assert len(eb) == len(ef)
        for k in range(len(eb)):
            assert eb[k].name == ef[k].name
            assert eb[k].postable == ef[k].postable
            assert eb[k].is_active == ef[k].is_active


def test_database_insert_default_coa(session):
    traded.db.main.setup(session)
    accounts = session.query(traded.db.models.Account).all()
    assert len(accounts) == 18
