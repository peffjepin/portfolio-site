import os
import secrets
import pathlib
import argparse
import getpass

from . import app
from . import config
from . import repo

USER_PROMPT = "Database Credentials -- User: "
PASSWD_PROMPT = "Database Credentials -- Password: "
ADDRESS_PROMPT = "Database Address: "

_ACCESS_LOG_PATH = pathlib.Path("/var/log/portfolio/access.log")
_ERROR_LOG_PATH = pathlib.Path("/var/log/portfolio/error.log")
_LOG_PATHS = (_ACCESS_LOG_PATH, _ERROR_LOG_PATH)


parser = argparse.ArgumentParser()

# commands
sub_parsers = parser.add_subparsers(help="commands", dest="command")
deploy = sub_parsers.add_parser("deploy", help="deploy an application")
query = sub_parsers.add_parser("query", help="query the database")
kill = sub_parsers.add_parser(
    "kill", help="kill a (production) app that is currently running"
)
setup = sub_parsers.add_parser(
    "setup",
    help="system setup (priveleges required), only needs to be called once, and should be called from the project root directory.",
)
logs = sub_parsers.add_parser("logs", help="peek into the server log files")

# deployment args
mode = deploy.add_mutually_exclusive_group(required=True)
mode.add_argument(
    "-d",
    "--development",
    action="store_true",
    help="launch in development mode",
)
mode.add_argument(
    "-p", "--production", action="store_true", help="launch in production mode"
)
deploy.add_argument(
    "--workers",
    type=int,
    default=4,
    help="how many gunicorn workers (production mode)",
)
deploy.add_argument(
    "--port",
    type=int,
    default=5000,
    help="what port should this server run on",
)
deploy.add_argument("--host", default="127.0.0.1", help="the server host")

# log args
logs.add_argument(
    "type",
    choices=("access", "error"),
    help="which log to look at",
)
logs.add_argument(
    "-l",
    "--length",
    type=int,
    default=25,
    help="the length of the tail of the log to be shown",
)

# always available
parser.add_argument(
    "-A",
    "--db-addr",
    default=None,
    help="the address the database is located at",
)
parser.add_argument(
    "-U", "--db-user", default=None, help="database credentials: User"
)
parser.add_argument(
    "-P", "--db-pass", default=None, help="database credentials: Password"
)
args = None


def main():
    global args
    args = parser.parse_args()

    if args.command == "deploy":
        if args.production:
            _deploy_production()
        else:
            _deploy_development()

    elif args.command == "kill":
        _kill_production_deployment()

    elif args.command == "query":
        _handle_print_messages()

    elif args.command == "setup":
        _setup_for_production()

    elif args.command == "logs":
        _show_logs()


def create_production():
    app_script = pathlib.Path.cwd() / "wsgi.py"
    out = dict()
    with open(app_script, "r") as f:
        exec(f.read(), {}, out)
    application = out["application"]
    if application.secret_key is None:
        application.secret_key = secrets.token_urlsafe(16)
    return application


def _deploy_development():
    if all(arg is None for arg in (args.db_user, args.db_addr, args.db_pass)):
        repo.init_debug()
    else:
        _login_to_database()
    application = app.create()
    application.secret_key = secrets.token_urlsafe(16)
    application.run(host=args.host, port=args.port)


def _setup_for_production():
    if not os.geteuid() == 0:
        print("setup requires root permissions")
        exit(1)

    # setup log files and permissions
    for p in _LOG_PATHS:
        if p.exists():
            os.unlink(p)
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
            os.system(f"chmod a+rwx {p.parent}")
        p.touch()
        os.system(f"chmod a+rw {p}")


def _deploy_production():
    try:
        for p in (_ERROR_LOG_PATH, _ACCESS_LOG_PATH):
            assert os.access(p, os.W_OK), f"write access required: {p}"
    except AssertionError:
        print(
            "you may need to call 'sudo sitectl setup' to setup the log files"
        )
        exit(1)

    os.system(
        f"""gunicorn \\
        -w {args.workers} \\
        --bind '{args.host}:{args.port}' \\
        --access-logfile {_ACCESS_LOG_PATH} \\
        --error-logfile {_ERROR_LOG_PATH} \\
        'portfolio.cli:create_production()' &\n
    """
    )


def _kill_production_deployment():
    os.system("killall gunicorn")


def _show_logs():
    if args.type == "access":
        path = _ACCESS_LOG_PATH
    elif args.type == "error":
        path = _ERROR_LOG_PATH
    os.system(f"tail {path} -n {args.length} -f")


def _handle_print_messages():
    _login_to_database()
    ids = repo.print_contact_messages()
    if ids:
        delete = input("Delete these messages (y/n)? ")
        if delete.lower() == "y":
            repo.delete_contact_messages_by_id(ids)


def _login_to_database():
    if args is not None:
        addr = args.db_addr or input(ADDRESS_PROMPT)
        user = args.db_user or input(USER_PROMPT)
        passwd = args.db_pass or getpass.getpass(PASSWD_PROMPT)
    else:
        addr = input(ADDRESS_PROMPT)
        user = input(USER_PROMPT)
        passwd = getpass.getpass(PASSWD_PROMPT)

    cfg = config.MySQL(user=user, passwd=passwd, addr=addr, db="portfolio")

    try:
        repo.init(cfg)
    except repo.InvalidCredentials:
        print("Invalid credentials, aborting...")
        exit(1)
