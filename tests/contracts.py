import logging
from typing import cast

from src.models import CrudServiceProtocol, UserId, UserInfo, UserRow

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CrudServiceContract:
    user_id = UserId(1)
    user_info = UserInfo(name="John", email="john@example.com")
    read_user_row = UserRow(id=1, name="John", email="john@example.com")
    updated_info = UserInfo(name="Jane", email="jane@example.com")

    def create_user(self, crud_service: CrudServiceProtocol):
        self.user_id = crud_service.create_user(self.user_info)
        logger.info(f"{self.user_id=}")
        assert self.user_id is not None, "Failed to create user"

    def read_user(self, crud_service: CrudServiceProtocol):
        user_id = cast(UserId, self.user_id)
        read_user_row = crud_service.read_user(user_id)
        read_user_row = cast(UserRow, read_user_row)
        logger.info(f"{read_user_row.to_user_info()=}")
        assert (
            read_user_row.to_user_info() == self.user_info
        ), "Failed to read correct user info"

    def update_user(self, crud_service: CrudServiceProtocol):
        user_id = cast(UserId, self.user_id)
        updated_row = crud_service.update_user(user_id, self.updated_info)
        logger.info(f"{updated_row=}")
        assert updated_row is not None, "Failed to update user"
        assert (
            updated_row.to_user_info() == self.updated_info
        ), "Updated info is incorrect"

    def delete_user(self, crud_service: CrudServiceProtocol):
        user_id = cast(UserId, self.user_id)
        is_deleted = crud_service.delete_user(user_id)
        logger.info(f"{is_deleted=}")
        assert is_deleted, "Failed to delete user"
