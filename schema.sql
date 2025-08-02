CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    picture BLOB DEFAULT NULL,
    administrator BOOLEAN DEFAULT 0
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    item_name TEXT NOT NULL,
    owner INTEGER NOT NULL,
    picture BLOB DEFAULT NULL,
    --uploaded BOOLEAN DEFAULT 1,
    --borrowed BOOLEAN DEFAULT 0,
    comment TEXT DEFAULT NULL,
    FOREIGN KEY(owner) REFERENCES users(id)

);

CREATE TABLE characteristic_keys (
    id INTEGER PRIMARY KEY,
    characteristic_name TEXT NOT NULL UNIQUE

);

CREATE TABLE classification_keys (
    id INTEGER PRIMARY KEY,
    classification_name TEXT NOT NULL UNIQUE

);

CREATE TABLE classifications (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL,
    classification_keys_id INTEGER NOT NULL,
    FOREIGN KEY(item_id) REFERENCES items(id),
    FOREIGN KEY(classification_keys_id) REFERENCES classification_keys(id)    
);

CREATE TABLE characteristics (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL,
    characteristic_keys_id INTEGER NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY(item_id) REFERENCES items(id),
    FOREIGN KEY(characteristic_keys_id) REFERENCES characteristic_keys(id)   
);

CREATE TABLE borrowings (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL,
    borrow_time TEXT NOT NULL,
    return_time TEXT,
    FOREIGN KEY(item_id) REFERENCES items(id) 
);

CREATE TABLE uploads (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL,
    upload_time TEXT NOT NULL,
    removal_time TEXT,
    FOREIGN KEY(item_id) REFERENCES items(id)     

);


INSERT INTO characteristic_keys (characteristic_name) VALUES
    ('tuotemerkki'),
    ('aines'),
    ('koko'),
    ('paino'),
    ('muoto'),
    ('tyyli'),
    ('ikä');

INSERT INTO classification_keys (classification_name) VALUES
    ('sähköiset'),
    ('koneet'),
    ('laitteet'),
    ('työkalu'),
    ('välineet'),
    ('tarvikkeet'),
    ('kalustukset'),
    ('varusteet'),
    ('vaatteet'),
    ('kirjat'),
    ('koristeet'),
    ('soittimet'),
    ('muut'); 

INSERT INTO users (username,password_hash) VALUES
    ('user1','scrypt:32768:8:1$rn3cIYeZ0d7o6ROq$e2afd9d35e56bbce012cb3a5d29aa365e593a073a2426af2730323e74a3fb8ee965891556762c67a15fa138152f1ec64f81cda16684456e2aa9d08c94e101932'),
    ('user2','scrypt:32768:8:1$rn3cIYeZ0d7o6ROq$e2afd9d35e56bbce012cb3a5d29aa365e593a073a2426af2730323e74a3fb8ee965891556762c67a15fa138152dfe234hjvjhjhjhk4456e2aa9d08c94e101932'),
    ('user3','scrypt:32768:8:1$rn3cIYeZ0d7o6ROq$e2afd9sdjlkjljwlennnfjjji8564365e593a073a2426af2730323e74a3fb8ee965891556762c67a15fa138152dfe234hjvjhsdjhk4456e2aa9d08c94e101932');

INSERT INTO items (item_name,owner) VALUES
    ('kossu',2),
    ('vissy',2),
    ('jekku',2),
    ('rikki flyygeli',3),
    ('tuhottu auto',3),
    ('poltettu kirja',1),   
    ('aurinko',2),
    ('auringon luoja',1),
    ('palava mies',2);

INSERT INTO classifications (item_id,classification_keys_id) VALUES
    (1,4),
    (1,13),
    (1,6),
    (2,2),
    (2,1),
    (3,9),
    (4,10),
    (4,5),
    (4,1),
    (4,8),
    (5,11),
    (5,12),
    (6,6),
    (7,7),
    (8,9),
    (9,10),
    (9,11),
    (9,12);


INSERT INTO characteristics (item_id,characteristic_keys_id,value) VALUES
    (1,1,'koskenkorva'),
    (1,2,'alkoholia'),
    (2,2,'vettä'),
    (2,3,'mikroskopinen'),
    (3,7,'9000 vuotta'),
    (4,1,'sibelius'),
    (4,6,'huono'),
    (5,5,'ylihuono'),
    (6,4,'0.1 mikrogrammaa'),
    (6,5,'satunaista'),
    (7,4,'jotakin'),
    (8,1,'jumala'),
    (9,1,'LGBT'),
    (9,2,'liha'),
    (9,3,'paksu'),
    (9,4,'lyhyt'),
    (9,5,'tuli'),
    (9,6,'kuollut'),
    (9,7,'vauva');