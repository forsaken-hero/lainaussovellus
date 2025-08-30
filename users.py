import base64
from werkzeug.security import check_password_hash, generate_password_hash
import db

def picture_converter(data):
    if data:
        return base64.b64encode(data).decode("utf-8")
    return None

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])
    return db.last_insert_id()

def check_login(username, password):
    sql = "SELECT user_id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if len(result) == 1:
        user_id, password_hash = result[0]
        if check_password_hash(password_hash, password):
            return user_id
    return None

def username(user_id):
    sql = "SELECT username FROM users WHERE user_id = ?"
    return db.query(sql, [user_id])[0][0]

def user_id_picture(user):
    sql = "SELECT user_id, user_picture FROM users WHERE username = ?"
    id, user_picture = db.query(sql, [user])[0]
    picture_b64 = picture_converter(user_picture)
    return [id, picture_b64]

def user_picture(user_id):
    sql = "SELECT user_picture FROM users WHERE user_id = ?"
    row = db.query(sql, [user_id])[0][0]
    picture = picture_converter(row)
    return picture

def has_no_picture(user_id):
    sql = """
        SELECT user_picture IS NULL AS has_no_picture
        FROM users 
        WHERE user_id = ?
    """
    return db.query(sql, [user_id])[0][0]

def user_id(user):
    sql = "SELECT user_id FROM users WHERE username = ?"
    return db.query(sql, [user])[0][0]

def upload_picture(user_id, user_picture=None):
    sql = "UPDATE users SET user_picture = ? WHERE user_id = ?"
    db.execute(sql, [user_picture, user_id])

def remove_picture(user_id):
    sql = "UPDATE users SET user_picture = NULL WHERE user_id = ?"
    db.execute(sql,[user_id])
