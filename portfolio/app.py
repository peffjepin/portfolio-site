import secrets

import flask
import repo


def create(name, config=None):
    app = flask.Flask(name)
    app.secret_key = secrets.token_urlsafe(16)

    if not repo.is_initialized():
        if config is None:
            raise RuntimeError(
                "repo has not been manually initialized, so a DBConfig is "
                "required to initialize the repo module."
            )
        repo.init(config)

    @app.route("/")
    def index():
        return flask.render_template("index.html")

    @app.route("/gamelib")
    def gamelib():
        return flask.render_template("gamelib.html")

    @app.route("/chess")
    def chess():
        return flask.render_template("chess.html")

    @app.route("/about")
    def about():
        return flask.render_template("about.html")

    @app.route("/handle_contact", methods=["POST"])
    def handle_contact():
        flask.flash("Thanks for the message!")
        repo.insert_contact_message(
            name=flask.request.form["id"],
            email=flask.request.form["contact"],
            msg=flask.request.form["message"],
        )
        return flask.redirect(flask.request.referrer)

    return app
