class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass


class SchemaExtractionError(DatabaseError):
    """Raised when schema extraction fails."""
    pass