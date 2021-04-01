import functools

from pydantic import BaseModel


class NoExtraModel(BaseModel):
    class Config:
        extra = "forbid"


class OrmModel(NoExtraModel):
    class Config:
        orm_mode = True

    @classmethod
    def returner(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            obj = func(*args, **kwargs)
            if obj is None:
                obj = None
            elif isinstance(obj, list):
                obj = [cls.from_orm(o) for o in obj]
            else:
                obj = cls.from_orm(obj)
            return obj

        return wrapper
