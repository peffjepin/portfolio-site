import flask

from . import repo


_APP_NAME = "portfolio"


def create(config=None):
    app = flask.Flask(_APP_NAME)

    if not repo.is_initialized():
        if config is None:
            raise RuntimeError(
                "repo has not been manually initialized, so a SQLAlchemyConfig"
                " is required to initialize the repo module."
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
        repo.insert_contact_message(
            name=flask.request.form["id"],
            email=flask.request.form["contact"],
            msg=flask.request.form["message"],
        )
        return flask.redirect(flask.request.referrer)

    return app
