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
