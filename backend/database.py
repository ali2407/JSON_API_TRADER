"""Database configuration and session management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Database file path
DB_DIR = Path(__file__).parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_DIR}/trading_terminal.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False  # Set to True for SQL query logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)

    # Run simple migrations for new columns
    _run_migrations()


def _run_migrations():
    """Run simple column migrations for SQLite"""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)

    # Check if api_keys table exists
    if 'api_keys' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('api_keys')]

        # Add btcc_username if it doesn't exist
        if 'btcc_username' not in columns:
            with engine.connect() as conn:
                conn.execute(text('ALTER TABLE api_keys ADD COLUMN btcc_username VARCHAR'))
                conn.commit()

        # Add btcc_password if it doesn't exist
        if 'btcc_password' not in columns:
            with engine.connect() as conn:
                conn.execute(text('ALTER TABLE api_keys ADD COLUMN btcc_password VARCHAR'))
                conn.commit()
