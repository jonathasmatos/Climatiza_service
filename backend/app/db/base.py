from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    "pk": "%(table_name)s_pkey"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)
