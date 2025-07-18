import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta, timezone
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

def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print("❌ 無法連接資料庫：", e)
        return None

# ===== 使用者相關 =====

def get_or_create_user(line_user_id, display_name=None):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            # 確保只查一次 user，不創新
            cur.execute("SELECT id FROM users WHERE line_user_id = %s;", (line_user_id,))
            result = cur.fetchone()
            if result:
                return result[0]
            # ✅ 不存在才建立（這段是舊邏輯）
            cur.execute("""
                INSERT INTO users (line_user_id, display_name) VALUES (%s, %s)
                RETURNING id;
            """, (line_user_id, display_name))
            conn.commit()
            return cur.fetchone()[0]
    except Exception as e:
        print("❌ 建立或取得使用者失敗：", e)
        return None
    finally:
        conn.close()


def user_exists(line_user_id):
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE line_user_id = %s;", (line_user_id,))
            return cur.fetchone() is not None
    except Exception as e:
        print("❌ 查詢使用者失敗：", e)
        return False
    finally:
        conn.close()

# ===== 帳本相關 =====

def get_or_create_default_book(user_id):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM books WHERE user_id = %s AND name = %s;", (user_id, "預設帳本"))
            result = cur.fetchone()
            if result:
                return result[0]
            cur.execute("""
                INSERT INTO books (user_id, name) VALUES (%s, %s)
                RETURNING id;
            """, (user_id, "預設帳本"))
            conn.commit()
            return cur.fetchone()[0]
    except Exception as e:
        print("❌ 建立或取得帳本失敗：", e)
        return None
    finally:
        conn.close()

def get_books_by_user(line_user_id):
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT b.id, b.name
                FROM books b
                JOIN users u ON b.user_id = u.id
                WHERE u.line_user_id = %s
                ORDER BY b.created_at ASC;
            """, (line_user_id,))
            return cur.fetchall()
    except Exception as e:
        print("❌ 查詢帳本失敗：", e)
        return []
    finally:
        conn.close()

# ===== 記帳項目相關 =====

def insert_entry(line_user_id, entry_type, description, amount, url=None, display_name=None):
    try:
        user_id = get_or_create_user(line_user_id, display_name)
        if not user_id:
            raise Exception("無法建立或取得使用者")

        # 取得使用者目前設定的帳本
        conn = get_connection()
        if not conn:
            raise Exception("無法連接資料庫")
        with conn.cursor() as cur:
            cur.execute("SELECT default_book_id FROM users WHERE id = %s;", (user_id,))
            result = cur.fetchone()
            book_id = result[0] if result and result[0] else None

        # 若沒有預設帳本就使用系統預設帳本
        if not book_id:
            book_id = get_or_create_default_book(user_id)
            if not book_id:
                raise Exception("無法建立或取得帳本")

            # ✅ 建立完預設帳本後設定 default_book_id
            with get_connection() as conn2:
                with conn2.cursor() as cur2:
                    cur2.execute("UPDATE users SET default_book_id = %s WHERE id = %s;", (book_id, user_id))
                    conn2.commit()


        # 取得台灣時間
        tw_now = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

        with get_connection() as conn2:
            with conn2.cursor() as cur2:
                cur2.execute("""
                    INSERT INTO ledger_entries (book_id, entry_type, description, amount, url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (book_id, entry_type, description, amount, url, tw_now))
                entry_id = cur2.fetchone()[0]
                conn2.commit()
                print(f"✅ 成功記錄項目，ID = {entry_id}")
                return entry_id  # ✅ 回傳 entry_id

    except Exception as e:
        print("❌ 插入項目失敗：", e)
        return None  # 用 None 表示失敗



def delete_entry(entry_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ledger_entries WHERE id = %s;", (entry_id,))
            conn.commit()


def get_entries_by_book(book_id, month=None):
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = "SELECT * FROM ledger_entries WHERE book_id = %s"
            params = [book_id]
            if month:
                query += " AND to_char(created_at, 'YYYY-MM') = %s"
                params.append(month)
            query += " ORDER BY created_at DESC"
            cur.execute(query, tuple(params))
            return cur.fetchall()
    except Exception as e:
        print("❌ 查詢明細失敗：", e)
        return []
    finally:
        conn.close()

def get_summary_by_book(book_id, month=None):
    conn = get_connection()
    if not conn:
        return {}
    try:
        with conn.cursor() as cur:
            query = """
                SELECT entry_type, SUM(amount)
                FROM ledger_entries
                WHERE book_id = %s
            """
            params = [book_id]
            if month:
                query += " AND to_char(created_at, 'YYYY-MM') = %s"
                params.append(month)
            query += " GROUP BY entry_type"
            cur.execute(query, tuple(params))
            return dict(cur.fetchall())
    except Exception as e:
        print("❌ 查詢摘要失敗：", e)
        return {}
    finally:
        conn.close()

def get_default_book_name(line_user_id):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT b.name
                FROM users u
                JOIN books b ON u.default_book_id = b.id
                WHERE u.line_user_id = %s;
            """, (line_user_id,))
            result = cur.fetchone()
            return result[0] if result else None
    except Exception as e:
        print("❌ 查詢預設帳本名稱失敗：", e)
        return None
    finally:
        conn.close()


# ===== 喜好網站（可選功能） =====

def get_favorite_site(line_user_id):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT favorite_site FROM users WHERE line_user_id = %s;", (line_user_id,))
            result = cur.fetchone()
            return result[0] if result else None
    except Exception as e:
        print("❌ 查詢 favorite_site 失敗：", e)
        return None
    finally:
        conn.close()

def set_favorite_site(line_user_id, url):
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET favorite_site = %s WHERE line_user_id = %s;", (url, line_user_id))
            conn.commit()
            return True
    except Exception as e:
        print("❌ 設定 favorite_site 失敗：", e)
        return False
    finally:
        conn.close()


def get_user_id(line_user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE line_user_id = %s", (line_user_id,))
            result = cur.fetchone()
            return result[0] if result else None

def create_book(line_user_id, name):
    user_id = get_user_id(line_user_id)
    if user_id is None:
        return None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO books (user_id, name)
                VALUES (%s, %s) RETURNING id
            """, (user_id, name))
            book_id = cur.fetchone()[0]
            conn.commit()
            return book_id

def delete_book(book_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
            conn.commit()

def update_entry(entry_id, entry_type, description, amount):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE ledger_entries
                SET entry_type = %s, description = %s, amount = %s
                WHERE id = %s
            """, (entry_type, description, amount, entry_id))
            conn.commit()

def set_active_book(user_id, book_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users SET default_book_id = %s
                WHERE id = (SELECT id FROM users WHERE line_user_id = %s)
            """, (book_id, user_id))
            conn.commit()


def get_entry_by_id(entry_id):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM ledger_entries WHERE id = %s;", (entry_id,))
            return cur.fetchone()
    except Exception as e:
        print("❌ 查詢單筆明細失敗：", e)
        return None
    finally:
        conn.close()
