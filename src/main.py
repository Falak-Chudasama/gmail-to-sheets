import os
import sys
import pickle
import time
import datetime
import logging
from config import CREDENTIALS_PATH, TOKEN_PATH, STATE_DB, SPREADSHEET_ID, SHEET_NAME, SCOPES
from src.gmail_service import GmailService
from src.sheets_service import SheetsService
from src.email_parser import parse_message_to_row
from src.state_store import StateStore

def load_credentials_for_sheets(token_path):
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"Token not found at {token_path}. Run the auth flow first.")
    with open(token_path, "rb") as f:
        creds = pickle.load(f)
    return creds

def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
    logger = logging.getLogger("gmail-to-sheets")
    return logger

def now_iso():
    return datetime.datetime.utcnow().isoformat()

def main():
    logger = setup_logging()
    if SPREADSHEET_ID == "REPLACE_WITH_YOUR_SPREADSHEET_ID":
        logger.error("Set your SPREADSHEET_ID in config.py before running.")
        sys.exit(1)
    gmail = GmailService(CREDENTIALS_PATH, TOKEN_PATH, SCOPES)
    logger.info("Authenticating Gmail and initializing services")
    gmail.authenticate()
    creds = load_credentials_for_sheets(TOKEN_PATH)
    sheets = SheetsService(creds)
    store = StateStore(STATE_DB)
    logger.info("Startup complete. Entering polling loop every 10 seconds. Press Ctrl+C to stop.")
    try:
        while True:
            try:
                messages = gmail.list_unread_messages()
            except Exception as e:
                logger.exception(f"{now_iso()} error listing messages: {e}")
                time.sleep(10)
                continue
            if not messages:
                logger.info(f"{now_iso()} no unread messages")
                time.sleep(10)
                continue
            for msg_meta in messages:
                msg_id = msg_meta.get("id")
                if not msg_id:
                    continue
                if store.is_processed(msg_id):
                    logger.info(f"{now_iso()} skipping already processed {msg_id}")
                    continue
                msg = gmail.get_message(msg_id)
                if not msg:
                    logger.error(f"{now_iso()} failed to fetch message {msg_id}")
                    continue
                row = parse_message_to_row(msg)
                try:
                    sheets.append_row(SPREADSHEET_ID, SHEET_NAME, row)
                    logger.info(f"{now_iso()} appended message {msg_id} subject={row[1]}")
                except Exception as e:
                    logger.exception(f"{now_iso()} failed to append message {msg_id}: {e}")
                    continue
                try:
                    store.mark_processed(msg_id)
                    gmail.mark_as_read(msg_id)
                    logger.info(f"{now_iso()} marked read and stored {msg_id}")
                except Exception as e:
                    logger.exception(f"{now_iso()} post-process error for {msg_id}: {e}")
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Interrupted by user, exiting")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
    finally:
        logger.info("Shutdown complete")

if __name__ == "__main__":
    main()