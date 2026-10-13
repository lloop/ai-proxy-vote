-- 1. USERS TABLE
-- Tracks member profiles, membership role, passwords, and voting weight.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT,
    email TEXT,
    role TEXT DEFAULT 'member',
    status TEXT DEFAULT 'Active',
    eligible_to_vote INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed initial test users
INSERT OR IGNORE INTO users (username, password, email, role, status, eligible_to_vote) VALUES 
('lloop', 'password123', 'lloop#lloop.com', 'organizer', 'Active', 1),
('lloop_2', 'password123', 'lloop2#lloop.com', 'member', 'Active', 1),
('lloop_3', 'password123', 'lloop3#lloop.com', 'member', 'Active', 1);

-- 2. PROPOSALS TABLE
-- Stores community governance issues and spending requests.
CREATE TABLE IF NOT EXISTS proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('active', 'passed', 'rejected', 'executed')) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closes_at TIMESTAMP NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id)
);

-- Seed initial proposals
INSERT OR IGNORE INTO proposals (id, title, description, creator_id, status, closes_at) VALUES 
(1, 'new prop', 'a brand new one', 1, 'active', datetime('now', '+3 days'));

-- 3. VOTES TABLE
-- Ensures each user can cast only one vote per proposal.
CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    choice TEXT NOT NULL CHECK(choice IN ('yes', 'no', 'abstain')),
    weight_cast REAL NOT NULL DEFAULT 1.0,
    cast_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proposal_id) REFERENCES proposals(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(proposal_id, user_id)
);

-- 4. TREASURY TRANSACTIONS & USAGE LOGS TABLE
-- Records system usage fees contributed to the treasury and approved expenses.
CREATE TABLE IF NOT EXISTS treasury_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('contribution', 'expense')),
    amount REAL NOT NULL,
    logged_by INTEGER NOT NULL,
    description TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (logged_by) REFERENCES users(id)
);

-- 5. CHAT MESSAGES TABLE
-- Stores real-time community chat history.
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    proposal_id TEXT,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (proposal_id) REFERENCES proposals(id)
);

-- 6. PARTICIPATION LOGS TABLE
-- Tracks hours worked or participation events to dynamically calculate voting weight.
CREATE TABLE IF NOT EXISTS participation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    hours REAL NOT NULL,
    description TEXT NOT NULL,
    logged_by INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (logged_by) REFERENCES users(id)
);

-- 7. SYSTEM USES TABLE
-- Tracks scheduled equipment or facility usage, organizing member responsibility, and pending treasury usage fees.
CREATE TABLE IF NOT EXISTS system_uses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheduled_date TEXT NOT NULL,
    description TEXT NOT NULL,
    organizer_id INTEGER NOT NULL,
    fee_amount REAL DEFAULT 50.00,
    fee_status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organizer_id) REFERENCES users (id)
);

-- Simulates connected bank accounts for the community treasury, tracking current balances and account identifiers.
CREATE TABLE IF NOT EXISTS mock_bank_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_name TEXT NOT NULL,
    account_number TEXT NOT NULL,
    balance REAL DEFAULT 0.00,
    currency TEXT DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. MOCK BANK TRANSACTIONS TABLE
-- Records simulated deposits, withdrawals, and ledger activity associated with mock bank accounts.
CREATE TABLE IF NOT EXISTS mock_bank_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    transaction_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES mock_bank_accounts (id)
);

