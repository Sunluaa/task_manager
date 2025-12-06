-- Create databases
CREATE DATABASE IF NOT EXISTS auth_db;
CREATE DATABASE IF NOT EXISTS tasks_db;

-- Connect to auth_db and create tables
\c auth_db;

CREATE TABLE IF NOT EXISTS public.user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user
INSERT INTO public.user (email, password_hash, full_name, role, is_active)
VALUES ('admin@admin.admin', '$2b$12$qSvqqJWWEsaQbCUEKV6mK.D7KSMVr/oVZB3/wqmPNSvqKyZpOUjN.', 'Admin', 'admin', 1)
ON CONFLICT DO NOTHING;

-- Connect to tasks_db and create tables
\c tasks_db;

CREATE TABLE IF NOT EXISTS public.task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'new',
    priority VARCHAR(50) DEFAULT 'medium',
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

