from typing import Dict, Optional

from src.models import CrudServiceProtocol, UserId, UserInfo, UserRow


class FakeCrudService(CrudServiceProtocol):
    def __init__(self, connection=None) -> None:
        self.db: Dict[UserId, UserRow] = {}
        self.next_id = 1

    def create_user(self, user_info: UserInfo) -> Optional[UserId]:
        new_id = self.next_id
        user_id = UserId(new_id)
        self.db[user_id] = UserRow(id=user_id, **user_info.model_dump())
        self.next_id += 1
        return user_id

    def read_user(self, user_id: UserId) -> Optional[UserRow]:
        return self.db.get(user_id)

    def update_user(self, user_id: UserId, user_info: UserInfo) -> Optional[UserRow]:
        if user_id in self.db.keys():
            user_row = UserRow(id=user_id, name=user_info.name, email=user_info.email)
            self.db[user_id] = user_row
            return user_row
        return None

    def delete_user(self, user_id: UserId) -> bool:
        if user_id in self.db:
            del self.db[user_id]
            return True
        return False
