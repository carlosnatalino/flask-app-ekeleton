# pylint: disable=cyclic-import
"""
File that contains all the routes of the application.
This is equivalent to the "controller" part in a model-view-controller architecture.
"""

from typing import Union

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.wrappers import Response as FlaskResponse
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select
from werkzeug.wrappers.response import Response as WerkzeugResponse

# app imports
from codeapp import bcrypt, db
from codeapp.forms import LoginForm, RegistrationForm
from codeapp.models import User

Response = Union[str, FlaskResponse, WerkzeugResponse]

bp = Blueprint("bp", __name__, url_prefix="/")

"""
############################### General routes ################################

The routes below include general views open for all users.
"""


@bp.get("/")
# @login_required  # uncomment if home page is restricted for logged users
def home() -> Response:
    return render_template("home.html")


@bp.get("/about")
def about() -> Response:
    return render_template("about.html")


"""
########################## Specific project routes ############################

Add here the routes specific to your project.
"""


"""
############################ User-related routes ##############################

The routes below include routes related to the user.
"""


@bp.route("/register", methods=["GET", "POST"])
def register() -> Response:
    if current_user.is_authenticated:
        return redirect(url_for("bp.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        _password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        _user = User(
            name=form.name.data, email=form.email.data, password=_password
        )
        db.session.add(_user)
        try:
            db.session.commit()
            flash("User successfully created. Please log in!", "success")
            return redirect(url_for("bp.login"))
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            flash(
                "There was an error while creating your user. Please try again later.",
                "danger",
            )
    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login() -> Response:
    if current_user.is_authenticated:
        return redirect(url_for("bp.home"))
    form = LoginForm()
    if form.validate_on_submit():
        _stmt = select(User).where(User.email == form.email.data).limit(1)
        _user = db.session.execute(_stmt).scalars().first()
        current_app.logger.debug(f"User ({type(_user)}): {_user}")
        if _user and bcrypt.check_password_hash(
            _user.password, form.password.data
        ):
            login_user(_user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash("Welcome!", "success")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("bp.home"))
        flash("Login Unsuccessful. Please check email and password.", "danger")
    return render_template("login.html", title="Login", form=form)


@bp.get("/logout")
def logout() -> Response:
    logout_user()
    flash("Logout successful!", "success")
    return redirect(url_for("bp.login"))


@bp.get("/profile")
@login_required
def profile() -> Response:
    return render_template("profile.html")
