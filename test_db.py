from database.db import get_connection, init_db

init_db()
print("Tables initialized.")

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name FROM sysobjects WHERE xtype='U' AND name IN ('datasets','queries')")
tables = [r[0] for r in cursor.fetchall()]
print("Tables found:", tables)
cursor.close()
conn.close()