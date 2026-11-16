import pytest
from fastapi.testclient import TestClient
from main import app


# Why is this in /?
# https://stackoverflow.com/questions/10253826/path-issue-with-pytest-importerror-no-module-named


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
