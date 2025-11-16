from traded import database


def test_should_always_pass():
    """Test if all imports and packages are working fine."""
    assert 1


def test_create_session():
    with database.create_session() as sess:
        assert isinstance(sess, database.Session)


def test_select_1():
    with database.create_session() as sess:
        given = sess.dql('select 1 as col')
    assert given == [{'col': 1}]
