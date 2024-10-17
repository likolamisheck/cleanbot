from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram Bot Token
TELEGRAM_TOKEN = '7061540516:AAFot-pHmGVk5ibgOsWvs1MRc1ksx-6Fylo'

# List of people on duty
duty_people = ["Likola", "Miliko George", "Temba"]

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! This bot will inform you who is on duty every Sunday please adhear to the rules so that your room is clean especially temba is a problem.h")

# Function to send the duty message
async def send_duty_message(context: ContextTypes.DEFAULT_TYPE):
    duty_message = "Today, the person on duty is: "
    
    # Get the current duty person based on the week number
    week_number = context.job.context['week_number'] % len(duty_people)
    duty_message += duty_people[week_number]
    
    # Send the message to the chat
    await context.bot.send_message(chat_id=context.job.context['chat_id'], text=duty_message)

# Schedule the duty message
async def schedule_duty_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    week_number = 0  # Initialize week number to track the duty rotation
    context.job_queue.run_repeating(send_duty_message, interval=604800, first=0, context={'chat_id': chat_id, 'week_number': week_number})
    await update.message.reply_text("Scheduled to send duty messages every Sunday!")

# Handle all text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This bot is only for cleaning updates on Sundays, not for chatting you understand bro")

def main():
    # Create an Application object
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("schedule", schedule_duty_message))
    
    # Add a message handler for all other text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()

