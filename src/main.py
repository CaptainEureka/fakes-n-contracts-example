import logging
from typing import Any, Dict, cast

import psycopg2
from psycopg2.extensions import connection

from src.models import (
    CrudServiceProtocol,
    Event,
    Message,
    Mode,
    UserId,
    UserInfo,
    UserRow,
)
from src.services import CrudService

# Constants
DB_NAME = "test"
DB_USER = "admin"
DB_PASSWORD = "password"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

# Configure logging
logging.basicConfig(level=logging.INFO)


def get_db_connection() -> connection:
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def app(event: Dict[str, Any]) -> None:
    with get_db_connection() as conn:
        validated_body = Event.model_validate(event).body
        handle_message(crud_service=CrudService(conn), msg=validated_body)


def handle_message(
    crud_service: CrudServiceProtocol, msg: Message
) -> Dict[str, int | str]:
    mode = msg.metadata.mode
    user_id = msg.metadata.user_id
    user_info = msg.user_info

    try:
        match mode:
            case Mode.CREATE:
                user_info = cast(UserInfo, user_info)
                create_response: UserId | None = crud_service.create_user(
                    user_info=user_info
                )
                logging.info(f"Create Response: {create_response}")
            case Mode.READ:
                read_response: UserRow | None = crud_service.read_user(user_id=user_id)
                logging.info(f"Read Response: {read_response}")
            case Mode.UPDATE:
                user_info = cast(UserInfo, user_info)
                update_response: UserRow | None = crud_service.update_user(
                    user_id=user_id, user_info=user_info
                )
                logging.info(f"Update Response: {update_response}")
            case Mode.DELETE:
                delete_response: bool = crud_service.delete_user(user_id=user_id)
                logging.info(f"Delete Response: {delete_response}")

        return {"status_code": 200, "body": "OK"}
    except Exception as e:
        return {"status_code": 500, "body": str(e)}


if __name__ == "__main__":
    event = {
        "body": {
            "metadata": {"mode": "delete", "user_id": 7},
            "user_info": None
            # "user_info": {
            #     "name": "Severus Snape",
            #     "email": "thehalfbloodprince@gmail.com",
            # },
        }
    }
    app(event=event)
