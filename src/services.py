from typing import Optional, Union

from aurora_data_api import AuroraDataAPIClient
from psycopg2.extensions import connection

from src.models import CrudServiceProtocol, UserId, UserInfo, UserRow

DbConnection = Union[connection, AuroraDataAPIClient]


class CrudService(CrudServiceProtocol):
    def __init__(self, connection: DbConnection) -> None:
        self._conn = connection

    def create_user(self, user_info: UserInfo) -> Optional[UserId]:
        sql = """
            INSERT INTO users (name, email) VALUES (%s, %s)
            ON CONFLICT (email) DO NOTHING
            RETURNING id
        """

        with self._conn.cursor() as cur:
            cur.execute(
                sql,
                (user_info.name, user_info.email),
            )
            user_id = cur.fetchone()

        self._conn.commit()
        if user_id is None:
            return None

        return UserId(user_id[0])

    def read_user(self, user_id: UserId) -> Optional[UserRow]:
        with self._conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM users WHERE id = %s;", (user_id,))
            user_row = cur.fetchone()

        if user_row is None:
            return None

        return UserRow(id=user_row[0], name=user_row[1], email=user_row[2])

    def update_user(self, user_id: UserId, user_info: UserInfo) -> Optional[UserRow]:
        set_clause = ", ".join(f"{k} = %s" for k in user_info.model_dump().keys())
        sql = f"UPDATE users SET {set_clause} WHERE id = %s RETURNING id;"
        with self._conn.cursor() as cur:
            cur.execute(sql, (*user_info.model_dump().values(), user_id))
            updated_id = cur.fetchone()

        self._conn.commit()
        if updated_id is None:
            return None

        return self.read_user(UserId(updated_id[0]))

    def delete_user(self, user_id: UserId) -> bool:
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

        self._conn.commit()
        return True
