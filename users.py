from werkzeug.security import check_password_hash, generate_password_hash
import db, app, base64

def picture_converter(data):
    if data:  return base64.b64encode(data).decode("utf-8")
    return None

def create_user(username, password):
    print("users.py's create_user called")
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql,[username,password_hash])
    print("users.py's create_user successful successful, returning user_id")
    return db.last_insert_id()

def check_login(username, password):
    print("users.py's check_login called")
    sql = "SELECT user_id, password_hash FROM users WHERE username = ?"
    result = db.query(sql,[username])

    if len(result) == 1:
        user_id, password_hash = result[0]
        if check_password_hash(password_hash, password):
            print("users.py's check_login password check successful, returnin user_id")
            return user_id

    return None

def username(user_id):
    print("users.py's username called, for user_id",user_id)
    sql = "SELECT username FROM users WHERE user_id = ?"
    out = db.query(sql,[user_id])[0][0]
    print("users.py's username success, returning", out)
    return out

def user_id_picture(user):
    print("users.py's user_id_picture called for user", user)
    sql = "SELECT user_id, user_picture FROM users WHERE username = ?"
    id, user_picture = db.query(sql, [user])[0]
    picture_b64 = picture_converter(user_picture)
    out = [id, picture_b64]
    print("users.py's user_id_picture done, returning", out)
    return out

def user_id(user):
    print("users.py's user_id called for user", user)
    sql = "SELECT user_id FROM users WHERE username = ?"
    id = db.query(sql, [user])[0][0]
    print("users.py's user_id done, returning", id)
    return id

def upload_picture(user_id, user_picture = None):
    print("users.py's upload_picture called for user_id", user_id, "picture to be uploaded ", user_picture) 
    sql = "UPDATE users SET user_picture = ? WHERE user_id = ?"
    db.execute(sql,[user_picture,user_id])
    print("forum.py's update_item done")    