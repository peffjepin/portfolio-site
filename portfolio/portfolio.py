import argparse
import getpass

import app
import config
import repo

USER_PROMPT = "Database Credentials -- User: "
PASSWD_PROMPT = "Database Credentials -- Password: "
ADDRESS_PROMPT = "Database Address: "


parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--debug", action="store_true", help="launch in debug mode"
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


def handle_cli(args):
    exitcode = None
    should_init_repo = args.contact

    if should_init_repo:
        if args.debug:
            repo.init_debug()
        else:
            login_to_db(args)

    if args.contact:
        exitcode = exitcode or handle_print_contacts()

    if exitcode is not None:
        exit(exitcode)


def handle_print_contacts():
    ids = repo.print_contact_messages()
    if ids:
        delete = input("Delete these messages (y/n)? ")
        if delete.lower() == "y":
            repo.delete_contact_messages_by_id(ids)
    return 0


def login_to_db(args):
    addr = args.db_addr or input(ADDRESS_PROMPT)
    user = args.db_user or input(USER_PROMPT)
    passwd = args.db_pass or getpass.getpass(PASSWD_PROMPT)
    cfg = config.MySQL(
        user=user, passwd=passwd, addr=addr, db="portfolio"
    )

    try:
        repo.init(cfg)
    except repo.InvalidCredentials:
        print("Invalid credentials, aborting...")
        exit(1)


if __name__ == "__main__":
    args = parser.parse_args()
    handle_cli(args)

    if not repo.is_initialized():
        login_to_db(args)
    app = app.create(__name__)
    app.run()
