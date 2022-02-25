from typing import NamedTuple
from urllib.parse import quote_plus


class SQLAlchemyConfig(NamedTuple):
    # implement on subclass type object
    BACKEND = NotImplemented
    DRIVER = NotImplemented
    POST = ""

    # instance attrs
    passwd: str
    user: str
    addr: str
    db: str

    @property
    def prefix(self):
        return f"{self.BACKEND}+{self.DRIVER}://"

    @property
    def credentials(self):
        return f"{quote_plus(self.user)}:{quote_plus(self.passwd)}"

    @property
    def url(self):
        return (
            f"{self.prefix}{self.credentials}@{self.addr}/{self.db}{self.POST}"
        )


class MySQL(SQLAlchemyConfig):
    BACKEND = "mysql"
    DRIVER = "pymysql"
    POST = "?charset=utf8mb4"
