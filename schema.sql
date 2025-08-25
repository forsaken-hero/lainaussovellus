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
    item_location TEXT NOT NULL,
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
    item_id INTEGER NOT NULL UNIQUE,
    borrower_id INTEGER NOT NULL,
    borrow_time TEXT NOT NULL,
    FOREIGN KEY(item_id) REFERENCES items(item_id)
    FOREIGN KEY(borrower_id) REFERENCES users(user_id)
);



CREATE INDEX idx_items_ownerid ON items(owner_id);
CREATE INDEX idx_items_itemname ON items(item_name);
CREATE INDEX idx_items_itemlocation ON items(item_location);
CREATE INDEX idx_items_itemcomment ON items(item_comment);

CREATE INDEX idx_borrowings_borrowerid_borrowtime
ON borrowings(borrower_id, borrow_time DESC);


CREATE INDEX idx_classifications_itemid ON classifications(item_id);
CREATE INDEX idx_classifications_keysid ON classifications(classification_keys_id);

CREATE INDEX idx_characteristics_itemid ON characteristics(item_id);
CREATE INDEX idx_characteristics_keysid ON characteristics(characteristic_keys_id);
CREATE INDEX idx_characteristics_value ON characteristics(characteristic_value);





