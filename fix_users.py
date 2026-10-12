import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database/sound_system.sqlite3')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get existing columns in users table
cursor.execute("PRAGMA table_info(users);")
columns = [col[1] for col in cursor.fetchall()]
print("Existing columns:", columns)

# Add missing columns if needed
if 'password' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN password TEXT;")
    print("Added 'password' column.")

if 'role' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT;")
    print("Added 'role' column.")

# Insert test accounts
users = [
    ('organizer_alex', 'password123', 'organizer'),
    ('member_sam', 'password123', 'member')
]

for username, password, role in users:
    cursor.execute(
        '''
        INSERT INTO users (username, password, role)
        SELECT ?, ?, ?
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = ?)
        ''',
        (username, password, role, username)
    )

conn.commit()
conn.close()
print("Users successfully populated and database closed correctly!")