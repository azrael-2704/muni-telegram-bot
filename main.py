import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

from sheets import log_transaction
from message_parser import parse_sales_message
from analytics import generate_report, generate_detailed_report

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌸 **Flower Bot Help** 🌸\n\n"
        "**📝 Logging Transactions**\n"
        "• `100, 500` → Sold 100g for 500\n"
        "• `100, Alice, 500` → Sold 100g to Alice for 500\n"
        "• `buy 100, 500` → Bought 100g for 500\n"
        "• `buy 100, Supplier, 500` → Bought 100g from Supplier\n\n"
        "**📊 Analytics**\n"
        "• `/report <period>` → Summary (daily/weekly/monthly)\n"
        "• `/detailed <period>` → Full transaction list + stats\n"
        "• `/sales <name>` → History for a specific person\n"
        "• `/sales` → Your own history"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "👋 **Welcome to the Flower Sales Bot!**\n\n"
            "I help you track sales, purchases, and profits.\n"
            "Data is saved to Google Sheets automatically.\n\n"
            "Type `/help` to see all available commands and how to log data."
        ),
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    data = parse_sales_message(text)

    if data:
        # data: {'type', 'amount', 'entity', 'price'}
        seller_name = update.effective_user.first_name or "Unknown"
        
        success = log_transaction(
            seller=seller_name,
            action=data['type'],
            entity=data['entity'],
            amount=data['amount'],
            price=data['price']
        )
        
        if success:
            # Logged: 3g sold to Priya for ₹450 by <message sender name>
            action_verb = "sold to" if data['type'] == 'Sale' else "bought from"
            response = (
                f"Logged: {data['amount']}g {action_verb} {data['entity']} "
                f"for ₹{data['price']} by {seller_name}"
            )
        else:
            response = "❌ Error recording transaction. Please check the logs."
            
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode='Markdown')

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Default to weekly if no arg provided
    period = 'weekly'
    if context.args:
        period = context.args[0].lower()
        
    if period not in ['daily', 'weekly', 'monthly']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /report <daily|weekly|monthly>")
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text="⏳ Generating report...")
    report_text = generate_report(period)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=report_text, parse_mode='Markdown')

async def detailed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    period = 'weekly'
    if context.args:
        period = context.args[0].lower()
        
    if period not in ['daily', 'weekly', 'monthly']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /detailed <daily|weekly|monthly>")
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text="⏳ Generating detailed report...")
    report_text = generate_detailed_report(period)
    # Split message if too long (Telegram limit is 4096 chars)
    if len(report_text) > 4000:
        for x in range(0, len(report_text), 4000):
            await context.bot.send_message(chat_id=update.effective_chat.id, text=report_text[x:x+4000], parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=report_text, parse_mode='Markdown')

async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /sales <name>
    If no name provided, defaults to the user who sent the command.
    """
    target_name = update.effective_user.first_name
    
    if context.args:
        target_name = " ".join(context.args)
        
    if not target_name:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Could not determine name. Usage: /sales <name>")
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⏳ Generating report for {target_name}...")
    
    # Parse response logic here?
    # Looks like we missed the implementation of sales_command body in previous edits or it was cut off.
    # Restoring the end of sales_command and adding proper app initialization.
    
    # We need to import generate_person_report inside or at top. 
    from analytics import generate_person_report
    report_text = generate_person_report(target_name)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=report_text, parse_mode='Markdown')

# Initialize app globally for Vercel import
app = None
if os.getenv('TELEGRAM_BOT_TOKEN'):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('report', report_command))
    app.add_handler(CommandHandler('detailed', detailed_command))
    app.add_handler(CommandHandler('sales', sales_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

if __name__ == '__main__':
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token or token == 'your_token_here':
        print("Error: TELEGRAM_BOT_TOKEN not found in .env file.")
        exit(1)

    application = app
    
    print("Bot is running...")
    
    # Check for MODE environment variable
    mode = os.getenv('MODE', 'polling')
    
    if mode == 'webhook':
        webhook_url = os.getenv('WEBHOOK_URL')
        port = int(os.getenv('PORT', '8080'))
        
        if not webhook_url:
            print("Error: WEBHOOK_URL is required for webhook mode.")
            exit(1)
            
        print(f"Starting webhook on port {port}...")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token,
            webhook_url=f"{webhook_url}/{token}"
        )
    else:
        print("Starting polling...")
        application.run_polling()

