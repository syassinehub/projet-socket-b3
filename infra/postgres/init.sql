CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'analyst',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(180) NOT NULL,
    description TEXT DEFAULT '',
    source_ip VARCHAR(64) DEFAULT 'unknown',
    severity VARCHAR(10) DEFAULT 'Medium',
    status VARCHAR(20) DEFAULT 'Nouveau',
    attack_type VARCHAR(80) DEFAULT 'Manual',
    score INTEGER DEFAULT 0,
    confidence INTEGER DEFAULT 0,
    recommendation TEXT DEFAULT '',
    evidence JSONB DEFAULT '[]'::jsonb,
    assigned_to INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS incident_events (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    actor VARCHAR(80) NOT NULL,
    event_type VARCHAR(40) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'admin_role') THEN
        CREATE ROLE admin_role;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'analyst_role') THEN
        CREATE ROLE analyst_role;
    END IF;
END
$$;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE users, incidents, incident_events TO admin_role;
GRANT SELECT ON TABLE users TO analyst_role;
GRANT SELECT, INSERT, UPDATE ON TABLE incidents, incident_events TO analyst_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO admin_role, analyst_role;
