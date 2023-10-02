from enum import StrEnum
from typing import Dict, NewType, Optional, Protocol, Self, TypeAlias

from psycopg2.extensions import connection
from pydantic import BaseModel, EmailStr, Field, model_validator

CrudResult: TypeAlias = Dict[str, str]
UserId = NewType("UserId", int)


class Mode(StrEnum):
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    READ = "read"


class Metadata(BaseModel):
    mode: Mode
    user_id: UserId


class UserInfo(BaseModel):
    name: str = Field(..., max_length=60)
    email: EmailStr = Field(..., max_length=60)

    def to_user_row(self, user_id: UserId) -> "UserRow":
        return UserRow(id=user_id, **self.model_dump())


class Message(BaseModel):
    metadata: Metadata
    user_info: Optional[UserInfo]

    @model_validator(mode="after")
    def validate_user_info(self) -> Self:
        match self.metadata.mode:
            case Mode.CREATE:
                if self.user_info is None:
                    raise ValueError("CREATE: user_info must not be None.")

                return self
            case Mode.READ:
                if self.user_info is None:
                    return self

                raise ValueError("READ: do not include user_info.")
            case Mode.UPDATE:
                if self.user_info is None:
                    raise ValueError("UPDATE: user_info must not be None.")

                return self
            case Mode.DELETE:
                if self.user_info is None:
                    return self

                raise ValueError("DELETE: do not include user_info")


class Event(BaseModel):
    body: Message


class UserRow(BaseModel):
    id: int
    name: str = Field(..., max_length=60)
    email: EmailStr = Field(..., max_length=60)

    def to_user_info(self) -> UserInfo:
        return UserInfo(name=self.name, email=self.email)


class CrudServiceProtocol(Protocol):
    def __init__(self, connection: connection) -> None:
        pass

    def create_user(self, user_info: UserInfo) -> Optional[UserId]:
        pass

    def read_user(self, user_id: UserId) -> Optional[UserRow]:
        pass

    def update_user(self, user_id: UserId, user_info: UserInfo) -> Optional[UserRow]:
        pass

    def delete_user(self, user_id: UserId) -> bool:
        pass
