ALTER TABLE voice_profiles
    ADD COLUMN provider VARCHAR(50) NOT NULL DEFAULT 'elevenlabs',
    ADD COLUMN status ENUM('processing', 'ready', 'failed') NOT NULL DEFAULT 'processing',
    ADD COLUMN error_message TEXT NULL;
