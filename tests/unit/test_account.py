import pytest

import traded


@pytest.fixture(scope="function")
def session():
    engine = traded.database.create_engine(traded.database.DATABASE_URL)
    SessionLocal = traded.database.sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = SessionLocal()
    traded.database.Base.metadata.create_all(bind=engine)

    try:
        yield session
    finally:
        session.close()


def test_should_always_pass():
    pass


def test_db_starts_with_no_accounts(session):
    accs = traded.account.get(session)
    assert len(accs) == 0


def test_create_root(session):
    test_db_starts_with_no_accounts(session)

    # insert
    acc_obj = traded.account.AccountCreate(
        name="root",
        postable=False,
    )
    acc = traded.account.insert(session, acc_obj)

    # check
    accs = traded.account.get(session)
    assert len(accs) == 1
    assert accs[0] == acc
    return acc


def test_create_account_with_parent(session):
    root = test_create_root(session)

    # insert
    acc_obj = traded.account.AccountCreate(
        name="Assets",
        postable=False,
        parent_id=root.id,
    )
    acc = traded.account.insert(session, acc_obj)
    root = traded.account.get_by_id(session, root.id)

    # check
    accs = traded.account.get(session)
    assert len(accs) == 2
    assert accs[0] == root
    assert accs[1] == acc
    assert accs[1].parent_id == root.id
    return accs


def test_root_children(session):
    accs = test_create_account_with_parent(session)
    assert accs[0].children == [accs[1]]


def test_account_parent(session):
    accs = test_create_account_with_parent(session)
    assert accs[1].parent_id == accs[0].id
