import psycopg2

DB_CONFIG = {
    "host": "34.81.249.186",
    "port": 5432,
    "database": "linebot_db",
    "user": "root",
    "password": "justin0706"
}


create_sql = """ALTER TABLE users ADD COLUMN default_book_id INTEGER;"""

# create_sql = """
# CREATE TABLE IF NOT EXISTS users (
#     id SERIAL PRIMARY KEY,
#     line_user_id TEXT UNIQUE NOT NULL,
#     display_name TEXT,
#     created_at TIMESTAMP DEFAULT NOW()
# );

# CREATE TABLE IF NOT EXISTS books (
#     id SERIAL PRIMARY KEY,
#     user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
#     name TEXT NOT NULL,
#     created_at TIMESTAMP DEFAULT NOW()
# );

# CREATE TABLE IF NOT EXISTS ledger_entries (
#     id SERIAL PRIMARY KEY,
#     book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
#     entry_type TEXT CHECK (entry_type IN ('收入', '支出')),
#     description TEXT,
#     amount NUMERIC NOT NULL,
#     url TEXT,
#     created_at TIMESTAMP DEFAULT NOW()
# );
# """

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(create_sql)
    conn.commit()
    print("✅ 資料表已成功建立！")
except Exception as e:
    print("❌ 建立資料表失敗：", e)
finally:
    if conn:
        conn.close()
