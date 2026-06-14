"""
Database wrapper.
Tries PostgreSQL first, falls back to in-memory SQLite when PG is
unavailable so the demo can run without infrastructure.
"""
import logging
import sqlite3

logger = logging.getLogger(__name__)

PG_AVAILABLE = True
try:
    import psycopg2
except ImportError:
    PG_AVAILABLE = False


class DBWrapper:
    def __init__(self, dsn=None):
        self.backend = None
        self.conn = None
        if dsn and PG_AVAILABLE:
            try:
                self.conn = psycopg2.connect(dsn)
                self.conn.autocommit = False
                self.backend = 'postgres'
                logger.info('Connected to PostgreSQL')
                return
            except Exception as exc:
                logger.warning('Postgres connect failed: %s', exc)
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.backend = 'sqlite'
        self._init_sqlite()
        logger.info('Using in-memory SQLite (PG unavailable)')

    def _init_sqlite(self):
        cur = self.conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS products (sku TEXT PRIMARY KEY, name TEXT, price REAL)')
        cur.execute('CREATE TABLE IF NOT EXISTS stock (sku TEXT, warehouse TEXT, quantity INTEGER)')
        self.conn.commit()

    def execute(self, sql, params=()):
        if self.backend == 'postgres':
            sql = sql.replace('%s', '%s')
        else:
            sql = sql.replace('%s', '?').replace('INSERT INTO products', 'INSERT OR REPLACE INTO products')
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
