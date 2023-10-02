from functools import wraps
from typing import Callable

import pytest

from src.fakes import FakeCrudService
from src.main import handle_message
from src.models import Message, Metadata, Mode, UserId, UserInfo


def simulate_error(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        raise Exception("Simulated Error")

    return wrapper


@pytest.fixture(scope="module")
def fake_crud_service():
    yield FakeCrudService()


@pytest.fixture(scope="module")
def fake_crud_service_with_error():
    service = FakeCrudService()
    service.create_user = simulate_error(service.create_user)
    yield service


@pytest.fixture
def message_factory() -> Callable[[Mode], Message]:
    def message(mode):
        if mode in ("delete", "read"):
            user_info = None
        else:
            user_info = UserInfo(
                name="Harry Potter", email="theboywholived@hogwarts.magic"
            )
        return Message(
            metadata=Metadata(mode=mode, user_id=UserId(1)), user_info=user_info
        )

    return message


@pytest.mark.parametrize("mode", ["create", "read", "update", "delete"])
def test_handle_message(fake_crud_service, message_factory, mode):
    # Arrange:
    message = message_factory(mode)

    # Act:
    result = handle_message(fake_crud_service, message)

    # Assert
    expectation = {"status_code": 200, "body": "OK"}
    assert result == expectation


def test_handle_create_message_with_error(
    fake_crud_service_with_error, message_factory
):
    # Arrange:
    message = message_factory("create")

    # Act:
    response = handle_message(fake_crud_service_with_error, message)

    # Assert:
    expectation = {"status_code": 500, "body": "Simulated Error"}
    assert response == expectation
