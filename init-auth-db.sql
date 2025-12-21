-- Auth Service Database Schema
CREATE SCHEMA IF NOT EXISTS public;

-- Create user table in auth_db
CREATE TABLE IF NOT EXISTS public."user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user (password: admin)
-- Hash: $2b$12$qSvqqJWWEsaQbCUEKV6mK.D7KSMVr/oVZB3/wqmPNSvqKyZpOUjN.
INSERT INTO public."user" (email, password_hash, full_name, role, is_active)
VALUES ('admin@admin.admin', '$2b$12$qSvqqJWWEsaQbCUEKV6mK.D7KSMVr/oVZB3/wqmPNSvqKyZpOUjN.', 'Admin User', 'admin', 1)
ON CONFLICT (email) DO NOTHING;

-- Insert worker users (password: admin) - role 'user' for regular users/workers
-- Hash: $2b$12$qSvqqJWWEsaQbCUEKV6mK.D7KSMVr/oVZB3/wqmPNSvqKyZpOUjN.
INSERT INTO public."user" (email, password_hash, full_name, role, is_active)
VALUES 
  ('john@worker.com', '$2b$12$qSvqqJWWEsaQbCUEKV6mK.D7KSMVr/oVZB3/wqmPNSvqKyZpOUjN.', 'John Worker', 'user', 1),
  ('jane@worker.com', '$2b$12$qSvqqJWWEsaQbCUEKV6mK.D7KSMVr/oVZB3/wqmPNSvqKyZpOUjN.', 'Jane Smith', 'user', 1),
  ('bob@worker.com', '$2b$12$qSvqqJWWEsaQbCUEKV6mK.D7KSMVr/oVZB3/wqmPNSvqKyZpOUjN.', 'Bob Johnson', 'user', 1)
ON CONFLICT (email) DO NOTHING;

-- Grant privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
