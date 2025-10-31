from pydantic import BaseModel


class AccountLoginModel(BaseModel):
    username: str
    hash: str | None = None


class AccountModel(AccountLoginModel):
    level: int = 0
    guild: int | None = None
    creation_time: int = 0


class AccountLoginSessionModel(BaseModel):
    timeout: int = 0
    session: str = ""


class SessionModel(BaseModel):
    timeout: int = 0
    username: str
