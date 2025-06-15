import sqlite3
import logging
from pathlib import Path
from .settings import settings

logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize database with required tables from persist_state.sql"""
    try:
        # Get database path from settings
        db_path = settings.DATABASE_PATH

        # Ensure the database directory exists
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        # Read the SQL schema file
        schema_file = Path(__file__).parent.parent.parent / "persist_state.sql"

        if not schema_file.exists():
            logger.error(f"Schema file not found at {schema_file}")
            raise FileNotFoundError(f"Schema file not found: {schema_file}")

        with open(schema_file, "r") as f:
            schema_sql = f.read()

        # Connect to database and execute schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the schema (CREATE TABLE IF NOT EXISTS statements)
        cursor.executescript(schema_sql)
        conn.commit()

        logger.info(f"Database initialized successfully at {db_path}")

        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        expected_tables = ["folder_state", "potree_metacloud_state"]
        for table in expected_tables:
            if table in table_names:
                logger.info(f"Table '{table}' exists and is ready")
            else:
                logger.warning(f"Expected table '{table}' was not found")

        conn.close()

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
