import base64
from datetime import datetime
import db

def picture_converter(data):
    if data:
        return base64.b64encode(data).decode("utf-8")
    return None

def formatter(query, match_value, length=10):
    index = match_value.find(query)
    if index == -1:
        return ""
    start = max(0, index - length)
    end = index + len(query) + length
    snippet = match_value[start:end]
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(match_value) else ""
    return f"{prefix}{snippet}{suffix}"

def available_items(page=1, page_size=10):
    sql = """
        SELECT i.item_id, i.item_name, i.owner_id, i.item_picture
        FROM items i
        WHERE NOT EXISTS (
            SELECT 1
            FROM borrowings b
            WHERE b.item_id = i.item_id
        )
        ORDER BY i.item_id ASC
        LIMIT ? OFFSET ?
    """
    result = []
    limit = page_size
    offset = page_size * (page - 1)
    for data in db.query(sql, [limit, offset]):
        (
            item_id,
            item_name,
            owner_id,
            item_picture,
        ) = data
        picture_b64 = picture_converter(item_picture)
        result.append({
            "item_id": item_id,
            "item_name": item_name,
            "owner_id": owner_id,
            "item_picture": picture_b64,
        })
    return result

def available_items_count():
    sql = """
        SELECT COUNT(*)
        FROM items i
        WHERE NOT EXISTS (
            SELECT 1 
            FROM borrowings b 
            WHERE b.item_id = i.item_id
        )
    """
    return db.query(sql)[0][0]

def borrowed_items(page=1, page_size=10):
    sql = """
        SELECT i.item_id,  
            i.item_name, 
            i.owner_id, 
            i.item_picture, 
            b.borrower_id, 
            b.borrow_time, 
            u.username AS borrower_username 
        FROM items i 
        JOIN borrowings b ON i.item_id = b.item_id 
        JOIN users u ON u.user_id = b.borrower_id
        ORDER BY b.borrow_time DESC
        LIMIT ? OFFSET ?
    """
    result = []
    limit = page_size
    offset = page_size * (page - 1)
    for data in db.query(sql, [limit, offset]):
        (
            item_id,
            item_name,
            owner_id,
            item_picture,
            borrower_id,
            borrow_time,
            borrower_username,
        ) = data
        borrow_date, borrow_clock = borrow_time.split(' ')
        borrow_date = (
            datetime.strptime(borrow_date, "%Y/%m/%d")
            .strftime("%d/%m/%Y")
        )
        picture_b64 = picture_converter(item_picture)
        result.append({
            "item_id": item_id,
            "item_name": item_name,
            "owner_id": owner_id,
            "item_picture": picture_b64,
            "borrower_id": borrower_id,
            "borrow_clock": borrow_clock,
            "borrow_date": borrow_date,
            "borrower_username": borrower_username,
        })
    return result

def user_borrowings(borrower_id, page=1, page_size=10):
    sql = """
        SELECT i.item_id,  
               i.item_name, 
               i.owner_id,
               i.item_picture,
               b.borrow_time
        FROM items i 
        JOIN borrowings b ON i.item_id = b.item_id 
        WHERE b.borrower_id = ?
        ORDER BY b.borrow_time DESC
        LIMIT ? OFFSET ?
    """
    result = []
    limit = page_size
    offset = page_size * (page - 1)
    for data in db.query(sql, [borrower_id, limit, offset]):
        (
            item_id,
            item_name,
            owner_id,
            item_picture,
            borrow_time,
        ) = data
        borrow_date, borrow_clock = borrow_time.split(' ')
        borrow_date = (
            datetime.strptime(borrow_date, "%Y/%m/%d")
            .strftime("%d/%m/%Y")
        )
        picture_b64 = picture_converter(item_picture)
        result.append({
            "item_id": item_id,
            "item_name": item_name,
            "owner_id": owner_id,
            "item_picture": picture_b64,
            "borrow_clock": borrow_clock,
            "borrow_date": borrow_date,
        })
    return result

def borrowed_items_count():
    sql = "SELECT COUNT(*) FROM borrowings;"
    return db.query(sql)[0][0]

def user_borrowings_count(id):
    sql = "SELECT COUNT(*) FROM borrowings WHERE borrower_id = ?"
    return db.query(sql, [id])[0][0]

def user_uploads(owner_id, page=1, page_size=10):
    sql = """
        SELECT i.item_id,
               i.item_name,
               i.owner_id,
               i.item_picture,
               CASE WHEN EXISTS (
                   SELECT 1 FROM borrowings b WHERE b.item_id = i.item_id
               ) THEN 1 ELSE 0 END AS has_borrowing
        FROM items i
        WHERE i.owner_id = ?
        ORDER BY i.item_id ASC
        LIMIT ? OFFSET ?
    """
    result = []
    limit = page_size
    offset = page_size * (page - 1)
    for data in db.query(sql, [owner_id, limit, offset]):
        (
            item_id,
            item_name,
            owner_id,
            item_picture,
            available
        ) = data
        picture_b64 = picture_converter(item_picture)
        result.append({
            "item_id": item_id,
            "item_name": item_name,
            "owner_id": owner_id,
            "item_picture": picture_b64,
            "available": available,
        })
    return result

def user_uploads_count(owner_id):
    sql = "SELECT COUNT(*) FROM items WHERE owner_id = ?"
    return db.query(sql, [owner_id])[0][0]

def is_borrowed(item_id):
    sql = """
        SELECT EXISTS (
            SELECT 1 FROM borrowings WHERE item_id = ?
        ) AS has_borrowing
    """
    if db.query(sql, [item_id])[0][0] == 1:
        return 1
    return None

def insert_item(
    item_name,
    owner_id,
    item_location,
    item_picture=None,
    item_comment=None,
    con=None,
):
    sql = """
        INSERT INTO items (
            item_name,
            owner_id,
            item_location,
            item_picture,
            item_comment
        )
        VALUES (?, ?, ?, ?, ?)
    """
    item_id, con = db.execute(
        sql,
        [item_name, owner_id, item_location, item_picture, item_comment],
        con,
    )
    return item_id, con

def insert_classifications(item_id, item_classifications=None, con=None):
    if item_classifications is None:
        item_classifications = []
    sql = """
        INSERT INTO classifications (
            item_id,
            classification_keys_id
        )
        VALUES (?, ?)
    """
    for data in item_classifications:
        db.execute(sql, [item_id, data], con)

def insert_characteristics(item_id, item_characteristics=None, con=None):
    if item_characteristics is None:
        item_characteristics = {}
    sql = """
        INSERT INTO characteristics (
            item_id,
            characteristic_keys_id,
            characteristic_value
        )
        VALUES (?, ?, ?)
    """
    for data in item_characteristics:
        db.execute(sql, [item_id, data, item_characteristics[data]], con)

def upload_item(
    item_name,
    owner_id,
    item_location,
    item_picture=None,
    item_comment=None,
    item_classifications=None,
    item_characteristics=None,
):
    if item_classifications is None:
        item_classifications = []
    if item_characteristics is None:
        item_characteristics = {}
    con = db.get_connection()
    item_id, _ = insert_item(
        item_name=item_name,
        owner_id=owner_id,
        item_location=item_location,
        item_picture=item_picture,
        item_comment=item_comment,
        con=con,
    )
    insert_classifications(
        item_id=item_id,
        item_classifications=item_classifications,
        con=con,
    )
    insert_characteristics(
        item_id=item_id,
        item_characteristics=item_characteristics,
        con=con,
    )
    con.commit()
    return item_id

def update_item(
    item_id,
    item_name,
    item_location,
    item_picture=None,
    item_comment=None,
    con=None
):
    if item_picture:
        sql = """
            UPDATE items 
            SET item_name = ?,
                item_location = ?,
                item_picture = ?,
                item_comment = ?
            WHERE item_id = ?
        """
        db.execute(
            sql,
            [item_name, item_location, item_picture, item_comment, item_id],
            con,
        )
    else:
        sql = """
            UPDATE items
            SET item_name = ?,
                item_location = ?,
                item_comment = ?
            WHERE item_id = ?
        """
        db.execute(
            sql,
            [item_name, item_location, item_comment, item_id],
            con,
        )

def delete_classifications(item_id, con=None):
    sql = "DELETE FROM classifications WHERE item_id = ?"
    db.execute(sql, [item_id], con)

def delete_characteristics(item_id, con=None):
    sql = "DELETE FROM characteristics WHERE item_id = ?"
    db.execute(sql, [item_id], con)

def edit_item(
    item_id,
    item_name,
    item_location,
    item_picture=None,
    item_comment=None,
    item_classifications=None,
    item_characteristics=None,
):
    if item_classifications is None:
        item_classifications = []
    if item_characteristics is None:
        item_characteristics = {}

    con = db.get_connection()
    delete_classifications(item_id=item_id, con=con)
    delete_characteristics(item_id=item_id, con=con)
    update_item(
        item_id=item_id,
        item_name=item_name,
        item_location=item_location,
        item_picture=item_picture,
        item_comment=item_comment,
        con=con,
     )
    insert_classifications(
        item_id=item_id,
        item_classifications=item_classifications,
        con=con,
    )
    insert_characteristics(
        item_id=item_id,
        item_characteristics=item_characteristics,
        con=con,
    )
    con.commit()

def remove_item(item_id):
    sql = "DELETE FROM items WHERE item_id = ?"
    db.execute(sql, [item_id])

def remove_item_picture(item_id):
    sql = "UPDATE items SET item_picture = NULL WHERE item_id = ?"
    db.execute(sql, [item_id])

def has_no_item_picture(item_id):
    sql = """
        SELECT item_picture IS NULL AS has_no_item_picture
        FROM items
        WHERE item_id = ?
    """
    return db.query(sql, [item_id])[0][0]

def classification_keys():
    """Returns dictionary of the classification_keys as the id: classification_name"""    
    sql = """
        SELECT classification_keys_id, classification_name
        FROM classification_keys
    """
    return {key_id: name for key_id, name in db.query(sql)}

def characteristic_keys():
    """Returns dictionary of the characteristic_keys as the id: characteristic_name"""
    sql = """
        SELECT characteristic_keys_id, characteristic_name
        FROM characteristic_keys
    """
    return {key_id: name for key_id, name in db.query(sql)}

def edit_page_data(item_id):
    sql = """
        SELECT item_name,
               item_location,
               item_picture,
               item_comment
        FROM items
        WHERE item_id = ?
    """
    (
        item_name,
        item_location,
        item_picture,
        item_comment,
    ) = db.query(sql,[item_id])[0]
    picture_b64 = picture_converter(item_picture)
    return {
        "item_name": item_name,
        "item_location": item_location,
        "item_picture": picture_b64,
        "item_comment": item_comment
    }

def item_owner_id(item_id):
    sql = "SELECT owner_id FROM items WHERE item_id = ?"
    return db.query(sql, [item_id])[0][0]

def item_picture(item_id):
    sql = "SELECT item_picture FROM items WHERE item_id = ?"
    item_picture = db.query(sql, [item_id])[0][0]
    picture_b64 = picture_converter(item_picture)
    return picture_b64

def item_name_picture(item_id):
    sql = "SELECT item_name, item_picture FROM items WHERE item_id = ?"
    item_name, item_picture = db.query(sql,[item_id])[0]
    picture_b64 = picture_converter(item_picture)
    return {
        "item_name": item_name,
        "item_picture": picture_b64,
    }

def item_classifications(item_id):
    """Returns item_classifications as list of integers"""
    sql = "SELECT classification_keys_id FROM classifications WHERE item_id = ?"
    return [key_id for key_id, in db.query(sql, [item_id])]

def item_characteristics(item_id):
    """Returns item_characteristics as a dictionary of
    characteristic_keys_id: characteristic_value"""
    sql = """
        SELECT characteristic_keys_id, characteristic_value
        FROM characteristics
        WHERE item_id = ?
    """
    return {key_id: value for key_id, value in db.query(sql, [item_id])}

def borrow_item(item_id, borrower_id):
    sql = "INSERT INTO borrowings (item_id, borrower_id, borrow_time) VALUES (?, ?, ?)"
    borrowings_id, _ = db.execute(
        sql,
        [item_id, borrower_id, datetime.now().strftime("%Y/%m/%d %H:%M")]
    )
    return borrowings_id

def borrower_id(item_id):
    sql = "SELECT borrower_id FROM borrowings WHERE item_id = ?"
    return db.query(sql,[item_id])[0][0]

def return_item(item_id):
    sql = "DELETE FROM borrowings WHERE item_id = ?"
    db.execute(sql,[item_id])

def search(query, page=1, page_size=10):
    """
    Return search results as a list of tuples:
    [
        (
            {
                "item_id": 1,
                "item_name": "Bike",
                "item_picture": "base64...",
                "owner_id": 42,
                "borrower_id": 7
            },
            {
                "Omistaja": ["Alice"],
                "Kommentti": ["Good condition"]
            }
        ),
        ...
    ]
    """
    sql = """
        WITH base_items AS (
            SELECT 
                i.item_id,
                i.item_name,
                i.item_picture,
                i.owner_id,
                u.username AS owner_username,
                i.item_location,
                i.item_comment
            FROM items i
            JOIN users u ON u.user_id = i.owner_id
        ),
        matches AS (
            SELECT item_id, item_name, item_picture, owner_id, 'Omistaja' AS match_origin, owner_username AS match_value
            FROM base_items
            WHERE owner_username LIKE ?

            UNION ALL

            SELECT item_id, item_name, item_picture, owner_id, 'Tavaran nimi', item_name
            FROM base_items
            WHERE item_name LIKE ?

            UNION ALL

            SELECT item_id, item_name, item_picture, owner_id, 'Sijainti', item_location
            FROM base_items
            WHERE item_location LIKE ?

            UNION ALL

            SELECT item_id, item_name, item_picture, owner_id, 'Kommentti', item_comment
            FROM base_items
            WHERE item_comment LIKE ?

            UNION ALL

            SELECT i.item_id, i.item_name, i.item_picture, i.owner_id, 'Ominaisuudet', c.characteristic_value
            FROM base_items i
            JOIN characteristics c ON i.item_id = c.item_id
            WHERE c.characteristic_value LIKE ?

            UNION ALL

            SELECT i.item_id, i.item_name, i.item_picture, i.owner_id, 'Luokitellut', clk.classification_name
            FROM base_items i
            JOIN classifications cl ON i.item_id = cl.item_id
            JOIN classification_keys clk ON cl.classification_keys_id = clk.classification_keys_id
            WHERE clk.classification_name LIKE ?
        ),
        first_ids AS (
            SELECT DISTINCT item_id
            FROM matches
            ORDER BY item_id ASC
            LIMIT ? OFFSET ?
        )
        SELECT m.*, b.borrower_id
        FROM matches m
        LEFT JOIN borrowings b ON m.item_id = b.item_id
        JOIN first_ids f ON m.item_id = f.item_id
        ORDER BY m.item_id ASC;
    """
    query_pattern = f"%{query}%"
    limit = page_size + 1
    offset = page_size * (page - 1)

    results = db.query(sql, [query_pattern] * 6 + [limit, offset])
    items_dict = {}

    for (
        item_id,
        item_name,
        item_picture,
        owner_id,
        match_origin,
        match_value,
        borrower_id,
    ) in results:
        picture_b64 = picture_converter(item_picture)
        if match_origin in ("Kommentti", "Sijainti", "Ominaisuudet"):
            match_value = formatter(query, match_value)
        if item_id not in items_dict:
            items_dict[item_id] = (
                {
                    "item_id": item_id,
                    "item_name": item_name,
                    "item_picture": picture_b64,
                    "owner_id": owner_id,
                    "borrower_id": borrower_id,
                },
                {}
            )
        _, matches = items_dict[item_id]
        if match_origin != "Tavaran nimi":
            matches.setdefault(match_origin, []).append(match_value)

    return list(items_dict.values())

def item_page_data(item_id):
    sql ="""
        SELECT i.item_name,
               i.owner_id,
               i.item_location,
               i.item_picture,
               i.item_comment,
               u_owner.username AS owner_username,
               u_borrower.username AS borrower_username,
               b.borrow_time
        FROM items i
        JOIN users u_owner ON i.owner_id = u_owner.user_id
        LEFT JOIN borrowings b ON i.item_id = b.item_id
        LEFT JOIN users u_borrower ON b.borrower_id = u_borrower.user_id
        WHERE i.item_id = ?
    """
    (
        item_name,
        owner_id,
        item_location,
        item_picture,
        item_comment,
        owner_username,
        borrower_username,
        borrow_time
     ) = db.query(sql,[item_id])[0]
    picture_b64 = picture_converter(item_picture)
    borrow_date = None
    borrow_clock = None
    if borrow_time:
        borrow_date, borrow_clock = borrow_time.split(' ')
        borrow_date = (
            datetime.strptime(borrow_date, "%Y/%m/%d")
            .strftime("%d/%m/%Y")
        )
    return {
        "item_name": item_name,
        "owner_id": owner_id,
        "item_location": item_location,
        "item_picture": picture_b64,
        "item_comment": item_comment,
        "owner_username": owner_username,
        "borrower_username": borrower_username,
        "borrow_clock": borrow_clock,
        "borrow_date": borrow_date,
    }
