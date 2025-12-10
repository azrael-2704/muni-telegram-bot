import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging
import os
import math

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Try to find the json file
CREDS_FILE = "service_account.json"
if not os.path.exists(CREDS_FILE):
    # Check for other json files that might be the key
    for file in os.listdir('.'):
        if file.endswith('.json') and 'telegram-bot' in file:
            CREDS_FILE = file
            break

SHEET_NAME = "telegram-bot-427"

import json

def get_client():
    """Authenticates and returns a gspread client."""
    try:
        # Check for environment variable first (Vercel deployment)
        google_creds_env = os.getenv("GOOGLE_CREDENTIALS")
        if google_creds_env:
            creds_dict = json.loads(google_creds_env)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        else:
            # Fallback to local file (local testing)
            creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
            
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Sheets: {e}")
        return None

def get_week_of_month(date):
    """Returns the week number of the month (1-5)."""
    first_day = date.replace(day=1)
    dom = date.day
    adjusted_dom = dom + first_day.weekday()
    return int(math.ceil(adjusted_dom / 7.0))

def get_or_create_sheet(client):
    """
    Gets the main spreadsheet. If it doesn't exist, it creates it.
    Then gets or creates the worksheet for the current week.
    Naming: "December Week 1"
    """
    try:
        # Try to open the main spreadsheet
        try:
            spreadsheet = client.open(SHEET_NAME)
        except gspread.SpreadsheetNotFound:
            logger.info(f"Spreadsheet '{SHEET_NAME}' not found. Creating it...")
            spreadsheet = client.create(SHEET_NAME)

        # Determine current sheet name
        now = datetime.now()
        month_name = now.strftime("%B")
        week_num = get_week_of_month(now)
        worksheet_name = f"{month_name} Week {week_num}"

        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            logger.info(f"Worksheet '{worksheet_name}' not found. Creating it...")
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=10)
            # Add headers
            worksheet.append_row([
                "Timestamp", "Seller", "Action", "Buyer/Source", "Amount(g)", "Price(INR)", "WeekID"
            ])

        return worksheet
    except Exception as e:
        logger.error(f"Error accessing sheet: {e}")
        return None

def log_transaction(seller, action, entity, amount, price):
    """
    Logs a transaction (Sale or Buy) to the current week's sheet.
    """
    client = get_client()
    if not client:
        return False

    worksheet = get_or_create_sheet(client)
    if not worksheet:
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # WeekID: YYYYWW (e.g. 202548)
    year, week_iso, _ = datetime.now().isocalendar()
    week_id = f"{year}{week_iso}"

    row = [timestamp, seller, action, entity, amount, price, week_id]
    
    try:
        worksheet.append_row(row)
        return True
    except Exception as e:
        logger.error(f"Failed to append row: {e}")
        return False
