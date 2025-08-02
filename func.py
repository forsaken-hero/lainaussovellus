from werkzeug.security import check_password_hash, generate_password_hash
import db, itertools

def create_user(username, password, picture = None, administrator = 0):
    print("func.py's create_user called")
    password_hash = generate_password_hash(password)
    sql = f"INSERT INTO users VALUES (NULL, '{username}', '{password_hash}', '{picture}', {administrator})"
    print("func.py's create_user sql command created. sql = ",sql)
    db.execute(sql)
    print("func.py's create_user successful successful, returning user_id")
    return db.last_insert_id()

def check_login(username, password):
    print("func.py's check_login called")
    sql = f"SELECT id, password_hash FROM users WHERE username = '{username}'"
    result = db.query(sql)

    if len(result) == 1:
        user_id, password_hash = result[0]
        if check_password_hash(password_hash, password):
            print("func.py's check_login password check successful, returnin user_id")
            return user_id

    return None


def available_items():
    print("func.py's available_items called")    
    sql = "SELECT * FROM items"
    out = []
    for data in db.query(sql): out.append(data)
    print("func.py's available_items data transfer succeeded, returning", out)    
    return out


def upload_item(item_name, owner, picture = None, comment = None):
    print("func.py's upload_item called")
    sql = f"INSERT INTO items VALUES (NULL, '{item_name}', '{owner}', '{picture}', '{comment}')"
    print("func.py's upload_item sql command created. sql = ",sql)
    db.execute(sql)
    item_id = db.last_insert_id()
    print("func.py's upload uploaded onto table items with values",[item_name, owner, picture, comment],"returning item_id")
    return item_id

def upload_classifications(item_id,classification_keys_id_list):
    print("func.py's upload_classifications called")
    classifications_ids = []
    sql = "INSERT INTO classifications VALUES ?"
    for data in classification_keys_id_list:
        db.execute(f"INSERT INTO classifications VALUES (NULL, '{item_id}', '{data}')")
        classifications_ids.append(db.last_insert_id())    
        print("func.py's for, upload onto classifications table success, with sql",sql,"classifications_ids now",classifications_ids) 
    return classifications_ids

def classification_keys():
    print("func.py's classification_keys called")
    sql = "SELECT * FROM classification_keys"
    out = []
    for data in db.query(sql): out.append(data)
    print("func.py's classification_keys done, returning", out)
    return out

def item_data(item_id):
    print("func.py's item_data called")    
    sql = f"SELECT * FROM items WHERE id = '{item_id}'"    
    out = db.query(sql)[0]
    print("func.py's item_data done, returning", out)
    return out


def item_classifications(item_id): #returns list of integers
    print("func.py's item_classifications called")
    sql = f"SELECT classification_keys_id FROM classifications WHERE item_id = '{item_id}'"
    out = []
    for data in db.query(sql): out.append(data[0])
    print("func.py's item_classifications done, returning", out)
    return out

def delete_classifications(item_id):
    print("func.py's delete_classifications called")
    sql = f"DELETE FROM classifications WHERE item_id = '{item_id}'"
    db.execute(sql)
    print("func.py's delete_classifications done")

def table_columns(table_name):
    print("func.py's table_data",table_name," called")    
    sql = f"SELECT name FROM PRAGMA_TABLE_INFO ('{table_name}')"
    print("func.py's table_columns sql command created. sql = ",sql)
    out = list(itertools.chain.from_iterable(db.query(sql)))
    print("func.py's table_columns database query success. Outputting",out)
    return out


def edit_item(item_id, item_name, owner, picture = None, comment = None):
    print("func.py's edit_item called")
    data_change = [item_name, owner, picture, comment]
    columns = table_columns('items')[1:]
    set_command = ""

    for index in range(len(columns)):
        add = f"{columns[index]} = '{data_change[index]}', "
        set_command += add
    set_command = set_command[:-2]
    sql = f"UPDATE items SET {set_command} WHERE id = {item_id}"
    print("func.py's edit_item sql command created. sql = ",sql)
    db.execute(sql)
    print("func.py's edit_item done")