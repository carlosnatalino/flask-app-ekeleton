import logging
from unittest.mock import patch

from .utils import TestCase


class TestUser(TestCase):
    def test_login_render(self) -> None:
        response = self.client.get("/login")
        self.assert200(response)

    def test_incorrect_email(self) -> None:
        response = self.client.post(
            "/login",
            data={"email": "xyz@chalmers.se", "password": "123456"},
            follow_redirects=True,
        )
        self.assert200(response)
        self.assertTemplateUsed("login.html")
        self.assertIn("Please check email", response.data.decode())
        self.assert_html(response)

    def test_incorrect_password(self) -> None:
        response = self.client.post(
            "/login",
            data={"email": "default@chalmers.se", "password": "123456"},
            follow_redirects=True,
        )
        self.assert200(response)
        self.assertTemplateUsed("login.html")
        self.assertIn("Please check email", response.data.decode())
        self.assert_html(response)

    def test_correct_login(self) -> None:
        response = self.client.post(
            "/login",
            data={"email": "default@chalmers.se", "password": "testing"},
            follow_redirects=True,
        )
        self.assertTemplateUsed("home.html")
        self.assertMessageFlashed("Welcome!", "success")
        self.assert_html(response)

    def test_correct_login_redirect(self) -> None:
        response = self.client.post(
            "/login?next=/profile",
            data={"email": "default@chalmers.se", "password": "testing"},
            follow_redirects=True,
        )
        self.assertTemplateUsed("profile.html")
        self.assertMessageFlashed("Welcome!", "success")
        self.assert_html(response)

    def test_logout(self) -> None:
        # first performs the login
        self.test_correct_login()

        # then tests the logout
        response = self.client.get("/logout", follow_redirects=True)
        self.assertTemplateUsed("login.html")
        self.assertMessageFlashed("Logout successful!", "success")
        self.assert_html(response)

    def test_redirect(self) -> None:
        # first performs the login
        self.test_correct_login()

        # then tests the logout
        response = self.client.get("/login", follow_redirects=True)
        self.assertTemplateUsed("home.html")
        self.assert_html(response)

    def test_profile_not_logged(self) -> None:
        response = self.client.get("/profile", follow_redirects=True)
        self.assertTemplateUsed("login.html")
        self.assertIn(
            "Please log in to access this page.", response.data.decode()
        )
        self.assert_html(response)

    def test_profile_logged_in(self) -> None:
        # first performs the login
        self.test_correct_login()

        response = self.client.get("/profile", follow_redirects=True)
        self.assertTemplateUsed("profile.html")
        self.assertIn("User ID", response.data.decode())
        self.assert_html(response)

    def test_sign_up_logged_in(self) -> None:
        # first performs the login
        self.test_correct_login()

        _ = self.client.get(
            "/register",
            follow_redirects=True,
        )
        self.assertTemplateUsed("home.html")

    def test_sign_up_wrong_passwords(self) -> None:
        response = self.client.post(
            "/register",
            data={
                "name": "Testing User",
                "email": "xyz@chalmers.se",
                "password": "testing",
                "confirm_password": "justtest",
            },
            follow_redirects=True,
        )
        self.assertTemplateUsed("register.html")
        self.assertIn(
            "Field must be equal to password.", response.data.decode()
        )
        self.assert_html(response)

    def test_sign_up_existing_email(self) -> None:
        response = self.client.post(
            "/register",
            data={
                "name": "Testing User",
                "email": "default@chalmers.se",
                "password": "testing",
                "confirm_password": "justtest",
            },
            follow_redirects=True,
        )
        self.assertTemplateUsed("register.html")
        self.assertIn(
            "This email is already registered.", response.data.decode()
        )
        self.assert_html(response)

    def test_sign_up_success(self) -> None:
        with patch(
            "codeapp.routes.db.session.add",
            autospec=True,
            spec_set=True,
        ) as mock_add, patch(
            "codeapp.routes.db.session.commit",
            autospec=True,
            spec_set=True,
        ) as mock_commit:
            response = self.client.post(
                "/register",
                data={
                    "name": "Testing User",
                    "email": "newtesting@chalmers.se",
                    "password": "testing",
                    "confirm_password": "testing",
                },
                follow_redirects=True,
            )

            # checks calls to the session
            mock_add.assert_called_once()  # db.session.add()
            mock_commit.assert_called_once()  # db.session.commit()

            # redirects to login upon success
            self.assertTemplateUsed("login.html")
            self.assertIn("User successfully created.", response.data.decode())

    def test_sign_up_exception(self) -> None:
        # in this test, we need to patch the db.session
        # to simulate the database throwing an exception
        with patch(
            "codeapp.routes.db.session.add",
            autospec=True,
            spec_set=True,
        ) as mock_add, patch(
            "codeapp.routes.db.session.commit",
            side_effect=ValueError("Mock error"),
            autospec=True,
            spec_set=True,
        ) as mock_commit:
            # mocks an error when calling the commit() method
            # mock.commit.
            response = self.client.post(
                "/register",
                data={
                    "name": "Testing User",
                    "email": "sign_up_exception@chalmers.se",
                    "password": "testing",
                    "confirm_password": "testing",
                },
                follow_redirects=True,
            )
            mock_add.assert_called_once()
            mock_commit.assert_called_once()
            self.assertTemplateUsed("register.html")
            self.assertIn("There was an error", response.data.decode())


if __name__ == "__main__":
    logging.fatal("This file cannot be run directly. Run `pytest` instead.")
