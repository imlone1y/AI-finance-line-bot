from NLP import load_assistant_id, classify_user_input

assistant_id = load_assistant_id()

test_inputs = [
    "我今天賺了5000",
    "看電影250",
    "我好餓",
    "怎麼記帳",
    "我要看功能選單",
    "幫我打開娛樂城網址",
    "哈囉～",
]

for input_text in test_inputs:
    print("💬 測試輸入：", input_text)
    result = classify_user_input(assistant_id, input_text)
    
    if result["function_name"] == "classify_entry_type":
        print("🧾 記帳類型：", result["function_args"]["entry_type"])
        print("📝 描述：", result["function_args"]["description"])
        print("💰 金額：", result["function_args"]["amount"])
        print("💬 回應：", result["function_args"]["reply"])

    elif result["function_name"] == "classify_intent":
        print("🔧 意圖判斷：", result["function_args"]["intent"])
        print("💬 回應：", result["function_args"]["reply"])

    else:
        print("💬 純聊天回應：", result["reply"])

    print("-" * 50)
