# init_assistant.py

import json
from NLP import create_bookkeeping_assistant

ASSISTANT_FILE = "assistant_id.json"

def save_assistant_id(assistant_id):
    with open(ASSISTANT_FILE, "w") as f:
        json.dump({"assistant_id": assistant_id}, f)
    print(f"✅ Assistant ID 已儲存到 {ASSISTANT_FILE}")

def main():
    assistant_id = create_bookkeeping_assistant()
    save_assistant_id(assistant_id)

if __name__ == "__main__":
    main()
