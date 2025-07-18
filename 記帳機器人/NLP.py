from openai import OpenAI
import json
from dotenv import load_dotenv
load_dotenv()
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Step 1: 建立 Assistant（只需建立一次，結果寫入檔案）
def create_bookkeeping_assistant():
    assistant = client.beta.assistants.create(
        instructions=(
            "你是記帳助理，也是一個聊天夥伴。\n\n"
            "如果使用者的訊息是記帳相關（包含金額的收入或支出），你要：\n"
            "1. 判斷是『收入』還是『支出』，\n"
            "2. 抽出金額與描述，\n"
            "3. 呼叫 classify_entry_type 函式，\n"
            "4. 並且同時用文字回應一句貼心的話給使用者，例如『很好，有好好吃早餐』。\n\n"
            "如果輸入與功能操作相關（例如「怎麼用」、「功能選單」、「去常用娛樂城」），請不要呼叫 classify_entry_type，而是呼叫 classify_intent 函式，並標記 intent 為：\n"
            "- how_to_use：使用者想看教學\n"
            "- show_menu：使用者想打開功能選單\n"
            "- favorite_site：使用者想打開娛樂城連結\n"
            "- win_or_lose：使用者想知道自己目前水上或水下(贏錢或輸錢)多少"
            "同時也要自然語氣回應一段話。\n\n"
            "如果輸入與記帳與功能無關（例如「你好」、「最近好嗎」），請不要呼叫 function，僅回一句自然聊天語句。\n"
            "不要回覆超過10個字的語句"
        ),
        model="gpt-4o-mini",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "classify_entry_type",
                    "description": "分類使用者輸入的記帳資訊",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entry_type": {
                                "type": "string",
                                "enum": ["收入", "支出"],
                                "description": "收入或支出"
                            },
                            "description": {
                                "type": "string",
                                "description": "記帳項目描述"
                            },
                            "amount": {
                                "type": "number",
                                "description": "金額"
                            },
                            "reply": {
                                "type": "string",
                                "description": "要回給使用者的貼心話"
                            }
                        },
                        "required": ["entry_type", "description", "amount", "reply"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "classify_intent",
                    "description": "判斷使用者的意圖，例如想看功能選單、怎麼用、查詢娛樂城、查看目前水上還是水下等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "intent": {
                                "type": "string",
                                "enum": ["how_to_use", "show_menu", "favorite_site", "win_or_lose"],
                                "description": "使用者想要的功能"
                            },
                            "reply": {
                                "type": "string",
                                "description": "自然語句回覆"
                            }
                        },
                        "required": ["intent", "reply"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        ]
    )
    print("✅ Assistant created:", assistant.id)
    with open("assistant_id.json", "w") as f:
        json.dump({"assistant_id": assistant.id}, f)
    return assistant.id

# Step 2: 載入 Assistant ID
def load_assistant_id():
    with open("assistant_id.json", "r") as f:
        return json.load(f)["assistant_id"]

def classify_user_input(assistant_id: str, user_input: str):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    if run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        args = None
        tool_name = None

        for call in tool_calls:
            arguments = json.loads(call.function.arguments)
            tool_outputs.append({
                "tool_call_id": call.id,
                "output": ""
            })
            if args is None:
                args = arguments
                tool_name = call.function.name

        run = client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

        return {
            "function_name": tool_name,
            "function_args": args,
            "reply": args.get("reply")
        }

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    reply_text = ""
    for msg in messages.data:
        if msg.role == "assistant" and msg.content:
            reply_text = msg.content[0].text.value
            break

    return {
        "function_name": None,
        "function_args": None,
        "reply": reply_text
    }
