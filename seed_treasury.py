import sqlite3
import random
from datetime import datetime, timedelta

def seed_mock_treasury():
    # Connect to your SQLite database file (adjust path if stored in an instance/ folder or database/ folder)
    conn = sqlite3.connect('database/sound_system.sqlite3')  # Update path if your db file is named differently
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if a mock bank account exists, create one if not
    account = cursor.execute("SELECT * FROM mock_bank_accounts ORDER BY id ASC LIMIT 1").fetchone()
    
    if not account:
        cursor.execute(
            """INSERT INTO mock_bank_accounts (account_name, account_number, balance, currency) 
               VALUES (?, ?, ?, ?)""",
            ("Community Main Account", "ES91-MOCK-7890-1234", 1000.00, "EUR")
        )
        conn.commit()
        account = cursor.execute("SELECT * FROM mock_bank_accounts ORDER BY id ASC LIMIT 1").fetchone()
        print("Created default mock bank account.")

    account_id = account['id']

    # 1. Add 500 Euros to the bank account balance
    add_amount = 500.00
    cursor.execute(
        "UPDATE mock_bank_accounts SET balance = balance + ? WHERE id = ?",
        (add_amount, account_id)
    )
    
    # Log the 500 EUR deposit transaction
    cursor.execute(
        """INSERT INTO mock_bank_transactions (account_id, amount, transaction_type, description, created_at) 
           VALUES (?, ?, ?, ?, ?)""",
        (account_id, add_amount, 'deposit', 'Manual top-up of 500 EUR', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )

    # 2. Add some random transactions
    random_transactions = [
        ("Equipment maintenance fee", "withdrawal"),
        ("Member monthly dues contribution", "deposit"),
        ("Community garden supplies", "withdrawal"),
        ("Workshop ticket sales", "deposit"),
        ("Internet and utility bill", "withdrawal")
    ]

    for desc, tx_type in random_transactions:
        amount = round(random.uniform(20.0, 200.0), 2)
        multiplier = 1 if tx_type == 'deposit' else -1
        
        # Update account balance
        cursor.execute(
            "UPDATE mock_bank_accounts SET balance = balance + ? WHERE id = ?",
            (amount * multiplier, account_id)
        )
        
        # Random timestamp within the last 7 days
        random_time = datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
        
        cursor.execute(
            """INSERT INTO mock_bank_transactions (account_id, amount, transaction_type, description, created_at) 
               VALUES (?, ?, ?, ?, ?)""",
            (account_id, amount, tx_type, desc, random_time.strftime('%Y-%m-%d %H:%M:%S'))
        )
    conn.commit()
    conn.close()
    print("Successfully added 500 EUR and random mock transactions to the database.")

if __name__ == '__main__':
    seed_mock_treasury()
    