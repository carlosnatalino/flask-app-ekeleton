import logging
from unittest.mock import patch

from flask import url_for

from codeapp import create_app

from .utils import TestCase


class TestSetup(TestCase):
    def test_routes(self) -> None:
        self.assertEqual(url_for("bp.home"), "/")
        url_for("bp.login")
        url_for("bp.logout")
        url_for("bp.profile")
        url_for("bp.about")

    def test_dev_configuration(self) -> None:
        with patch("codeapp.os.getenv", autospec=True, spec_set=True) as mock:
            mock.return_value = "codeapp.config.DevelopmentConfig"
            app = create_app()
            mock.assert_called()
            self.assertEqual(app.config["SQLALCHEMY_ECHO"], True)

    def test_prod_configuration(self) -> None:
        with patch(
            "codeapp.os.getenv", autospec=True, spec_set=True
        ) as mock, patch(
            "codeapp.config.ProductionConfig.SQLALCHEMY_DATABASE_URI",
            autospec=True,
            spec_set=True,
        ) as mock_config:
            mock.return_value = "codeapp.config.ProductionConfig"
            mock_config.return_value = "sqlite:///site-prod.db"
            app = create_app("codeapp.config.ProductionConfig")
            mock.assert_not_called()
            self.assertEqual(app.config["SQLALCHEMY_ECHO"], False)


if __name__ == "__main__":
    logging.fatal("This file cannot be run directly. Run `pytest` instead.")
