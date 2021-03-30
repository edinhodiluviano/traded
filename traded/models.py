from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from .database import Base


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, index=False, nullable=False)
    postable = Column(Boolean, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

#     parent_id = Column(Integer, ForeignKey("account.id"))
#     parent = relationship("Account")

#    children = relationship(
#        "Account",
#        backref=backref("parent", remote_side=[id]),
#    )
