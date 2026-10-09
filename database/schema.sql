-- 1. USERS TABLE
-- Tracks member profiles, membership tier, and voting weight.
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    contact_info TEXT,
    tier TEXT NOT NULL CHECK(tier IN ('general', 'organizer')),
    voting_weight REAL NOT NULL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. PROPOSALS TABLE
-- Stores community governance issues and spending requests.
CREATE TABLE proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('active', 'passed', 'rejected', 'executed')) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closes_at TIMESTAMP NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id)
);

-- 3. VOTES TABLE
-- Ensures each user can cast only one vote per proposal.
-- Stores the voting weight at the time of voting to preserve historical accuracy.
CREATE TABLE votes (
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
CREATE TABLE treasury_logs (
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
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 6. PARTICIPATION LOGS TABLE
-- Tracks hours worked or participation events to dynamically calculate voting weight.
CREATE TABLE participation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    hours REAL NOT NULL,
    description TEXT NOT NULL,
    logged_by INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (logged_by) REFERENCES users(id)
);