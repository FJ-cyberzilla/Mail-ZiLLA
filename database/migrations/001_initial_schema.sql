-- database/migrations/001_initial_schema.sql
-- database/migrations/001_initial_schema.sql
CREATE TABLE IF NOT EXISTS task_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    search_type VARCHAR(50) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    profile_data JSONB NOT NULL,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS search_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    search_parameters JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    results_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- database/migrations/002_add_indexes.sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_results_email ON task_results(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_results_phone ON task_results(phone);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_results_platform ON task_results(platform);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_results_created_at ON task_results(created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_search_tasks_status ON search_tasks(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_search_tasks_user_id ON search_tasks(user_id);
CREATE TABLE IF NOT EXISTS task_results (
    -- Full schema definition matching SQLAlchemy models
);

-- database/migrations/002_add_indexes.sql  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_results_email ON task_results(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_results_created_at ON task_results(created_at);
