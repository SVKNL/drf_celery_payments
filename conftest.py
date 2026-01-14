import os

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from rest_framework.test import APIClient

os.environ.setdefault("DATABASE_URL", "postgresql://payouts:payouts@localhost:5433/payouts")


@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture(autouse=True)
def mock_process_payout_delay(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("payouts.views.process_payout.delay")
