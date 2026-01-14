from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SheetsService:
    def __init__(self, credentials):
        self.service = build("sheets", "v4", credentials=credentials)

    def append_row(self, spreadsheet_id, sheet_name, row_values):
        body = {"values": [row_values]}
        range_name = f"{sheet_name}!A1"
        try:
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body
            ).execute()
            return result
        except HttpError as e:
            raise e