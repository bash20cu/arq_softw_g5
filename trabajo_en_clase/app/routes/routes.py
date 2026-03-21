from flask import Blueprint, redirect, render_template, session, url_for

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return redirect(url_for("main.login_page"))


@main.route("/login")
def login_page():
    return render_template("Login.html")


@main.route("/registro")
def register_page():
    return render_template("Registro.html")


@main.route("/principal")
def principal_page():
    if session.get("user") is None:
        return redirect(url_for("main.login_page"))
    return render_template("principal.html")


@main.route("/logout")
def logout_page():
    session.clear()
    return redirect(url_for("main.login_page"))
