"""
DATABASE CONFIGURATION - SQLAlchemy ORM Setup
Enterprise-grade database session management and transaction handling
"""

import logging
import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cyberzilla:Cyberzilla123!@localhost:5432/cyberzilla_enterprise",
)

# Create Engine with Enterprise Configuration
engine = create_engine(
    DATABASE_URL,
    # Connection Pooling
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,  # 1 hour
    # Performance
    echo=False,  # Set to True for SQL debugging
    echo_pool=False,
    # Timeouts
    connect_args={
        "connect_timeout": 10,
        "application_name": "cyberzilla_enterprise",
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Scoped Session for Thread Safety
ScopedSession = scoped_session(SessionLocal)

Base = declarative_base()


# Database Event Handlers
@event.listens_for(engine, "connect")
def set_pragmas(dbapi_connection, connection_record):
    """Set database pragmas on connection"""
    try:
        # Enable WAL mode for better concurrency
        dbapi_connection.execute("PRAGMA journal_mode=WAL")
        dbapi_connection.execute("PRAGMA synchronous=NORMAL")
        dbapi_connection.execute("PRAGMA foreign_keys=ON")
        dbapi_connection.execute("PRAGMA busy_timeout=5000")
    except Exception:
        # PostgreSQL doesn't support PRAGMA, ignore errors
        pass


@event.listens_for(engine, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """Ping connection before using it"""
    try:
        dbapi_connection.ping(False)
    except Exception:
        # If ping fails, connection will be recycled
        raise


class DatabaseManager:
    """Enterprise Database Session Management"""

    def __init__(self):
        self.logger = logging.getLogger("database_manager")

    @contextmanager
    def get_db(self) -> Generator[SessionLocal, None, None]:
        """Get database session with automatic cleanup"""
        session = ScopedSession()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
            ScopedSession.remove()

    def get_session(self) -> SessionLocal:
        """Get raw session (use with caution)"""
        return ScopedSession()

    def close_session(self):
        """Close current session"""
        ScopedSession.remove()

    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.get_db() as db:
                db.execute("SELECT 1")
            return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False

    def get_connection_info(self) -> dict:
        """Get database connection information"""
        return {
            "url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL,
            "pool_size": engine.pool.size(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
            "checked_in": engine.pool.checkedin(),
        }


# Initialize database
def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("✅ Database tables initialized successfully")
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")
        raise


# Dependency for FastAPI
def get_database() -> Generator:
    """FastAPI dependency for database sessions"""
    db = ScopedSession()
    try:
        yield db
    finally:
        db.close()
        ScopedSession.remove()


# Global database manager instance
db_manager = DatabaseManager()
