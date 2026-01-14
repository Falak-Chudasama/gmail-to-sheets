import os
CREDENTIALS_PATH = os.path.join("credentials", "credentials.json")
TOKEN_PATH = os.path.join("credentials", "token.pickle")
STATE_DB = os.path.join("data", "state.db")
SPREADSHEET_ID = "170ydHhoJVt7dI2zlkaPN4yVRJ17p3atajb6i8ttEJjY"
SHEET_NAME = "Sheet1"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/spreadsheets"
]