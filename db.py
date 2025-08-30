import sqlite3
from flask import g

DATABASE = "database.db"

def get_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.row_factory = sqlite3.Row
    return g.db

def execute(sql, params=[], con=None):
    if con is None:
        con = get_connection()
        result = con.execute(sql, params)
        con.commit()
    else:
        result = con.execute(sql,params)
    g.last_insert_id = result.lastrowid
    return g.last_insert_id, con

def commit(con):
    con.commit()

def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    return result

def last_insert_id():
    return g.last_insert_id

def close_connection(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
