from pydantic import BaseModel


class NoExtraModel(BaseModel):
    class Config:
        extra = "forbid"
        orm_mode = True
