from pydantic import BaseModel


class NoExtra(BaseModel):
    class Config:
        extra = "forbid"


class OrmMode(NoExtra):
    class Config:
        orm_mode = True


class AccountBase(NoExtra):
    name: str
    postable: bool
    is_active: bool = True


class AccountCreate(AccountBase):
    pass


class Account(AccountBase):
    id: int
