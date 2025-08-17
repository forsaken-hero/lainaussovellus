
import sqlite3
from flask import g

DATABASE = "database.db"

def get_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.row_factory = sqlite3.Row
    return g.db

def execute(sql, params=[], con = None):
    print("db.py's execute starts")
    if con == None:
        con = get_connection()
        result = con.execute(sql, params)
        con.commit()
    else: 
        result = con.execute(sql,params)
    g.last_insert_id = result.lastrowid
    print("db.py's execute succeeded returning last_insert_id",g.last_insert_id, "& con=",con)
    return g.last_insert_id, con


def commit(con):
    con.commit()

def query(sql, params=[]):
    con = get_connection()
    return con.execute(sql, params).fetchall()

def last_insert_id():
    return g.last_insert_id

def close_connection(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

'''
def multi_execute(sql, params=[], con = None): #returning the last insert id & connection
    print("db.py's multi_execute starts")
    if con == None: print("con == None!");con = get_connection()
    print("trying to execute")
    result = con.execute(sql,params)
    g.last_insert_id = result.lastrowid
    print("db.py's multi_execute succeeded, returning con=",con,"& last_insert_id",g.last_insert_id)
    return g.last_insert_id , con

'''