-- database/migrations/001_initial_schema.sql
CREATE TABLE IF NOT EXISTS task_results (
    -- Full schema definition matching SQLAlchemy models
);

-- database/migrations/002_add_indexes.sql  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_results_email ON task_results(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_results_created_at ON task_results(created_at);
