import pytest

#


@pytest.fixture(autouse=True)
def env_setup(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv('DATABASE_URL', ':memory:')

