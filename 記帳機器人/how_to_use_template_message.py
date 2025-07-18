from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    PushMessageRequest,
    FlexMessage, FlexContainer
)
from dotenv import load_dotenv
import os
load_dotenv()

channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")

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



def send_template_carousel1(user_id):
    config = Configuration(access_token=channel_access_token)
    with ApiClient(config) as api_client:
        messaging_api = MessagingApi(api_client)

        carousel_json = {
            "type": "carousel",
            "contents": [
                make_bubble("功能教學1", "輸入<怎麼用>跳出教學選單", "https://example.com/bot/images/item1.jpg", "https://example.com/page/111"),
                make_bubble("功能教學2", "說明 2", "https://example.com/bot/images/item2.jpg", "https://example.com/page/222"),
                make_bubble("功能教學3", "說明 3", "https://example.com/bot/images/item3.jpg", "https://example.com/page/333"),
                make_bubble("功能教學4", "說明 4", "https://example.com/bot/images/item4.jpg", "https://example.com/page/444"),
                make_bubble("功能教學5", "說明 5", "https://example.com/bot/images/item5.jpg", "https://example.com/page/555")
            ]
        }

        flex_container = FlexContainer.from_dict(carousel_json)
        message = FlexMessage(alt_text="使用教學", contents=flex_container)

        messaging_api.push_message(PushMessageRequest(
            to=user_id,
            messages=[message]
        ))


def send_template_carousel2(user_id):
    config = Configuration(access_token=channel_access_token)
    with ApiClient(config) as api_client:
        messaging_api = MessagingApi(api_client)

        carousel_json = {
            "type": "carousel",
            "contents": [
                make_bubble("功能教學1", "輸入<娛樂城>跳出常用娛樂城網址", "https://example.com/bot/images/item1.jpg", "https://example.com/page/111"),
                make_bubble("功能教學2", "說明 2", "https://example.com/bot/images/item2.jpg", "https://example.com/page/222"),
                make_bubble("功能教學3", "說明 3", "https://example.com/bot/images/item3.jpg", "https://example.com/page/333"),
                make_bubble("功能教學4", "說明 4", "https://example.com/bot/images/item4.jpg", "https://example.com/page/444"),
                make_bubble("功能教學5", "說明 5", "https://example.com/bot/images/item5.jpg", "https://example.com/page/555")
            ]
        }

        flex_container = FlexContainer.from_dict(carousel_json)
        message = FlexMessage(alt_text="使用教學", contents=flex_container)

        messaging_api.push_message(PushMessageRequest(
            to=user_id,
            messages=[message]
        ))

def send_template_carousel3(user_id):
    config = Configuration(access_token=channel_access_token)
    with ApiClient(config) as api_client:
        messaging_api = MessagingApi(api_client)

        carousel_json = {
            "type": "carousel",
            "contents": [
                make_bubble("功能教學1", "輸入<怎麼用>跳出教學選單", "https://example.com/bot/images/item1.jpg", "https://example.com/page/111"),
                make_bubble("功能教學2", "說明 2", "https://example.com/bot/images/item2.jpg", "https://example.com/page/222"),
                make_bubble("功能教學3", "說明 3", "https://example.com/bot/images/item3.jpg", "https://example.com/page/333"),
                make_bubble("功能教學4", "說明 4", "https://example.com/bot/images/item4.jpg", "https://example.com/page/444"),
                make_bubble("功能教學5", "說明 5", "https://example.com/bot/images/item5.jpg", "https://example.com/page/555")
            ]
        }

        flex_container = FlexContainer.from_dict(carousel_json)
        message = FlexMessage(alt_text="使用教學", contents=flex_container)

        messaging_api.push_message(PushMessageRequest(
            to=user_id,
            messages=[message]
        ))

def send_template_carousel4(user_id):
    config = Configuration(access_token=channel_access_token)
    with ApiClient(config) as api_client:
        messaging_api = MessagingApi(api_client)

        carousel_json = {
            "type": "carousel",
            "contents": [
                make_bubble("功能教學1", "輸入<怎麼用>跳出教學選單", "https://example.com/bot/images/item1.jpg", "https://example.com/page/111"),
                make_bubble("功能教學2", "說明 2", "https://example.com/bot/images/item2.jpg", "https://example.com/page/222"),
                make_bubble("功能教學3", "說明 3", "https://example.com/bot/images/item3.jpg", "https://example.com/page/333"),
                make_bubble("功能教學4", "說明 4", "https://example.com/bot/images/item4.jpg", "https://example.com/page/444"),
                make_bubble("功能教學5", "說明 5", "https://example.com/bot/images/item5.jpg", "https://example.com/page/555")
            ]
        }

        flex_container = FlexContainer.from_dict(carousel_json)
        message = FlexMessage(alt_text="使用教學", contents=flex_container)

        messaging_api.push_message(PushMessageRequest(
            to=user_id,
            messages=[message]
        ))

def send_template_carousel5(user_id):
    config = Configuration(access_token=channel_access_token)
    with ApiClient(config) as api_client:
        messaging_api = MessagingApi(api_client)

        carousel_json = {
            "type": "carousel",
            "contents": [
                make_bubble("功能教學1", "輸入<怎麼用>跳出教學選單", "https://example.com/bot/images/item1.jpg", "https://example.com/page/111"),
                make_bubble("功能教學2", "說明 2", "https://example.com/bot/images/item2.jpg", "https://example.com/page/222"),
                make_bubble("功能教學3", "說明 3", "https://example.com/bot/images/item3.jpg", "https://example.com/page/333"),
                make_bubble("功能教學4", "說明 4", "https://example.com/bot/images/item4.jpg", "https://example.com/page/444"),
                make_bubble("功能教學5", "說明 5", "https://example.com/bot/images/item5.jpg", "https://example.com/page/555")
            ]
        }

        flex_container = FlexContainer.from_dict(carousel_json)
        message = FlexMessage(alt_text="使用教學", contents=flex_container)

        messaging_api.push_message(PushMessageRequest(
            to=user_id,
            messages=[message]
        ))