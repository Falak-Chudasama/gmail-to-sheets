import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

class GmailService:
    def __init__(self, credentials_path, token_path, scopes):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.scopes = scopes
        self.service = None

    def authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            with open(self.token_path, "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, "wb") as token:
                pickle.dump(creds, token)
        self.service = build("gmail", "v1", credentials=creds)

    def list_unread_messages(self, user_id="me", query="in:inbox is:unread"):
        try:
            response = self.service.users().messages().list(userId=user_id, q=query).execute()
            messages = response.get("messages", [])
            return messages
        except HttpError:
            return []

    def get_message(self, message_id, user_id="me", format="full"):
        try:
            msg = self.service.users().messages().get(userId=user_id, id=message_id, format=format).execute()
            return msg
        except HttpError:
            return None

    def mark_as_read(self, message_id, user_id="me"):
        try:
            self.service.users().messages().modify(
                userId=user_id,
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]}
            ).execute()
        except HttpError:
            pass