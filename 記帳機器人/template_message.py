from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    PushMessageRequest, TextMessage,
    QuickReply, QuickReplyItem, PostbackAction,
    FlexMessage, FlexContainer, URIAction
)
import os
from db import get_favorite_site
from dotenv import load_dotenv
load_dotenv()

channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")


# ➤ Flex Bubble 建立函式（保留原教學用）
def make_bubble(title, desc, img_url, link_url):
    return {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": img_url,
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
                "type": "uri",
                "uri": link_url
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": title, "weight": "bold", "size": "lg"},
                {"type": "text", "text": desc, "wrap": True}
            ]
        }
    }

def send_entry_flex(messaging_api, user_id, entry_type, description, amount, book_name, date_str, entry_id):
    color = "#16a34a" if entry_type == "收入" else "#ef4444"  # 綠 / 紅
    flex_json = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": entry_type,
                            "weight": "bold",
                            "color": color,
                            "size": "sm",
                            "flex": 1
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{
                                "type": "text",
                                "text": book_name,
                                "color": "#ffffff",
                                "size": "xs",
                                "align": "center",
                                "gravity": "center",
                                "wrap": True
                            }],
                            "backgroundColor": "#22c55e",
                            "cornerRadius": "999px",
                            "paddingAll": "5px",
                            "paddingStart": "10px",
                            "paddingEnd": "10px"
                        }
                    ],
                    "justifyContent": "space-between"
                },
                {
                    "type": "text",
                    "text": f"${int(amount):,}",
                    "weight": "bold",
                    "size": "3xl"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {"type": "text", "text": "備註", "flex": 1, "color": "#aaaaaa", "size": "sm"},
                                {"type": "text", "text": description, "flex": 4, "size": "sm"}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {"type": "text", "text": "日期", "flex": 1, "color": "#aaaaaa", "size": "sm"},
                                {"type": "text", "text": date_str, "flex": 4, "size": "sm"}
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "編輯",
                        "uri": f"https://money-line-bot.de.r.appspot.com/manage_books/{user_id}?entry_id={entry_id}"
                    }
                }
            ],
            "flex": 0
        },
        "styles": {
            "body": {
                "backgroundColor": "#ffffff"
            },
            "footer": {
                "backgroundColor": "#ffffff"
            }
        }
    }

    flex = FlexMessage(alt_text="記帳成功", contents=FlexContainer.from_dict(flex_json))
    messaging_api.push_message(PushMessageRequest(to=user_id, messages=[flex]))




def send_button_flex_template(user_id):
    config = Configuration(access_token=channel_access_token)
    with ApiClient(config) as api_client:
        messaging_api = MessagingApi(api_client)

        site_url = get_favorite_site(user_id)

        if site_url:
            game_button = {
                "type": "button",
                "action": {
                    "type": "uri",
                    "label": "🎰 前往常用娛樂城",
                    "uri": site_url
                }
            }
        else:
            game_button = {
                "type": "button",
                "action": {
                    "type": "postback",
                    "label": "🎰 設定娛樂城網址",
                    "data": "set_favorite_site"
                }
            }

        how_to_button = {
            "type": "button",
            "action": {
                "type": "postback",
                "label": "📖 機器人使用說明",
                "data": "how_to_use"
            }
        }

        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://money-line-bot.de.r.appspot.com/static/function.png",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "text", "text": "💡 功能選單", "weight": "bold", "size": "lg"},
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    game_button,
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "💰 我現在贏錢還輸錢？",
                            "data": "check_balance"
                        }
                    },
                    how_to_button
                ]
            }
        }
        flex_container = FlexContainer.from_dict(bubble)
        message = FlexMessage(
            alt_text="要記帳嗎",
            contents=flex_container
        )

        messaging_api.push_message(PushMessageRequest(
            to=user_id,
            messages=[message]
        ))

def send_quick_reply_entry_type(user_id,text):
    config = Configuration(access_token=channel_access_token)
    with ApiClient(config) as api_client:
        messaging_api = MessagingApi(api_client)

        quick_reply = QuickReply(items=[
            QuickReplyItem(action=URIAction(label='🎲 擲筊', uri=f"https://tw.piliapp.com/random/blocks/")),
            QuickReplyItem(action=URIAction(label='🗂️ 管理', uri=f"https://money-line-bot.de.r.appspot.com/manage_books/{user_id}")),
            QuickReplyItem(action=URIAction(label='📊 明細', uri=f"https://money-line-bot.de.r.appspot.com/summary/{user_id}"))
        ])

        message = TextMessage(
            text=str(text),
            quick_reply=quick_reply
        )

        messaging_api.push_message(PushMessageRequest(
            to=user_id,
            messages=[message]
        ))
