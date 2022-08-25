"""Create pytest fixture"""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.api.main import app


@pytest.fixture(scope='session', autouse=True)
def client():
    return TestClient(app)
