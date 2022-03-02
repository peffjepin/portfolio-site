import sys

import sqlalchemy as sql


engine = None
meta = sql.MetaData()
contact_table = sql.Table(
    "contact",
    meta,
    sql.Column("id", sql.Integer, primary_key=True),
    sql.Column("name", sql.String(60)),
    sql.Column("email", sql.String(255)),
    sql.Column("message", sql.String(255)),
)


class InvalidCredentials(Exception):
    pass


def is_initialized():
    return engine is not None


def init(config):
    global engine

    engine = sql.create_engine(
        config.url, echo=False, future=True, pool_recycle=60
    )

    try:
        meta.create_all(engine)
    except sql.exc.OperationalError as e:
        if "access denied" in str(e).lower():
            raise InvalidCredentials()
        raise e


def init_debug():
    global engine

    engine = sql.create_engine(
        "sqlite+pysqlite:///:memory:",
        echo=True,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=sql.pool.StaticPool,
    )
    meta.create_all(engine)


def _check_init():
    if engine is None:
        raise RuntimeError(
            "You must call repo.init before interacting with the database."
        )


def insert_contact_message(name, email, msg, *, _retry=False):
    _check_init()

    stmt = sql.insert(contact_table).values(
        name=name, email=email, message=msg
    )
    try:
        with engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
    except sql.exc.OperationalError as e:
        if "broken pipe" in str(e).lower() and _retry is False:
            insert_contact_message(name, email, msg, _retry=True)
        else:
            raise e


def print_contact_messages(file=sys.stdout):
    _check_init()
    print("\n", file=file)

    with engine.connect() as conn:
        ids = []
        for row in conn.execute(sql.select(contact_table)):
            ids.append(row.id)
            print(f"CONTACT:\n   {row.name}", file=file)
            print(f"   {row.email}", file=file)
            print(f"MESSAGE:\n   {row.message}\n\n", file=file)

    return ids


def delete_contact_messages_by_id(ids):
    _check_init()

    with engine.connect() as conn:
        conn.execute(
            sql.delete(contact_table).where(contact_table.c.id.in_(ids))
        )
        conn.commit()
