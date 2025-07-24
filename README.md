# AI Accounting Bot

[繁體中文](README_TW.md) | English

This project is a private commission. Unauthorized copying or usage is strictly prohibited.

## Project Overview

To simplify accounting, this project utilizes `Linebot` + `OpenAI` for natural language processing. The model automatically identifies whether the input is an income or an expense and records it into a `PostgreSQL` database.

## Project Structure

```
.
├── .env
├── app.yaml                        # GCP App Engine configuration
├── assistant_id.json               # Stores OpenAI Assistant ID
├── assistant_test.py               # Tests NLP for income/expense classification
├── connect.py                      # Database connection settings
├── db.py                           # Handles database value updates
├── deault_book.py                  # Sets default account book for new users
├── how_to_use_template_message.py  # Flex message tutorial for the bot
├── init_assistant.py               # Initializes the Assistant
├── main.py                         # Main program
├── NLP.py                          # Assistant configuration for NLP
├── requirements.txt
├── template_message.py             # Other template message configurations
└── templates
    ├── manage_books.html           # Account book management webpage template
    └── summary.html                # Balance overview webpage template
```

## Feature List

* Natural language accounting
* Multiple account book management
* Pie chart and line chart overviews of income and expenses
* Edit and delete accounting entries
* Set frequently used websites

## Accounting Bot Demo

The image below shows the natural language accounting process:

<img width="545" height="502" alt="Screenshot 2025-07-21 10:31 PM" src="https://github.com/user-attachments/assets/e53fd37d-0c57-4ba4-9987-0b1ad0078c88" />
