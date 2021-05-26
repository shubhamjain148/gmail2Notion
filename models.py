from enum import unique
from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    refresh_token = db.Column(db.String())
    notion_integration_key = db.Column(db.String())
    database_id = db.Column(db.String())
    label = db.Column(db.String())
    is_active = db.Column(db.Boolean(), unique = False, default = True)

    def __init__(self, refresh_token, notion_integration_key, database_id, label, is_active = True):
        self.refresh_token = refresh_token
        self.notion_integration_key = notion_integration_key
        self.database_id = database_id
        self.label = label
        self.is_active = is_active

    def __repr__(self):
        return '<id {}, refresh_token {}, notion_integration_key {}, database_id {}, is_active {}>'.format(self.id, self.refresh_token, self.notion_integration_key, self.database_id, self.is_active)
    
    def to_dict(self):
        return {
            "id": self.id,
            "notion_key": self.notion_integration_key,
            "database_id": self.database_id
        }