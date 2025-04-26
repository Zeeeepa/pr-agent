-- Migration to add additional indexes and constraints
-- This migration adds additional indexes and constraints to improve performance and data integrity

-- Add indexes to improve query performance
CREATE INDEX IF NOT EXISTS idx_projects_full_name ON projects(full_name);
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);
CREATE INDEX IF NOT EXISTS idx_migrations_status ON migrations(status);

-- Add foreign key constraints to improve data integrity
ALTER TABLE workflow_runs 
ADD CONSTRAINT fk_workflow_runs_workflow_id 
FOREIGN KEY (workflow_id) REFERENCES workflows(id) 
ON DELETE CASCADE 
ON UPDATE CASCADE;

-- Add created_at and updated_at columns to projects table if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'projects' AND column_name = 'created_at') THEN
        ALTER TABLE projects ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'projects' AND column_name = 'updated_at') THEN
        ALTER TABLE projects ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
    END IF;
END
$$;

-- Add created_at and updated_at columns to triggers table if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'triggers' AND column_name = 'created_at') THEN
        ALTER TABLE triggers ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'triggers' AND column_name = 'updated_at') THEN
        ALTER TABLE triggers ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
    END IF;
END
$$;
