from werkzeug.security import check_password_hash, generate_password_hash
import db
def create_user(username, password, picture = None, administrator = 0):
    print("users.py's create_user called")
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash, user_picture, administrator) VALUES (?, ?, ?, ?)"
    db.execute(sql,[username,password_hash,picture,administrator])
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