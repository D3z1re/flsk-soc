import sqlalchemy
from .db_session import SqlAlchemyBase


class Relationship(SqlAlchemyBase):
    __tablename__ = 'relatoinship'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    from_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    to_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
