-- 수동 마이그레이션 SQL 스크립트
-- Railway 프로덕션 DB에서 누락된 컬럼 추가

-- 1. tone_manner 컬럼 추가 (이미 존재하는지 확인 후)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='projects_project' 
        AND column_name='tone_manner'
    ) THEN
        ALTER TABLE projects_project 
        ADD COLUMN tone_manner VARCHAR(50) NULL;
    END IF;
END$$;

-- 2. genre 컬럼 추가
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='projects_project' 
        AND column_name='genre'
    ) THEN
        ALTER TABLE projects_project 
        ADD COLUMN genre VARCHAR(50) NULL;
    END IF;
END$$;

-- 3. concept 컬럼 추가
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='projects_project' 
        AND column_name='concept'
    ) THEN
        ALTER TABLE projects_project 
        ADD COLUMN concept VARCHAR(50) NULL;
    END IF;
END$$;

-- 4. IdempotencyRecord 테이블 생성
CREATE TABLE IF NOT EXISTS projects_idempotencyrecord (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    idempotency_key VARCHAR(255) NOT NULL,
    project_id INTEGER NULL,
    request_data TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'processing',
    UNIQUE(user_id, idempotency_key)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_idempotency_key ON projects_idempotencyrecord(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_created_at ON projects_idempotencyrecord(created_at);

-- 5. 마이그레이션 기록 업데이트 (Django가 인식하도록)
INSERT INTO django_migrations (app, name, applied)
SELECT 'projects', '0012_add_tone_manner_fields', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM django_migrations 
    WHERE app = 'projects' AND name = '0012_add_tone_manner_fields'
);

-- 확인 쿼리
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'projects_project' 
AND column_name IN ('tone_manner', 'genre', 'concept');