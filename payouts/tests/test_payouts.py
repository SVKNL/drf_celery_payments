from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from rest_framework.test import APIClient

from payouts.models import Payout, PayoutStatus
from payouts.tasks import process_payout


def create_payout(**overrides: Any) -> Payout:
    data = {
        "amount": "100.00",
        "currency": "USD",
        "recipient_details": "Bank account 123456",
        "description": "Test payout",
    }
    data.update(overrides)
    return Payout.objects.create(**data)


@pytest.mark.django_db(transaction=True)
def test_create_payout(api_client: APIClient, mock_process_payout_delay: MagicMock) -> None:
    payload = {
        "amount": "100.50",
        "currency": "USD",
        "recipient_details": "Bank account 123456",
        "description": "Test payout",
    }

    response = api_client.post("/api/payouts/", payload, format="json")

    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "100.50"
    assert data["currency"] == "USD"
    assert data["status"] == "PENDING"
    assert Payout.objects.count() == 1
    mock_process_payout_delay.assert_called_once()


@pytest.mark.django_db
def test_create_with_invalid_amount(api_client: APIClient) -> None:
    payload = {
        "amount": "-1",
        "currency": "USD",
        "recipient_details": "Bank account 123456",
    }

    response = api_client.post("/api/payouts/", payload, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_with_invalid_currency(api_client: APIClient) -> None:
    payload = {
        "amount": "10.00",
        "currency": "AAA",
        "recipient_details": "Bank account 123456",
    }

    response = api_client.post("/api/payouts/", payload, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_with_invalid_recipient_details(api_client: APIClient) -> None:
    payload = {
        "amount": "10.00",
        "currency": "USD",
        "recipient_details": "abc",
    }

    response = api_client.post("/api/payouts/", payload, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_with_forbidden_status(api_client: APIClient) -> None:
    payload = {
        "amount": "10.00",
        "currency": "USD",
        "recipient_details": "Bank account 123456",
        "status": "COMPLETED",
    }

    response = api_client.post("/api/payouts/", payload, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_list_payouts(api_client: APIClient) -> None:
    payout1 = create_payout(amount="10.00")
    payout2 = create_payout(amount="20.00")

    response = api_client.get("/api/payouts/")

    assert response.status_code == 200
    data = response.json()
    ids = {item["id"] for item in data}
    assert ids == {str(payout1.id), str(payout2.id)}


@pytest.mark.django_db
def test_retrieve_payout(api_client: APIClient) -> None:
    payout = create_payout()

    response = api_client.get(f"/api/payouts/{payout.id}/")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(payout.id)


@pytest.mark.django_db
def test_update_status_success(api_client: APIClient) -> None:
    payout = create_payout()

    response = api_client.patch(
        f"/api/payouts/{payout.id}/",
        {"status": PayoutStatus.PROCESSING},
        format="json",
    )

    assert response.status_code == 200
    payout.refresh_from_db()
    assert payout.status == PayoutStatus.PROCESSING


@pytest.mark.django_db
def test_update_status_canceled(api_client: APIClient) -> None:
    payout = create_payout()

    response = api_client.patch(
        f"/api/payouts/{payout.id}/",
        {"status": PayoutStatus.CANCELED},
        format="json",
    )

    assert response.status_code == 200
    payout.refresh_from_db()
    assert payout.status == PayoutStatus.CANCELED


@pytest.mark.django_db
def test_update_status_invalid_transition(api_client: APIClient) -> None:
    payout = create_payout()

    response = api_client.patch(
        f"/api/payouts/{payout.id}/",
        {"status": PayoutStatus.COMPLETED},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_update_immutable_fields_rejected(api_client: APIClient) -> None:
    payout = create_payout()

    response = api_client.patch(
        f"/api/payouts/{payout.id}/",
        {"amount": "250.00", "currency": "EUR"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_delete_payout(api_client: APIClient) -> None:
    payout = create_payout()

    response = api_client.delete(f"/api/payouts/{payout.id}/")

    assert response.status_code == 204
    assert Payout.objects.count() == 0


@pytest.mark.django_db
def test_process_payout_happy_path(mocker: MockerFixture) -> None:
    payout = create_payout()
    mocker.patch("payouts.tasks.time.sleep", return_value=None)

    process_payout(str(payout.id))

    payout.refresh_from_db()
    assert payout.status == PayoutStatus.COMPLETED


@pytest.mark.django_db
def test_process_payout_noop_when_not_pending(mocker: MockerFixture) -> None:
    payout = create_payout(status=PayoutStatus.COMPLETED)
    mocker.patch("payouts.tasks.time.sleep", return_value=None)

    process_payout(str(payout.id))

    payout.refresh_from_db()
    assert payout.status == PayoutStatus.COMPLETED
