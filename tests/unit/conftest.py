from unittest.mock import patch

import pytest

from traded import config, database


@pytest.fixture(scope="session", autouse=True)
def settings():
    new_settings = config.Settings(sqlite=True)
    with patch("traded.config.settings", new=new_settings):
        yield new_settings


@pytest.fixture(scope="function", autouse=True)
def session():
    with database.create_session() as session:
        yield session
