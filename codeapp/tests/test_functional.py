import logging

from .utils import FunctionalTestCase

logger = logging.getLogger("functional")
logger.setLevel(logging.DEBUG)


class TestFunctional(FunctionalTestCase):
    def test_server_is_up_and_running(self) -> None:
        # establish intent
        logger.info(
            "John wants to check if the project website is up and running."
        )

        # introduce, execute, wait
        logger.info(
            "John opens the web browser and tries to access the project."
        )
        self.browser.get(self.get_server_url())
        self.wait()

        # introduce, execute, wait
        logger.info(
            "Once the page loads, it is possible to see the title `Skeleton`"
        )
        self.assertIn("Skeleton", self.browser.title)
        logger.info("John is happy and closes the browser")

    def test_about_page(self) -> None:
        # establish intent
        logger.info(
            "John wants to check if the `about` page of the project is working."
        )

        # introduce, execute, wait
        logger.info(
            "John opens the web browser and tries to access the project."
        )
        self.browser.get(self.get_server_url() + "/about")
        self.wait()

        # introduce, execute, wait
        logger.info(
            "Once the page loads, it is possible to see the page title `About`"
        )
        self.assertIn("About", self.browser.page_source)
        logger.info("John is happy and closes the browser")


if __name__ == "__main__":
    logging.fatal("This file cannot be run directly. Run `pytest` instead.")
