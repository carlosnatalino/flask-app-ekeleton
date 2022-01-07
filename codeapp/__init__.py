# python built-in imports
import os
from logging.config import dictConfig
from typing import Dict, Optional

# python external imports
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# app imports

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "bp.login"
login_manager.login_message_category = "info"

limiter = Limiter(
    key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)

# configuring the logging
# for more info, check:
# https://docs.python.org/3.9/howto/logging.html
# this configuration writes to a file and to the console
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s] "
                "[%(module)s:%(lineno)s] - %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "to_file": {
                "level": "DEBUG",
                "formatter": "default",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "messages.log",
                "maxBytes": 5000000,
                "backupCount": 10,
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console", "to_file"],
        },
    }
)


def create_app(app_settings: Optional[str] = None) -> Flask:
    app: Flask = Flask(__name__)

    if app_settings is None:
        # if there are no settings,
        # runs in development mode
        app_settings = os.getenv(
            "APP_SETTINGS", "codeapp.config.DevelopmentConfig"
        )
        # if no environment is set, set it to `development`
        # more info:
        # https://flask.palletsprojects.com/en/2.0.x/config/#environment-and-debug-features
        if os.getenv("FLASK_ENV") is None:
            os.environ["FLASK_ENV"] = "development"  # pragma: no cover
    app.config.from_object(app_settings)

    # making sure we have "postgresql"
    if (
        app.config["SQLALCHEMY_DATABASE_URI"] is not None
        and "postgres://" in app.config["SQLALCHEMY_DATABASE_URI"]
    ):  # pragma: no cover
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config[
            "SQLALCHEMY_DATABASE_URI"
        ].replace("postgres://", "postgresql://")

    db.init_app(app)
    # the code below activates stricter handling foreign keys
    if (
        app.config["SQLALCHEMY_DATABASE_URI"] is not None
        and "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]
    ):

        def _fk_pragma_on_connect(db_api_con, _) -> None:  # type: ignore
            db_api_con.execute("pragma foreign_keys=ON")

        from sqlalchemy import event  # pylint: disable=import-outside-toplevel

        with app.app_context():
            event.listen(db.engine, "connect", _fk_pragma_on_connect)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # register blueprints
    from codeapp.routes import bp  # pylint: disable=import-outside-toplevel

    app.register_blueprint(bp)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx() -> Dict[str, object]:  # pragma: no cover
        return {"app": app, "db": db}

    return app
