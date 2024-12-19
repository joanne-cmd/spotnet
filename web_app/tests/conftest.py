"""
This module contains the fixtures for the tests.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from web_app.api.main import app
from web_app.db.crud import DBConnector, PositionDBConnector, UserDBConnector
from web_app.db.database import get_database


@pytest.fixture(scope="module")
def client() -> None:
    """
    A client mock fixture
    :return: TestClient
    """
    mock_db_connector = MagicMock(spec=DBConnector)
    app.dependency_overrides[get_database] = lambda: mock_db_connector

    with patch(
        "starknet_py.contract.Contract.from_address", new_callable=AsyncMock
    ) as mock_from_address, patch(
        "starknet_py.net.full_node_client.FullNodeClient.get_class_hash_at",
        new_callable=AsyncMock,
    ) as mock_class_hash, patch(
        "starknet_py.net.http_client.HttpClient.request", new_callable=AsyncMock
    ) as mock_request:
        # Mock return values
        mock_from_address.return_value = MagicMock()
        mock_class_hash.return_value = "0x123"
        mock_request.return_value = {}

        with TestClient(app=app) as test_client:
            yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def mock_db_connector() -> None:
    """
    Mock DBConnector
    :return: None
    """
    mock_connector = MagicMock(spec=DBConnector)
    yield mock_connector


@pytest.fixture(scope="module")
def mock_user_db_connector() -> None:
    """
    Mock for UserDBConnector
    :return: None
    """
    mock_user_connector = MagicMock(spec=UserDBConnector)
    yield mock_user_connector


@pytest.fixture(scope="module")
def mock_position_db_connector() -> None:
    """
    Mock for PositionDBConnector
    :return: None
    """
    mock_position_connector = MagicMock(spec=PositionDBConnector)
    yield mock_position_connector
