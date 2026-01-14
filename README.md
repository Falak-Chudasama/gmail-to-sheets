# gmail-to-sheets

Python automation that reads unread emails from Gmail and appends them to a Google Sheet

## features

- OAuth 2.0 installed app flow
- fetch unread messages from inbox
- parse from, subject, date, plain-text content
- append rows to Google Sheets
- mark processed messages as read
- persist processed message ids in local SQLite

## structure


├── src/
│   ├── gmail_service.py
│   ├── sheets_service.py
│   ├── email_parser.py
│   ├── state_store.py
│   └── main.py
├── credentials/
├── data/
├── proof/
├── config.py
├── requirements.txt
├── .gitignore
└── README.md

## quickstart

1. enable Gmail API and Google Sheets API in Google Cloud
2. create OAuth client credentials (Desktop) and put credentials.json in credentials/
3. install deps and run


python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py