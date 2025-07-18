from flask import Flask, request, abort, render_template, jsonify
import re

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError

from db import (
    insert_entry,
    get_summary_by_book, 
    get_entries_by_book, 
    user_exists,
    get_books_by_user,
    set_favorite_site,
    get_favorite_site,
    get_connection,
    get_user_id,
    create_book,
    delete_entry,
    set_active_book,
    get_default_book_name
)

from datetime import datetime

from template_message import send_quick_reply_entry_type, send_button_flex_template, send_entry_flex

from how_to_use_template_message import (send_template_carousel1,
                                         send_template_carousel2,
                                         send_template_carousel3,
                                         send_template_carousel4,
                                         send_template_carousel5
                                         )

from NLP import load_assistant_id, classify_user_input

# 載入 Assistant ID
assistant_id = load_assistant_id()


from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent,
    FollowEvent
)
from dotenv import load_dotenv
load_dotenv()

import os

app = Flask(__name__)

# Channel Token & Secret
channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")
channel_secret = os.getenv("CHANNEL_SECRET")

handler = WebhookHandler(channel_secret)

# 儲存每位使用者點過「收入 / 支出」的選擇
pending_set_site = {}

@app.route("/manage_books/<user_id>")
def manage_books_page(user_id):
    return render_template("manage_books.html", user_id=user_id)


# HTML summary 頁面
@app.route("/summary/<user_id>")
def user_summary_page(user_id):
    from datetime import datetime, timedelta
    from db import get_user_id, get_books_by_user, get_summary_by_book, get_entries_by_book, get_connection

    # 所有帳本
    books = get_books_by_user(user_id)

    # 從 URL 取得參數
    book_id_str = request.args.get("book")
    month = request.args.get("month")

    # 決定 selected_book_id
    try:
        selected_book_id = int(book_id_str)
    except (TypeError, ValueError):
        # 若沒傳 book_id，就找使用者的 default_book_id
        user_db_id = get_user_id(user_id)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT default_book_id FROM users WHERE id = %s", (user_db_id,))
                result = cur.fetchone()
                selected_book_id = result[0] if result and result[0] else (books[0]["id"] if books else None)

    # 查詢資料
    entries = get_entries_by_book(selected_book_id, month)
    summary = get_summary_by_book(selected_book_id, month)
    balance = summary.get("收入", 0) - summary.get("支出", 0)

    return render_template("summary.html",
                           summary=summary,
                           entries=entries,
                           balance=balance,
                           books=books,
                           selected_book=selected_book_id,
                           now=datetime.now(),
                           timedelta=timedelta)



# LINE Webhook 入口
@app.route("/", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    if not signature:
        abort(400)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 抓取使用者名稱
def get_user_name(user_id):
    config = Configuration(access_token=channel_access_token)
    with ApiClient(config) as api_client:
        messaging_api = MessagingApi(api_client)
        try:
            profile = messaging_api.get_profile(user_id)
            user_name = profile.display_name
            print(f"✅ 獲取用戶: {user_name} 的訊息")
            return user_name
        except Exception as e:
            print(f"無法獲取用戶名稱: {e}")
            return "未知使用者"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    message_text = event.message.text.strip()
    user_name = get_user_name(user_id)

    config = Configuration(access_token=channel_access_token)
    with ApiClient(config) as api_client:
        messaging_api = MessagingApi(api_client)

        if not user_exists(user_id):
            insert_entry(user_id, "收入", "初始化帳戶", 0, display_name=user_name)
            push_message(messaging_api, user_id, "👤 歡迎新用戶，我們已幫你建立預設帳本")

        # ➤ 如果是 "!怎麼用"
        if message_text == "怎麼用":
            send_template_carousel1(user_id)
            send_template_carousel2(user_id)
            send_template_carousel3(user_id)
            send_template_carousel4(user_id)
            send_template_carousel5(user_id)
            send_quick_reply_entry_type(user_id, "可以開始記帳了！")
            return

        elif message_text == "功能選單":
            send_button_flex_template(user_id)
            send_quick_reply_entry_type(user_id, "可以開始記帳了！")
            return

        elif message_text == "娛樂城":
            site = get_favorite_site(user_id)
            if site == None:
                push_message(messaging_api, user_id, "請先輸入\"功能選單\" 後，點選\"🎰 設定娛樂城網址\" 來設定常用娛樂城網址 !")
                return
            else:
                push_message(messaging_api, user_id, site)
                return
        
        # ➤ 如果 user 正在輸入 favorite site，就處理並 return
        elif user_id in pending_set_site:
            set_favorite_site(user_id, message_text)
            del pending_set_site[user_id]
            send_quick_reply_entry_type(user_id,"✅ 已儲存你的常用娛樂城網址")
            return

        else:
            result = classify_user_input(assistant_id, message_text)

            if result["function_name"] == "classify_entry_type":
                args = result["function_args"]

                # 🟢 一次 insert 並取得 entry_id
                entry_id = insert_entry(
                    line_user_id=user_id,
                    entry_type=args["entry_type"],
                    description=args["description"],
                    amount=float(args["amount"]),
                    url=None,
                    display_name=user_name
                )

                if entry_id:
                    book_name = get_default_book_name(user_id)
                    date_str = datetime.now().strftime("%Y/%m/%d")

                    send_entry_flex(
                        messaging_api=messaging_api,
                        user_id=user_id,
                        entry_type=args["entry_type"],
                        description=args["description"],
                        amount=float(args["amount"]),
                        book_name=book_name or "預設帳本",
                        date_str=date_str,
                        entry_id=entry_id
                    )
                else:
                    push_message(messaging_api, user_id, "❌ 寫入失敗，請稍後再試")

            elif result["function_name"] == "classify_intent":
                intent = result["function_args"]["intent"]
                if intent == "how_to_use":
                    send_template_carousel1(user_id)
                    send_template_carousel2(user_id)
                    send_template_carousel3(user_id)
                    send_template_carousel4(user_id)
                    send_template_carousel5(user_id)
                elif intent == "show_menu":
                    send_button_flex_template(user_id)
                elif intent == "favorite_site":
                    site = get_favorite_site(user_id)
                    send_quick_reply_entry_type(user_id, site if site else "請先輸入\"功能選單\" 後，點選\"🎰 設定娛樂城網址\" 來設定常用娛樂城網址 !")
                    return
                elif intent == "win_or_lose":
                    numeric_user_id = get_user_id(user_id)
                    conn = get_connection()
                    if not conn:
                        reply_text = "⚠️ 無法連線資料庫"
                    else:
                        with conn.cursor() as cur:
                            cur.execute("SELECT default_book_id FROM users WHERE id = %s", (numeric_user_id,))
                            result = cur.fetchone()
                            if not result or not result[0]:
                                reply_text = "⚠️ 你尚未設定預設帳本"
                            else:
                                book_id = result[0]
                                this_month = datetime.now().strftime("%Y-%m")
                                summary = get_summary_by_book(book_id, this_month)
                                income = summary.get("收入", 0)
                                expense = summary.get("支出", 0)
                                balance = income - expense

                                if balance > 0:
                                    reply_text = f"💰 本月目前水上：{balance} 元\n保持下去～不要上頭！"
                                elif balance < 0:
                                    reply_text = f"💰 本月目前水下：{abs(balance)} 元\n沒問題～希望可以見證你上岸！"
                                else:
                                    reply_text = f"💰 本月目前收支打平\n理財小能手！繼續保持～"
                        conn.close()
                    send_quick_reply_entry_type(user_id, reply_text)
                    return

                    

            send_quick_reply_entry_type(user_id, result["reply"])
            return


@app.route('/_ah/warmup')
def warmup():
    print("🔥 Warmup request received")
    return 'warmed up', 200


@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    postback_data = event.postback.data

    config = Configuration(access_token=channel_access_token)
    with ApiClient(config) as api_client:
        messaging_api = MessagingApi(api_client)

        if postback_data == 'how_to_use':
            send_template_carousel1(user_id)
            send_template_carousel2(user_id)
            send_template_carousel3(user_id)
            send_template_carousel4(user_id)
            send_template_carousel5(user_id)
            send_quick_reply_entry_type(user_id, "可以開始記帳了！")
        elif postback_data == 'set_favorite_site':
            pending_set_site[user_id] = True
            push_message(messaging_api, user_id, "請輸入你常用的娛樂城網址（含 https://）")
        elif postback_data == "check_balance":
            line_user_id = event.source.user_id
            user_id = get_user_id(line_user_id)

            if not user_id:
                reply_text = "⚠️ 找不到你的帳戶，請重新開始"
            else:
                conn = get_connection()
                if not conn:
                    reply_text = "⚠️ 無法連線資料庫"
                else:
                    with conn.cursor() as cur:
                        cur.execute("SELECT default_book_id FROM users WHERE id = %s", (user_id,))
                        result = cur.fetchone()
                        if not result or not result[0]:
                            reply_text = "⚠️ 你尚未設定預設帳本"
                        else:
                            book_id = result[0]
                            this_month = datetime.now().strftime("%Y-%m")
                            summary = get_summary_by_book(book_id, this_month)
                            income = summary.get("收入", 0)
                            expense = summary.get("支出", 0)
                            balance = income - expense

                            if balance > 0:
                                reply_text = f"💰 本月目前水上：{balance} 元\n保持下去～不要上頭！"
                            elif balance < 0:
                                reply_text = f"💰 本月目前水下：{abs(balance)} 元\n沒問題～希望可以見證你上岸！"
                            else:
                                reply_text = f"💰 本月目前收支打平\n理財小能手！繼續保持～"
                    conn.close()

            send_quick_reply_entry_type(line_user_id, reply_text)



@app.route("/api/summary_data")
def api_summary_data():
    book_id = int(request.args.get("book_id"))
    
    summary = get_summary_by_book(book_id)
    entries = get_entries_by_book(book_id)
    balance = summary.get('收入', 0) - summary.get('支出', 0)

    for e in entries:
        e["created_at"] = e["created_at"].strftime("%Y-%m-%d %H:%M")
    
    return jsonify({
        "summary": summary,
        "entries": entries,
        "balance": balance
    })


@app.route("/api/books/<user_id>")
def api_get_books(user_id):
    books = get_books_by_user(user_id)
    return jsonify(books)

@app.route("/api/entries/<int:entry_id>")
def api_get_single_entry(entry_id):
    from db import get_entry_by_id
    entry = get_entry_by_id(entry_id)
    if not entry:
        return jsonify({"error": "not found"}), 404
    return jsonify(entry)



@app.route("/api/books", methods=["POST"])
def api_create_book():
    data = request.json
    user_id = request.args.get("user_id")
    name = data.get("name")

    if not user_id or not name:
        return "缺少參數", 400

    new_id = create_book(user_id, name)
    return jsonify({"id": new_id})


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def api_delete_book(book_id):
    from db import delete_book  # 你需自行實作這個函式
    delete_book(book_id)
    return "", 204


@app.route("/api/books/<int:book_id>/entries")
def api_get_entries(book_id):
    entries = get_entries_by_book(book_id)
    for e in entries:
        e["created_at"] = e["created_at"].strftime("%Y-%m-%d %H:%M")
    return jsonify(entries)


@app.route("/api/entries/<int:entry_id>", methods=["PUT"])
def api_update_entry(entry_id):
    data = request.json
    from db import update_entry  # 你需自行實作這個函式
    update_entry(entry_id, data["entry_type"], data["description"], data["amount"])
    return "", 204


@app.route("/api/active_book", methods=["POST"])
def api_set_active_book():
    data = request.json
    line_user_id = data.get("line_user_id")  # ✅ 直接從 JSON 拿 LINE ID
    book_id = data.get("book_id")

    set_active_book(line_user_id, book_id)  # ✅ 傳 line_user_id，而非數字 ID
    print(f"✅ 已為 {line_user_id} 設定預設帳本為 ID {book_id}")
    return "", 204


@app.route("/api/default_book/<line_user_id>")
def api_get_default_book_id(line_user_id):
    from db import get_user_id
    user_id = get_user_id(line_user_id)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT default_book_id FROM users WHERE id = %s", (user_id,))
            result = cur.fetchone()
            return jsonify({"default_book_id": result[0] if result else None})


@app.route("/api/entries/<int:entry_id>", methods=["DELETE"])
def api_delete_entry(entry_id):
    delete_entry(entry_id)
    return "", 204


@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    send_button_flex_template(user_id)
    send_quick_reply_entry_type(user_id)

# 基本訊息函式
def reply_message(messaging_api, reply_token, message_text):
    message = TextMessage(text=message_text)
    reply_request = ReplyMessageRequest(
        reply_token=reply_token,
        messages=[message]
    )
    messaging_api.reply_message(reply_request)

def push_message(messaging_api, user_id, message_text):
    message = TextMessage(text=message_text)
    push_request = PushMessageRequest(
        to=user_id,
        messages=[message]
    )
    messaging_api.push_message(push_request)
    


if __name__ == "__main__":
    app.run()
