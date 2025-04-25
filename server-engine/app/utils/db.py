import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from app.config.config import Config
from app.utils.logger import log_error

class DatabaseManager:
    _pool = None

    @classmethod
    def initialize(cls):
        """Initialize the connection pool."""
        if cls._pool is None:
            try:
                cls._pool = pool.SimpleConnectionPool(
                    1,  # minconn
                    20,  # maxconn
                    Config.DB_CONNECTION_URL
                )
            except Exception as e:
                log_error(e, {"context": "Failed to initialize database pool"})
                raise

    @classmethod
    @contextmanager
    def get_connection(cls):
        """Get a connection from the pool."""
        if cls._pool is None:
            cls.initialize()
        
        conn = None
        try:
            conn = cls._pool.getconn()
            yield conn
        except Exception as e:
            log_error(e, {"context": "Failed to get database connection"})
            raise
        finally:
            if conn:
                cls._pool.putconn(conn)

    @classmethod
    @contextmanager
    def get_cursor(cls):
        """Get a cursor from a connection in the pool."""
        with cls.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                log_error(e, {"context": "Database operation failed"})
                raise
            finally:
                if cursor:
                    cursor.close() 