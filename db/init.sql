-- Инициализация таблицы для токенов
CREATE TABLE token (
    id SERIAL PRIMARY KEY,
    address VARCHAR NOT NULL UNIQUE,
    initial_sig VARCHAR,
    update_authority VARCHAR
);

-- Инициализация таблицы для подписей
CREATE TABLE signature (
    signature VARCHAR PRIMARY KEY,
    slot INTEGER NOT NULL,
    block_time INTEGER NOT NULL,
    token_id INTEGER NOT NULL,
    FOREIGN KEY (token_id) REFERENCES token(id)
);

-- Инициализация таблицы для держателей токенов
CREATE TABLE holder (
    address VARCHAR NOT NULL,
    token_id INTEGER NOT NULL,
    initial_balance BIGINT NOT NULL,
    current_balance BIGINT NOT NULL,
    last_checked TIMESTAMP NOT NULL,
    PRIMARY KEY (address, token_id),
    FOREIGN KEY (token_id) REFERENCES token(id)
);
