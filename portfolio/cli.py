import argparse
import getpass

from . import app
from . import config
from . import repo

USER_PROMPT = "Database Credentials -- User: "
PASSWD_PROMPT = "Database Credentials -- Password: "
ADDRESS_PROMPT = "Database Address: "


parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--debug", action="store_true", help="launch in debug mode"
)
parser.add_argument(
    "-r",
    "--run",
    action="store_true",
    help="run the app using flasks development server.",
)
parser.add_argument(
    "-c",
    "--contact",
    action="store_true",
    help="print all contact messages from the database",
)
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


def main():
    args = parser.parse_args()

    if _should_init_repo(args):
        if args.debug:
            repo.init_debug()
        else:
            _login_to_database(args)

    if args.contact:
        _handle_print_messages()

    if args.run:
        app.create().run()


def _should_init_repo(args):
    return args.contact or args.run


def _handle_print_messages():
    ids = repo.print_contact_messages()
    if ids:
        delete = input("Delete these messages (y/n)? ")
        if delete.lower() == "y":
            repo.delete_contact_messages_by_id(ids)


def _login_to_database(args=None):
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
