import os

class Config:
    DEBUG = False
    DEVELOPMENT = False
    NOTION_SECRET_KEY = os.getenv("NOTION_SECRET_KEY", "this-is-the-default-key")
    GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID", "random")
    GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET", "random")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
    REDIS_URL = os.environ.get('REDIS_URL')
    SESSION_COOKIE_HTTPONLY = True
    REDIRECT_URL = "http://localhost:3000"

class ProductionConfig(Config):
    REDIRECT_URL = "https://gmail-notion-web.herokuapp.com"
    SESSION_COOKIE_HTTPONLY = False
    pass

class StagingConfig(Config):
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True