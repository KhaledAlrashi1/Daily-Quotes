# my_app/models.py
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('quotes.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Create the quotes table with a 'category' column
    conn.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')

    # Create the categories table with an 'order' column
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            "order" INTEGER
        )
    ''')

    # Ensure the "Others" category exists
    conn.execute('''
        INSERT OR IGNORE INTO categories (name) VALUES (?)
    ''', ("Others",))

    # Check if 'order' column exists in 'categories' table
    cursor = conn.execute("PRAGMA table_info(categories)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'order' not in columns:
        conn.execute('ALTER TABLE categories ADD COLUMN "order" INTEGER')
        # Initialize order values
        conn.execute('UPDATE categories SET "order" = id')
    
    conn.commit()
    conn.close()