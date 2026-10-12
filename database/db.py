import sqlite3
import os

DB_NAME = "sound_system.sqlite3"

def get_db_connection():
    """Creates and returns a connection to the SQLite database."""
    db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
    conn = sqlite3.connect(db_path)
    # Enable dictionary-like access to rows
    conn.row_factory = sqlite3.Row
    
    return conn

def init_db():
    """Initializes the database using the schema.sql file."""
    conn = get_db_connection()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    
    with open(schema_path, "r") as f:
        schema_sql = f.read()
        
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()