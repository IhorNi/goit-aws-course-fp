-- Database initialization script for Gradio Chatbot
-- This script is run automatically when using docker-compose for local development

-- Create users table (matches SQLAlchemy model)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Insert default admin user
-- Password: admin123 (bcrypt hash)
-- IMPORTANT: Change this password in production!
INSERT INTO users (username, email, password_hash, is_active, is_admin)
VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$aOqQ1jqi0t5tY94ajdeQyeLsltc20Jb0puHw0amGHme0dfVFI2rT6',
    TRUE,
    TRUE
)
ON CONFLICT (username) DO NOTHING;

-- Create a regular test user
-- Password: user1234 (bcrypt hash)
INSERT INTO users (username, email, password_hash, is_active, is_admin)
VALUES (
    'user',
    'user@example.com',
    '$2b$12$tv.RrsWvdJRJTHWURiXOfuE2AzASEfm.fBZMo6HteTI/ewy79uuiK',
    TRUE,
    FALSE
)
ON CONFLICT (username) DO NOTHING;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chatbot_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chatbot_user;
