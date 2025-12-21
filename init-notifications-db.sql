-- Notifications Service Database Schema
CREATE SCHEMA IF NOT EXISTS public;

-- Create notification table in notifications_db
CREATE TABLE IF NOT EXISTS public.notification (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    task_id INTEGER,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'task_update',
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_notification_user_id ON public.notification(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_task_id ON public.notification(task_id);
CREATE INDEX IF NOT EXISTS idx_notification_is_read ON public.notification(is_read);

-- Grant privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
