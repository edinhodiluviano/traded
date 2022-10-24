import sqlalchemy as sa
import sqlalchemy.ext.declarative

Base = sa.ext.declarative.declarative_base()


class Account(Base):
    __tablename__ = "account"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    parent_id = sa.Column(
        sa.Integer, sa.ForeignKey("account.id"), nullable=True, index=True
    )
    name = sa.Column(sa.String, unique=False, index=True, nullable=False)
    entry = sa.Column(sa.Boolean, index=False, nullable=False)
    active = sa.Column(sa.Boolean, index=True, nullable=False)

    @classmethod
    def new(
        cls,
        *,
        name: str,
        parent: "Account" = None,
        entry: bool = True,
        active: bool = True,
    ):
        parent_id = None
        if parent:
            parent_id = parent.id
        a = cls(
            name=name,
            parent_id=parent_id,
            entry=entry,
            active=active,
        )
        return a


class EntryLine(Base):
    __tablename__ = "entry_line"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    entry_id = sa.Column(sa.Integer, sa.ForeignKey("entry.id"), index=True)
    value = sa.Column(sa.Numeric(12, 6), nullable=False)


class Entry(Base):
    __tablename__ = "entry"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    account_id = sa.Column(sa.Integer, sa.ForeignKey("account.id"), index=True)

    entries = sa.orm.relationship("EntryLine")
