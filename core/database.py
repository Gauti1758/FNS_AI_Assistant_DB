import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator, Dict, Any, Optional
import logging
from config.settings import DatabaseConfig
from core.exceptions import ConnectionError, DatabaseError

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager with optional RealDictCursor."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._base_params = self._build_base_params()

    def _build_base_params(self) -> Dict[str, Any]:
        """Base connection parameters without cursor_factory."""
        return {
            'host': self.config.host,
            'port': self.config.port,
            'database': self.config.database,
            'user': self.config.user,
            'password': self.config.password,
            'sslmode': self.config.sslmode,
            'connect_timeout': 10,
        }

    @contextmanager
    def get_connection(self, use_real_dict_cursor: bool = True) -> Generator[psycopg2.extensions.connection, None, None]:
        """Context manager for database connections with optional RealDictCursor."""
        connection = None
        try:
            params = dict(self._base_params)
            if use_real_dict_cursor:
                params['cursor_factory'] = RealDictCursor

            logger.debug(f"Connecting to database: {self.config.host}:{self.config.port}/{self.config.database}")
            connection = psycopg2.connect(**params)
            connection.autocommit = True
            yield connection
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during database connection: {e}")
            raise DatabaseError(f"Unexpected database error: {e}") from e
        finally:
            if connection:
                try:
                    connection.close()
                    logger.debug("Database connection closed")
                except Exception as e:
                    logger.warning(f"Error closing database connection: {e}")

    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False