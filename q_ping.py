import sqlite3

conn = sqlite3.connect('ex.db')
c = conn.cursor()

c.execute("SELECT * FROM result")
rows = c.fetchall()
for row in rows:
    print row
