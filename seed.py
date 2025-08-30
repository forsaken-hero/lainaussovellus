import random
import sqlite3
from datetime import datetime, timedelta

db = sqlite3.connect("database.db")
USER_COUNT= 100
BORROWING_COUNT = 10**6
ITEM_COUNT = 10**7
available = []
PASSWORD_HASH = 'scrypt:32768:8:1$rn3cIYeZ0d7o6ROq$e2afd9sdjlkjljwlennaasdji8564365e593a073a2426af2730323e74a3fb8ee965891556762c67a15fa138152dfe234hjvjhsdjhk4456e2aa9d08c94e101932'
ITEM_LOCATION = "l1"
start_time = datetime(1000, 1, 1, 0, 0)

users = [("usertest" + str(i), PASSWORD_HASH) for i in range(1, USER_COUNT + 1)]
db.executemany("INSERT INTO users (username, password_hash) VALUES (?, ?)", users)
print("users done")

items = [("itemtest" + str(i), random.randint(1, USER_COUNT), ITEM_LOCATION)
         for i in range(1, ITEM_COUNT + 1)]
db.executemany("""INSERT INTO items (item_name, owner_id, item_location)
                  VALUES (?, ?, ?)""", items)
print("items done")

borrowed_items = random.sample(range(1, ITEM_COUNT + 1), BORROWING_COUNT)
borrowings = [
    (
        item_id,
        random.randint(1, USER_COUNT),
        (start_time + timedelta(minutes=i)).strftime("%Y/%m/%d %H:%M")
    )
    for i, item_id in enumerate(borrowed_items)
]
db.executemany("""INSERT INTO borrowings (item_id, borrower_id, borrow_time)
                  VALUES (?, ?, ?)""", borrowings)
print("borrowings done")

db.commit()
db.close()
