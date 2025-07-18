import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

query_sql = """
SELECT 
  u.id AS user_id,
  u.line_user_id,
  u.display_name,
  u.created_at,
  b.id AS book_id,
  b.name AS book_name,
  b.created_at AS book_created_at
FROM users u
LEFT JOIN books b ON u.default_book_id = b.id
ORDER BY u.created_at;
"""

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(query_sql)
    results = cur.fetchall()

    for row in results:
        user_id, line_user_id, name, created_at, book_id, book_name, book_created = row
        if book_id:
            print(f"✅ 用戶 {name}（{line_user_id}）的預設帳本是「{book_name}」，建立於 {book_created}")
        else:
            print(f"⚠️ 用戶 {name}（{line_user_id}）尚未設定預設帳本（建立於 {created_at}）")
except Exception as e:
    print("❌ 查詢失敗：", e)
finally:
    if conn:
        conn.close()
