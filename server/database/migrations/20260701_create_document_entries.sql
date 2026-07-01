CREATE TABLE IF NOT EXISTS document_entries (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES profiles(id),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(40) NOT NULL DEFAULT 'other',
    source VARCHAR(40) NOT NULL DEFAULT 'uploaded',
    size_in_bytes INTEGER NOT NULL DEFAULT 0,
    mime_type VARCHAR(120) NOT NULL DEFAULT 'application/pdf',
    file_data_base64 TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE INDEX IF NOT EXISTS ix_document_entries_profile_id
    ON document_entries (profile_id);

CREATE INDEX IF NOT EXISTS ix_document_entries_category
    ON document_entries (category);

CREATE INDEX IF NOT EXISTS ix_document_entries_source
    ON document_entries (source);

CREATE INDEX IF NOT EXISTS ix_document_entries_created_at
    ON document_entries (created_at);
