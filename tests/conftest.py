import os
from unittest.mock import patch

import pytest
from faker import Faker


@pytest.fixture(scope='session', autouse=True)
def mock_database_file(tmpdir_factory):
    fake = Faker()
    folder = fake.pystr(min_chars=20, max_chars=20)
    tmp_db_file = tmpdir_factory.mktemp(folder) / 'temp.sqlite'
    with patch.dict(os.environ, {'DATABASE_FILENAME': str(tmp_db_file)}):
        yield
