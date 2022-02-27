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
        params = _get_common_params()
        return flask.render_template("index.html", **params)

    @app.route("/gamelib")
    def gamelib():
        params = _get_common_params()
        return flask.render_template("gamelib.html", **params)

    @app.route("/chess")
    def chess():
        params = _get_common_params()
        return flask.render_template("chess.html", **params)

    @app.route("/about")
    def about():
        params = _get_common_params()
        return flask.render_template("about.html", **params)

    @app.route("/handle_contact", methods=["POST"])
    def handle_contact():
        repo.insert_contact_message(
            name=flask.request.form["id"],
            email=flask.request.form["contact"],
            msg=flask.request.form["message"],
        )
        flask.session["message"] = "Thanks for the message!"
        return flask.redirect(flask.request.referrer)

    return app


def _get_common_params():
    params = {}
    try:
        params["message"] = flask.session["message"]
        flask.session["message"] = ""
    except KeyError:
        pass
    return params
