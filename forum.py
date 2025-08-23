
import db, itertools, datetime, users, app, base64


def available_items(page = 1, page_size = 10):
    print("forum.py's available_items called")    
    sql = """SELECT i.item_id, 
                    i.item_name, 
                    i.owner_id, 
                    i.item_picture 
            FROM items i 
            WHERE i.item_id 
            NOT IN (SELECT b.item_id FROM borrowings b)
            ORDER BY i.item_id ASC
            LIMIT ? OFFSET ?
            """
    out = []
    limit = page_size
    offset = page_size * (page - 1)
    for data in db.query(sql,[limit, offset]):
        item_id, item_name, owner_id, item_picture = data
        picture_b64 = app.picture_converter(item_picture)
        out.append([item_id, item_name, owner_id, picture_b64])
    print("forum.py's available_items data transfer succeeded, returning", out)    
    return out

def available_items_count():
    print("forum.py's available_items_call called")
    sql = "SELECT COUNT(*) FROM items i WHERE i.item_id NOT IN (SELECT b.item_id FROM borrowings b)"
    out = db.query(sql)[0][0]
    print("forum.py's available_items_count data transfer succeeded, returning", out)    
    return out    

def borrowed_items(page = 1, page_size = 10):#indexes 0=item_id, 1=item_name, 2=owner_id, 3=item_picture, 4=borrower_id, 5 = borrow_clock, 6 = borrow_day, 7 = borrower_username
    print("forum.py's borrowed_items called")    
    sql = """SELECT i.item_id,  
                    i.item_name, 
                    i.owner_id, 
                    i.item_picture, 
                    b.borrower_id, 
                    b.borrow_time, 
                    u.username AS borrower_username 
            FROM items i 
            JOIN borrowings b ON i.item_id = b.item_id 
            JOIN users u ON u.user_id = b.borrower_id
            ORDER BY i.item_id ASC
            LIMIT ? OFFSET ?
            """
    out = []
    limit = page_size
    offset = page_size * (page - 1)
    for data in db.query(sql, [limit, offset]): 
        item_id, item_name, owner_id, item_picture, borrower_id, borrow_time, borrower_username = data
        borrow_clock, borrow_day = borrow_time.split(' ')
        picture_b64 = app.picture_converter(item_picture)
        out.append([item_id, item_name, owner_id, picture_b64, borrower_id, borrow_clock, borrow_day, borrower_username])

    print("forum.py's borrowed_items data transfer succeeded, returning", out)    
    return out

def borrowed_items_count():
    print("forum.py's borrowed_items_count called")
    sql = "SELECT COUNT(*) FROM items i WHERE i.item_id IN (SELECT b.item_id FROM borrowings b)"
    out = db.query(sql)[0][0]
    print("forum.py's borrowed_items_count data transfer succeeded, returning", out)    
    return out    

def user_uploads(owner_id, page = 1, page_size = 10):
    print("forum.py's user_uploads called")    
    sql = """SELECT item_id, 
                    item_name, 
                    owner_id,
                    item_picture 
            FROM items 
            WHERE owner_id = ? 
            ORDER BY item_id ASC
            LIMIT ? OFFSET ?
            """
    out = []
    limit = page_size
    offset = page_size * (page - 1)
    for data in db.query(sql,[owner_id, limit, offset]):
        item_id, item_name, owner_id, item_picture = data
        picture_b64 = app.picture_converter(item_picture)
        out.append([item_id, item_name, owner_id, picture_b64])
    print("forum.py's user_uploads data transfer succeeded, returning", out)    
    return out

def user_uploads_count(owner_id):
    print("forum.py's user_uploads_count called")
    sql = "SELECT COUNT(*) FROM items WHERE owner_id = ?"
    out = db.query(sql, [owner_id])[0][0]
    print("forum.py's user_uploads_count data transfer succeeded, returning", out)
    return out

def is_borrowed(item_id):
    print("forum.py's is_borrowed called")
    sql = "SELECT EXISTS (SELECT 1 FROM borrowings WHERE item_id = ?) AS has_borrowing;"
    if db.query(sql,[item_id])[0][0] == 1: print("forum.py's is_borrowed query succeeded, returning 1"); return 1
    print("forum.py's is_borrowed query succeeded, returning None")
    return None

def insert_item(item_name, owner_id, item_picture = None, item_comment = None, con = None):
    print("forum.py's insert_item called")
    sql = "INSERT INTO items (item_name, owner_id, item_picture, item_comment) VALUES (?, ?, ?, ?)"
    item_id, con = db.execute(sql,[item_name,owner_id,item_picture, item_comment],con)
    print("forum.py's insert_item succeeded")
    return item_id, con

def insert_classifications(item_id, classifications = [], con = None):
    print("forum.py's insert_classifications called")
    sql = "INSERT INTO classifications (item_id, classification_keys_id) VALUES (?, ?)"
    for data in classifications:    
        db.execute(sql,[item_id,data], con)
        print("forum.py's insert_classifications upload onto classifications table for classification_key_id", data," success")
    print("forum.py's insert_classifications done")

def insert_characteristics(item_id, characteristics = {}, con = None):
    print("forum.py's insert_characteristics called")
    sql = "INSERT INTO characteristics (item_id, characteristic_keys_id, characteristic_value) VALUES (?, ?, ?)"
    for data in characteristics:
        db.execute(sql, [item_id,data,characteristics[data]], con)          
        print("forum.py's insert_characteristics for, upload onto characteristics table for data",data,",",characteristics[data]," succeeded")
    print("forum.py's insert_characteristics done")

def upload_item(item_name, owner_id, item_picture = None, item_comment = None, classifications = [], characteristics = {}):
    print("forum.py's upload_item called")

    con = db.get_connection()
    print("forum.py's upload_item connection made")

    item_id, con2 = insert_item(item_name, owner_id, item_picture, item_comment, con)
    insert_classifications(item_id, classifications, con)
    insert_characteristics(item_id, characteristics, con)
 
    con.commit()
    '''
    try:
        print("forum.py's upload_item try starts")
        con, item_id = db.multi_execute(sql = items_sql,params = [item_name,owner_id,item_picture, item_comment], con = con)
        print("forum.py's upload_item uploaded onto table items with values",[item_name, owner_id, item_picture, item_comment],"returning item_id")

        for data in classifications:    
            con, id = db.multi_execute(sql = classifications_sql, params = [item_id,data], con = con)
            print("forum.py's upload_item for, upload onto classifications table for classification_key_id", data," success")

        for data in characteristics:
            con, id = db.multi_execute(sql = characteristics_sql, params = [item_id,data,characteristics[data]], con = con)          
            print("forum.py's upload_item for, upload onto characteristics table for data",data,",",characteristics[data]," succeeded")
        
        con.commit()
    except:
        con.rollback()
        raise Exception("Failed to execute SQL statement")
    '''
    print("forum.py's upload_item done, returning item_id =",item_id)
    return item_id

def update_item(item_id, item_name, item_picture = None, item_comment = None, con = None):
    print("forum.py's update_item called")
    sql = "UPDATE items SET item_name = ?, item_picture = ?, item_comment = ? WHERE item_id = ?"
    db.execute(sql,[item_name,item_picture,item_comment,item_id], con)
    print("forum.py's update_item done")


def delete_classifications(item_id, con = None):
    print("forum.py's delete_classifications called")
    sql = "DELETE FROM classifications WHERE item_id = ?"
    db.execute(sql,[item_id],con)
    print("forum.py's delete_classifications done")

def delete_characteristics(item_id,con = None):
    print("forum.py's delete_characteristics called")
    sql = "DELETE FROM characteristics WHERE item_id = ?"
    db.execute(sql,[item_id],con)
    print("forum.py's delete_classifications done")


def edit_item(item_id, item_name, item_picture = None, item_comment = None, classifications = [], characteristics = {}):
    print("forum.py's edit_item called")

    con = db.get_connection()
    delete_classifications(item_id, con)
    delete_characteristics(item_id,con)
    update_item(item_id, item_name, item_picture , item_comment, con)
    insert_classifications(item_id, classifications, con)
    insert_characteristics(item_id, characteristics, con)
    con.commit()

    print("forum.py's edit_item done")

def remove_item(item_id):
    print("forum.py's remove_item called")
    sql = "DELETE FROM items WHERE item_id = ?"
    db.execute(sql,[item_id])
    print("forum.py's remove_item succeed")

def classification_keys(): #returns dictionary of the id: classification_name
    print("forum.py's classification_keys called")
    sql = "SELECT classification_keys_id, classification_name FROM classification_keys"
    out = {}
    for data in db.query(sql): out[data[0]] = data[1]
    print("forum.py's classification_keys done, returning", out)
    return out

def characteristic_keys(): #returns dictionary of the id: characteristic_name
    print("forum.py's characteristic_keys called")
    sql = "SELECT characteristic_keys_id, characteristic_name FROM characteristic_keys"
    out = {}
    for data in db.query(sql): out[data[0]] = data[1]
    print("forum.py's characteristic_keys done, returning", out)
    return out


def item_data(item_id): #0 = item_name, 1 = item_picture, 2 = item_comment
    print("forum.py's item_data called, enquiring for item_id",item_id)    
    sql = "SELECT item_name, item_picture, item_comment FROM items WHERE item_id = ?"
    out = db.query(sql,[item_id])[0]
    print("forum.py's item_data done, returning", out)
    return out

def item_data_full(item_id): #0 = item_name, 1= owner_id, 2 = item_picture, 3 = item_comment
    print("forum.py's item_data_full called, enquiring for item_id",item_id)
    sql = "SELECT item_name, owner_id, item_picture, item_comment FROM items WHERE item_id = ?"
    out = db.query(sql,[item_id])[0]
    print("forum.py's item_data_full done, returning", out)
    return out

def item_owner_id(item_id):
    print("forum.py's item_owner_id called, enquiring for item_id",item_id)    
    sql = "SELECT owner_id FROM items WHERE item_id = ?"
    out = db.query(sql,[item_id])[0][0]
    print("forum.py's item_owner_id done, returning", out)
    return out

def item_picture(item_id):
    print("forum.py's item_picture called,enquiring for item_id",item_id)    
    sql = "SELECT item_picture FROM items WHERE item_id = ?"
    out = db.query(sql,[item_id])[0][0]
    print("forum.py's item_picture done, returning", out)
    return out

def item_name(item_id):
    print("forum.py's item_name called,enquiring for item_id",item_id)    
    sql = "SELECT item_name FROM items WHERE item_id = ?"
    out = db.query(sql,[item_id])[0][0]
    print("forum.py's item_name done, returning", out)
    return out

def item_classifications(item_id): #returns list of integers
    print("forum.py's item_classifications called")
    sql = "SELECT classification_keys_id FROM classifications WHERE item_id = ?"
    out = []
    for data in db.query(sql,[item_id]): out.append(data[0])
    print("forum.py's item_classifications done, returning", out)
    return out

def item_characteristics(item_id): #returning a dictionary of the item_characteristics
    print("forum.py's item_characteristics called")
    sql = "SELECT characteristic_keys_id, characteristic_value FROM characteristics WHERE item_id = ?"
    out = {}
    for data in db.query(sql,[item_id]): out[data[0]] = data[1]
    print("forum.py's item_characteristics done, returning", out)
    return out

def borrow_item(item_id, borrower_id):
    print("forum.py's borrow_item called for item_id",item_id)    
    sql = "INSERT INTO borrowings (item_id, borrower_id, borrow_time) VALUES (?, ?, ?)"
    borrowings_id, con = db.execute(sql,[item_id,borrower_id,str(datetime.datetime.now().strftime("%H:%M %d/%m/%Y"))])
    print("forum.py's borrow_item done, with borrowings_id", borrowings_id)
    return borrowings_id    

def borrower_id(item_id):
    print("forum.py's borrower_id called, enquiring for item_id",item_id)    
    sql = "SELECT borrower_id FROM borrowings WHERE item_id = ?"
    out = db.query(sql,[item_id])[0][0]
    print("forum.py's borrower_id done, returning", out)
    return out

def return_item(item_id):
    print("forum.py's return_item called for item_id",item_id)    
    sql = "DELETE FROM borrowings WHERE item_id = ?"
    db.execute(sql,[item_id])
    print("forum.py's return_item succeeded")

#add picture here later!
def search(query, page = 1, page_size = 10): #printing forum.search('h') {(1, 'kossu'): {'Ominaisuudet': ['alkoholia']}, (2, 'vissy'): {'Luokkitellut': ['sähköiset']}, (4, 'rikki flyygeli'): {'Ominaisuudet': ['huono'], 'Luokkitellut': ['sähköiset']}, (5, 'tuhottu auto'): {'Ominaisuudet': ['ylihuono']}, (9, 'palava mies'): {'Ominaisuudet': ['liha', 'lyhyt']}, (10, 'haha'): {'Kommentti': ['hah???']}, (11, 'heeh'): {'Omistaja': ['haha']}}
    print("forum.py's search called for query",query)
    sql = """WITH matches AS (
        SELECT i.item_id, i.item_name, i.item_picture, 'Omistaja' AS match_origin, u.username AS match_value
        FROM users u
        JOIN items i ON u.user_id = i.owner_id
        WHERE u.username LIKE ?

        UNION ALL

        SELECT i.item_id, i.item_name, i.item_picture, 'Tavaran nimi' AS match_origin, i.item_name AS match_value 
        FROM users u
        JOIN items i ON u.user_id = i.owner_id
        WHERE i.item_name LIKE ?

        UNION ALL

        SELECT i.item_id, i.item_name, i.item_picture, 'Kommentti' AS match_origin, i.item_comment AS match_value
        FROM users u
        JOIN items i ON u.user_id = i.owner_id
        WHERE i.item_comment LIKE ?

        UNION ALL

        SELECT i.item_id, i.item_name, i.item_picture, 'Ominaisuudet' AS match_origin, c.characteristic_value AS match_value
        FROM users u
        JOIN items i ON u.user_id = i.owner_id
        JOIN characteristics c ON i.item_id = c.item_id
        WHERE c.characteristic_value LIKE ?

        UNION ALL

        SELECT i.item_id, i.item_name, i.item_picture, 'Luokitellut' AS match_origin, clk.classification_name AS match_value
        FROM users u
        JOIN items i ON u.user_id = i.owner_id
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
    SELECT m.*
    FROM matches m
    JOIN first_ids f ON m.item_id = f.item_id
    ORDER BY m.item_id ASC;
    """
    que = "%" + query + "%"
    limit = page_size + 1
    offset = page_size * (page - 1)
    results = db.query(sql, [que,que,que,que,que,limit,offset])
    out = {}
    for result in results:
        item_id = result[0]; item_name = result[1]; item_picture = result[2]; match_origin = result[3]; match_value = result[4]
        picture_b64 = app.picture_converter(item_picture)
        key = (item_id, item_name, picture_b64)
        if key not in out: #if the item_id not yet in out
            print("(item_id, item_name, picture_b64)",key," not yet in out, out now",out)
            out[key] = {}
            if match_origin != "Tavaran nimi": out[key].update({match_origin:[match_value]})

            print("line 269 done, out now",out)
        else: #if the item_id already in out
            print("(item_id, item_name, picture_b64)",key," already in out, out now",out)
            if match_origin == "Tavaran nimi":
                print("no need to record, continue!")
                continue
            if match_origin not in out[key]: #if the match_origin not yet in 
                print("match_origin not yet in, out now",out)
                out[key].update({match_origin:[match_value]})
                print("line275 done, out now",out)
            else: #if the match_origin already in
                print("match origin already in, out now", out)
                out[key][match_origin].append(match_value)
                print("line279 done, out now",out)

    print("forum.py's search succeeded, returning",out)
    return out


def table_columns(table_name): ##############is this needed?
    print("forum.py's table_data",table_name," called")    
    sql = "SELECT name FROM PRAGMA_TABLE_INFO (?)"
    print("forum.py's table_columns sql command created. sql = ",sql)
    out = list(itertools.chain.from_iterable(db.query(sql,[table_name])))
    print("forum.py's table_columns database query success. Outputting",out)
    return out



'''
result should be 
{1: {'Tavaran nimi': 'kossu', 'Ominaisuudet': ['alkoholia']}, 2: {'Tavaran nimi': 'vissy', 'Luokkitellut': ['sähköiset']}, 4: {'Tavaran nimi': 'rikki flyygeli', 'Ominaisuudet': ['huono'], 'Luokkitellut': ['sähköiset']}, 5: {'Tavaran nimi': 'tuhottu auto', 'Ominaisuudet': ['ylihuono']}, 9: {'Tavaran nimi': 'palava mies', 'Ominaisuudet': ['liha', 'lyhyt']}, 10: {'Tavaran nimi': 'haha', 'Kommentti': ['hah???']}, 11: {'Tavaran nimi': 'heeh', 'Omistaja': ['haha']}}
dev printing forum.search('h')[0][0], value is 1
dev printing forum.search('h')[0][1], value is kossu
dev printing forum.search('h')[0][2], value is Tavaran Ominaisuudet
dev printing forum.search('h')[0][3], value is alkoholia
dev printing forum.search('h')[1][0], value is 2
dev printing forum.search('h')[1][1], value is vissy
dev printing forum.search('h')[1][2], value is Tavaran Luokkitellut
dev printing forum.search('h')[1][3], value is sähköiset
dev printing forum.search('h')[2][0], value is 4
dev printing forum.search('h')[2][1], value is rikki flyygeli
dev printing forum.search('h')[2][2], value is Tavaran Ominaisuudet
dev printing forum.search('h')[2][3], value is huono
dev printing forum.search('h')[3][0], value is 4
dev printing forum.search('h')[3][1], value is rikki flyygeli
dev printing forum.search('h')[3][2], value is Tavaran Luokkitellut
dev printing forum.search('h')[3][3], value is sähköiset
dev printing forum.search('h')[4][0], value is 5
dev printing forum.search('h')[4][1], value is tuhottu auto
dev printing forum.search('h')[4][2], value is Tavaran nimi
dev printing forum.search('h')[4][3], value is tuhottu auto
dev printing forum.search('h')[5][0], value is 5
dev printing forum.search('h')[5][1], value is tuhottu auto
dev printing forum.search('h')[5][2], value is Tavaran Ominaisuudet
dev printing forum.search('h')[5][3], value is ylihuono
dev printing forum.search('h')[6][0], value is 9
dev printing forum.search('h')[6][1], value is palava mies
dev printing forum.search('h')[6][2], value is Tavaran Ominaisuudet
dev printing forum.search('h')[6][3], value is liha
dev printing forum.search('h')[7][0], value is 9
dev printing forum.search('h')[7][1], value is palava mies
dev printing forum.search('h')[7][2], value is Tavaran Ominaisuudet
dev printing forum.search('h')[7][3], value is lyhyt
dev printing forum.search('h')[8][0], value is 10
dev printing forum.search('h')[8][1], value is haha
dev printing forum.search('h')[8][2], value is Tavaran nimi
dev printing forum.search('h')[8][3], value is haha
dev printing forum.search('h')[9][0], value is 10
dev printing forum.search('h')[9][1], value is haha
dev printing forum.search('h')[9][2], value is Tavaran kommentti
dev printing forum.search('h')[9][3], value is hah???
dev printing forum.search('h')[10][0], value is 11
dev printing forum.search('h')[10][1], value is heeh
dev printing forum.search('h')[10][2], value is Omistaja
dev printing forum.search('h')[10][3], value is haha
dev printing forum.search('h')[11][0], value is 11
dev printing forum.search('h')[11][1], value is heeh
dev printing forum.search('h')[11][2], value is Tavaran nimi
dev printing forum.search('h')[11][3], value is heeh


def edit_item(item_id, item_name, owner_id, item_picture = None, item_comment = None):
    print("forum.py's edit_item called")
    data_change = [item_name, owner_id, item_picture, item_comment]
    columns = ['item_name', 'owner_id', 'item_picture', 'item_comment']
    set_command = ""

    for index in range(len(columns)):
        add = f"{columns[index]} = '{data_change[index]}', "
        set_command += add
    set_command = set_command[:-2]
    sql = "UPDATE items SET ? WHERE id = ?"
    print("forum.py's edit_item sql command created. sql = ",sql,". set_command = ",set_command,". item_id = ", item_id)
    db.execute(sql,[set_command,item_id])
    print("forum.py's edit_item done")
'''