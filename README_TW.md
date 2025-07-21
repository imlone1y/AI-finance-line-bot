# AI 記帳機器人

繁體中文 | [English](README.md)

本項目為私人委託項目，未經允許不得擅自抄襲、利用。

## 項目介紹

為使記帳簡單化，使用 `LineBot` + `OpenAI` 做自然語言處理記帳，模型會自動分辨輸入內容為收入或是支出，並且記錄進 `PostgreSQL`。

## 項目結構
```
.
├── app.yaml                        # 設定 gcp App Engine 參數
├── assistant_id.json               # 紀錄 OpenAI Assistant id 用
├── assistant_test.py               # 測試自然語言處理收入 / 支出
├── connect.py                      # db 連線參數
├── db.py                           # 處理修改 db 數值
├── deault_book.py                  # 設定新成員預設帳本
├── how_to_use_template_message.py  # 機器人教學 flex message
├── init_assistant.py               # 初始化 Assistant
├── main.py                         # 主程式
├── NLP.py                          # 自然語言處理 Assistant 參數設定
├── requirements.txt
├── template_message.py             # 其餘樣板訊息設定
└── templates
    ├── manage_books.html           # 帳本管理網站模板
    └── summary.html                # 餘額總覽網站模板
```
## 功能列表
- 自然語言記帳
- 多帳本管理
- 收入支出圓餅圖、折線圖總覽
- 記帳項目更改、刪除
- 設定常用網站

## 記帳機器人圖示
下方圖片為自然語言記帳過程：

<img width="545" height="502" alt="截圖 2025-07-21 晚上10 31 10" src="https://github.com/user-attachments/assets/e53fd37d-0c57-4ba4-9987-0b1ad0078c88" />
