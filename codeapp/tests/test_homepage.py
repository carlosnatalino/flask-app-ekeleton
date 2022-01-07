import logging

from .utils import TestCase


class TestHomePage(TestCase):
    def test_home_page(self) -> None:
        response = self.client.get("/")
        self.assertTemplateUsed("home.html")
        self.assertIn("Home", response.data.decode())
        self.assert_html(response)

    def test_about_page(self) -> None:
        response = self.client.get("/about")
        self.assertTemplateUsed("about.html")
        self.assertIn("About", response.data.decode())
        self.assert_html(response)


if __name__ == "__main__":
    logging.fatal("This file cannot be run directly. Run `pytest` instead.")
