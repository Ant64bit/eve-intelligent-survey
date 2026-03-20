CREATE TABLE IF NOT EXISTS sessions (
    uuid UUID PRIMARY KEY,
    ton TEXT,
    current_question_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS session_history (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL REFERENCES sessions(uuid) ON DELETE CASCADE,
    question_id VARCHAR(50),
    question_reformulee TEXT,
    options_proposees JSONB,
    reponse_utilisateur VARCHAR(50),
    step_order INT,
    answered_at TIMESTAMP DEFAULT NOW()
);