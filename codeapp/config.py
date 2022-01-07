import os


class BaseConfig:
    TESTING = False
    SECRET_KEY = ">s&}24@{]]#k3&^5$f3#?6?h3{W@[}/7z}2pa]>{3&5%RP<)[("
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///site-dev.db"
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///site-testing.db"
    SQLALCHEMY_ECHO = False
    # disables checking of CSRF for testing
    # more info: https://flask-wtf.readthedocs.io/en/1.0.x/config/
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or ""
    SQLALCHEMY_ECHO = False
