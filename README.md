# 🌸 Flower Sales Tracker Bot

A Telegram bot to track flower sales and purchases, integrated with Google Sheets for storage and analytics.

## Features
- **Easy Logging**: Log sales and purchases using simple text or CSV format.
- **Google Sheets**: Automatically saves data to weekly tabs (e.g., "December Week 1").
- **Analytics**: Generate daily, weekly, and monthly reports with profit calculation.
- **Detailed Reports**: View sales breakdowns by person.
- **Hosting**: Supports Polling (local) and Webhook (Render/Cloud) modes.

## 🚀 Setup

1.  **Clone the repo**
    ```bash
    git clone <your-repo-url>
    cd telegram-bot
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**
    Create a `.env` file:
    ```ini
    TELEGRAM_BOT_TOKEN=your_bot_token_here
    # Optional for Webhook mode
    MODE=polling
    WEBHOOK_URL=https://your-app.onrender.com
    ```

4.  **Google Sheets Setup**
    - Place your Service Account JSON file in the root directory.
    - Rename it to `telegram-bot-427.json` (or update `sheets.py`).
    - Share your Google Sheet with the service account email.

5.  **Run the Bot**
    ```bash
    python main.py
    ```

## 📝 Usage

### Logging Transactions
*   **Sale**: `100, 500` (100g for 500 INR)
*   **Sale with Name**: `100, Alice, 500`
*   **Purchase**: `buy 100, 500`
*   **Purchase with Name**: `buy 100, Supplier, 500`

### Commands
*   `/start` - Show welcome message and commands.
*   `/help` - Show usage instructions.
*   `/report <daily|weekly|monthly>` - View sales/profit summary.
*   `/detailed <daily|weekly|monthly>` - View detailed breakdown.
*   `/sales <name>` - View sales history for a specific person.

## ☁️ Deployment
Ready for **Render** (use `Procfile`) or **Google Cloud**.
See `hosting.md` for details.
