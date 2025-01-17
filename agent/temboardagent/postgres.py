#
# Configure and extend psycopg2 for temBoard
#
# - Use float for decimal.
# - dict as default row type
# - per query row_factory
# - connection helpers to hide cursor.
#

import ctypes
import logging
import re
from contextlib import closing

from psycopg2 import connect
from psycopg2.pool import ThreadedConnectionPool
import psycopg2.extensions

from .toolkit.versions import load_libpq


logger = logging.getLogger(__name__)


# See https://www.psycopg.org/docs/faq.html#faq-float
DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    'DEC2FLOAT',
    lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)


def pg_escape(in_string, escapee_char=r"'"):
    out_string = ''
    out_string += escapee_char
    out_string += re.sub(escapee_char, escapee_char * 2, in_string)
    out_string += escapee_char
    return out_string


class Postgres:
    # main object holding Postgres parameters and methods.

    def __init__(
            self, host=None, port=5432, user=None, password=None, dbname=None,
            app=None,
            **kw):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        # Compat with conninfo dict.
        if 'database' in kw:
            dbname = kw['database']
        self.dbname = dbname
        self.app = app
        self._server_version = None

    def __repr__(self):
        return '<{} on {}@{}:{}/{}>'.format(
            self.__class__.__name__,
            self.user, self.host, self.port, self.dbname,
        )

    def dbpool(self):
        return DBConnectionPool(self)

    def pool(self):
        return ThreadedConnectionPool(
            minconn=1, maxconn=2,
            **self.pqvars(),
        )

    def connect(self):
        conn = connect(**self.pqvars())
        conn.set_session(autocommit=True)
        return closing(conn)

    def fetch_version(self):
        if self._server_version is None:
            with self.connect() as conn:
                self._server_version = conn.server_version
        return self._server_version

    def copy(self, **kw):
        defaults = dict(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
            app=self.app,
        )
        kw = dict(defaults, **kw)
        return self.__class__(**kw)

    def pqvars(self, dbname=None):
        return dict(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=dbname or self.dbname,
            connection_factory=FactoryConnection,
            application_name='temboard-agent',
        )


class DBConnectionPool:
    # Pool one connection per database.
    #
    # Not thread-safe.

    def __init__(self, postgres):
        self.postgres = postgres
        self.pool = dict()

    def getconn(self, dbname=None):
        dbname = dbname or self.postgres.dbname
        conn = self.pool.get(dbname)
        if conn and conn.pqstatus() == conn.CONNECTION_BAD:
            logger.debug("Recycling bad connection to db %s.", dbname)
            conn.close()
            del self.pool[dbname]
            conn = None

        if not conn:
            logger.debug("Opening connection to db %s.", dbname)
            pqvars = self.postgres.pqvars(dbname=dbname)
            conn = self.pool.setdefault(dbname, connect(**pqvars))

        return conn

    def closeall(self):
        for dbname in list(self.pool):
            conn = self.pool.pop(dbname)
            logger.debug("Closing pooled connection to %s.", dbname)
            conn.close()

    def __del__(self):
        self.closeall()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closeall()


class FactoryConnection(psycopg2.extensions.connection):  # pragma: nocover
    CONNECTION_OK = 0
    CONNECTION_BAD = 1

    def pqstatus(self):
        try:
            self.libpq
        except AttributeError:
            self.libpq = load_libpq()
            self.libpq.PQstatus.argtypes = [ctypes.c_void_p]
            self.libpq.PQstatus.restype = ctypes.c_int

        return self.libpq.PQstatus(self.pgconn_ptr)

    def cursor(self, *a, **kw):
        row_factory = kw.pop('row_factory', None)
        kw['cursor_factory'] = FactoryCursor.make_factory(
            row_factory=row_factory)
        return super(FactoryConnection, self).cursor(*a, **kw)

    def execute(self, sql, *args):
        with self.cursor() as cur:
            cur.execute(sql, *args)

    def query(self, sql, *args, row_factory=None):
        with self.cursor(row_factory=row_factory) as cur:
            cur.execute(sql, *args)
            for row in cur.fetchall():
                yield row

    def queryone(self, sql, *args, row_factory=None):
        with self.cursor(row_factory=row_factory) as cur:
            cur.execute(sql, *args)
            return cur.fetchone()

    def queryscalar(self, sql, *args):
        return self.queryone(sql, *args, row_factory=scalar)


class FactoryCursor(psycopg2.extensions.cursor):  # pragma: nocover
    # Implement row_factory for psycopg2.

    @classmethod
    def make_factory(cls, row_factory=None):
        # Build a cursor_factory for psycopg2 connection.
        def factory(*a, **kw):
            kw['row_factory'] = row_factory
            return cls(*a, **kw)
        return factory

    def __init__(self, conn, name=None, row_factory=None):
        super(FactoryCursor, self).__init__(conn)
        if not row_factory:
            def row_factory(**kw):
                return kw
        self._row_factory = row_factory

    def fetchone(self):
        row = super(FactoryCursor, self).fetchone()
        kw = dict(zip([c.name for c in self.description], row))
        return self._row_factory(**kw)

    def fetchmany(self, size=None):
        for row in super(FactoryCursor, self).fetchmany(size):
            kw = dict(zip([c.name for c in self.description], row))
            yield self._row_factory(**kw)

    def fetchall(self):
        for row in super(FactoryCursor, self).fetchall():
            kw = dict(zip([c.name for c in self.description], row))
            yield self._row_factory(**kw)


def scalar(**kw):
    # Row factory for scalar.
    return next(iter(kw.values()))
