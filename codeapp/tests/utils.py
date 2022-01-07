import logging
import os
import sys
import time
import unittest
from subprocess import PIPE, Popen

import flask_testing
import requests
from bs4 import BeautifulSoup
from flask import Flask
from selenium import webdriver
from werkzeug.test import TestResponse

from codeapp import create_app as ca


class TestCase(flask_testing.TestCase):
    # the URL below is for the general service
    # url = "https://validator.w3.org/nu/?out=json"

    # the URL below is for the service deployed at Chalmers
    url = "http://onu2.s2.chalmers.se:8888/?out=json"

    def create_app(self) -> Flask:
        os.environ["FLASK_ENV"] = "testing"
        app = ca("codeapp.config.TestingConfig")
        return app

    def assert_html(self, response: TestResponse) -> BeautifulSoup:
        html_to_test = response.data.decode("UTF-8")
        response_html = requests.post(
            self.url,
            headers={"Content-Type": "text/html; charset=UTF-8"},
            data=html_to_test,
        )
        message = ""
        has_error = False

        if response_html.json()["messages"]:
            has_error = True
            for key, value in response_html.json().items():
                if not isinstance(value, list):
                    message += key + " |-> " + value + "\n"
                else:
                    error_number = 1
                    html_split = html_to_test.split("\n")
                    for i in value:
                        message += "\n"
                        if "type" in i:
                            if i["type"] == "error":
                                message += f"\tError {error_number}:" + "\n"
                            elif i["type"] == "warning":
                                message += f"\tWarning {error_number}:" + "\n"
                            else:
                                message += (
                                    f"""\t{i["type"]} {error_number}:\n"""
                                )
                            if error_number == 1:
                                message += (
                                    "\t\tThis is probably the one to look for first!"
                                    + "\n"
                                )

                            message += "\t\tMessage: " + i["message"] + "\n"

                            initial_line = max(0, i["lastLine"] - 3)
                            end_line = min(
                                len(html_split) - 1, i["lastLine"] + 2
                            )

                            message += f"""\t\tLine with problem: {i["lastLine"] - 1}\n"""
                            message += "\t\tCheck the code below:\n"

                            for j in range(initial_line, end_line):
                                mark = ""
                                if j + 1 == i["lastLine"]:
                                    mark = ">>"
                                message += (
                                    f"""\t\t{j}: {mark}\t{html_split[j]}\n"""
                                )
                            error_number += 1
                        else:
                            for k2, v2 in i.items():
                                message += (
                                    "\t" + str(k2) + " -> " + str(v2) + "\n\n"
                                )
        if has_error:
            raise ValueError(f"HTML error:\n{message}")
        soup = BeautifulSoup(html_to_test, "html.parser")
        return soup


class LiveTestCase(unittest.TestCase):
    _configured_port: int
    _process: Popen  # type: ignore

    @classmethod
    def setUpClass(cls) -> None:
        env = os.environ.copy()
        env["APP_SETTINGS"] = "codeapp.config.TestingConfig"
        env["FLASK_ENV"] = "testing"
        # env[
        #     "DATABASE_TEST_URL"
        # ] = "postgresql://postgres:postgres@localhost:5432/db_test"
        # env["REDIS_TEST_URL"] = "redis://localhost:6379"
        cls._configured_port = int(os.environ.get("LIVESERVER_PORT", 5005))
        cls._process = Popen(  # pylint: disable=consider-using-with
            [
                sys.executable,
                "manage.py",
                "run",
                f"--port={cls._configured_port}",
                "--host=localhost",
            ],
            env=env,
            stdout=PIPE,
            stderr=PIPE,
        )
        # waiting for server to start
        while True:
            time.sleep(1)
            if cls._process.stderr is not None:
                line = cls._process.stderr.readline()
                print(line.decode())
                if "Running" in line.decode():
                    break
                if "Address already in use" in line.decode():
                    raise ValueError(
                        f"Address `{cls.get_server_url()}` already in use. "
                        "Please stop any other server instance."
                    )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._process.terminate()

    @classmethod
    def get_server_url(cls) -> str:
        return f"http://localhost:{cls._configured_port}"


class FunctionalTestCase(LiveTestCase):
    wait_before_proceed = False

    def setUp(self) -> None:
        self.browser = webdriver.Firefox()
        self.addCleanup(self.browser.close)
        _value = os.getenv("WAIT")
        if _value:
            self.wait_before_proceed = bool(_value)
        else:
            self.wait_before_proceed = False
        self.browser.switch_to.window(self.browser.current_window_handle)

    def wait(self) -> None:
        if self.wait_before_proceed:
            input("Press any key to proceed...")


if __name__ == "__main__":
    logging.fatal("This file cannot be run directly. Run `pytest` instead.")
