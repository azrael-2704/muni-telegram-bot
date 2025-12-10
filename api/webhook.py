import asyncio
import os
import logging
from telegram import Update
from http.server import BaseHTTPRequestHandler
import json

# Import the application from main
# Note: we need to make sure main.py doesn't run its main block when imported
from main import app

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def process_update(update_json):
    if app:
        # Initialize the app if not already done
        if not app.updater.running:
             await app.initialize()
        
        update = Update.de_json(update_json, app.bot)
        await app.process_update(update)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update_json = json.loads(post_data.decode('utf-8'))
        
        # Run the async process
        try:
            asyncio.run(process_update(update_json))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        except Exception as e:
            logging.error(f"Error processing update: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Telegram Bot API is running')
