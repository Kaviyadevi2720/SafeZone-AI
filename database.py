import sqlite3
import os
from datetime import datetime, date

# --- CONFIGURATION ---
DATABASE_FILE = "safety_violations.db"
SNAPSHOTS_DIR = "static/snapshots"

# --- CORE FUNCTIONS ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    # Create the static/snapshots directory if it doesn't exist
    if not os.path.exists(SNAPSHOTS_DIR):
        os.makedirs(SNAPSHOTS_DIR)
        print(f"Created directory: {SNAPSHOTS_DIR}")

    conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    # This allows us to access columns by name
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database and creates the 'violations' table if it doesn't exist.
    This is the function that was missing.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # SQL command to create the table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        snapshot_path TEXT NOT NULL
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()
    print("Database has been initialized successfully.")

def log_violation(snapshot_path):
    """Logs a new violation record into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the current time in a format that's easy to store and read
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # SQL command to insert a new row
    insert_query = "INSERT INTO violations (timestamp, snapshot_path) VALUES (?, ?)"
    cursor.execute(insert_query, (timestamp, snapshot_path))
    
    conn.commit()
    conn.close()

def get_today_stats():
    """Retrieves the total number of violations logged today."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today_str = date.today().strftime("%Y-%m-%d")
    
    # SQL query to count violations with today's date
    query = "SELECT COUNT(id) FROM violations WHERE DATE(timestamp) = ?"
    cursor.execute(query, (today_str,))
    
    # The result will be a tuple like (2,), so we get the first element
    count = cursor.fetchone()[0]
    
    conn.close()
    return {"violations_today": count}

def get_recent_violations(limit=5):
    """Retrieves the most recent violation records, up to a specified limit."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQL query to get the latest violations, ordered by timestamp
    query = "SELECT timestamp, snapshot_path FROM violations ORDER BY timestamp DESC LIMIT ?"
    cursor.execute(query, (limit,))
    
    # Fetch all results and convert them into a list of dictionaries
    violations = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return violations

    return {"violations_today": count}

