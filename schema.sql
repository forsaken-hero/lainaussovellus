CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    user_picture BLOB DEFAULT NULL--,
    --administrator BOOLEAN DEFAULT 0
);

CREATE TABLE items (
    item_id INTEGER PRIMARY KEY,
    item_name TEXT NOT NULL,
    owner_id INTEGER NOT NULL,
    item_picture BLOB DEFAULT NULL,
    --uploaded BOOLEAN DEFAULT 1,
    --borrowed BOOLEAN DEFAULT 0,
    item_comment TEXT DEFAULT NULL,
    FOREIGN KEY(owner_id) REFERENCES users(user_id)

);

CREATE TABLE characteristic_keys (
    characteristic_keys_id INTEGER PRIMARY KEY,
    characteristic_name TEXT NOT NULL UNIQUE

);

CREATE TABLE classification_keys (
    classification_keys_id INTEGER PRIMARY KEY,
    classification_name TEXT NOT NULL UNIQUE

);

CREATE TABLE classifications (
    classifications_id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL,
    classification_keys_id INTEGER NOT NULL,
    FOREIGN KEY(item_id) REFERENCES items(item_id) ON DELETE CASCADE,
    FOREIGN KEY(classification_keys_id) REFERENCES classification_keys(classification_keys_id)    
);

CREATE TABLE characteristics (
    characteristics_id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL,
    characteristic_keys_id INTEGER NOT NULL,
    characteristic_value TEXT NOT NULL,
    FOREIGN KEY(item_id) REFERENCES items(item_id) ON DELETE CASCADE,
    FOREIGN KEY(characteristic_keys_id) REFERENCES characteristic_keys(characteristic_keys_id)   
);

CREATE TABLE borrowings (
    borrowings_id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL,
    borrower_id INTEGER NOT NULL,
    borrow_time TEXT NOT NULL,
    FOREIGN KEY(item_id) REFERENCES items(item_id)
    FOREIGN KEY(borrower_id) REFERENCES users(user_id)
);

CREATE TABLE uploads (
    uploads_id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL,
    upload_time TEXT NOT NULL,
    removal_time TEXT,
    FOREIGN KEY(item_id) REFERENCES items(item_id) ON DELETE CASCADE    

);
