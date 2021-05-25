from app import db
from sqlalchemy.dialects.postgresql import JSON


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    refresh_token = db.Column(db.String())


    def __init__(self, refresh_token):
        self.refresh_token = refresh_token

    def __repr__(self):
        return '<id {}>'.format(self.id)