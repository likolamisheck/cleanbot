from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram Bot Token
TELEGRAM_TOKEN = '7061540516:AAFot-pHmGVk5ibgOsWvs1MRc1ksx-6Fylo'

# List of people on duty
duty_people = ["Kasakula", "Milimo", "Temba", "Likola"]

# Function to send the duty message
async def send_duty_message(context: ContextTypes.DEFAULT_TYPE):
    # Get the current week number and rotate through the duty list
    week_number = context.job.context['week_number']
    duty_message = f"Today, the person on duty is: {duty_people[week_number % len(duty_people)]}"
    
    # Send the message to the chat
    await context.bot.send_message(chat_id=context.job.context['chat_id'], text=duty_message)

    # Update the week number for the next rotation
    context.job.context['week_number'] += 1

# Calculate when the next Sunday is, for 12:00 AM
def next_sunday_midnight():
    today = datetime.now()
    days_ahead = 6 - today.weekday()  # Sunday is day 6
    if days_ahead <= 0:  # Target next Sunday if it's today or past Sunday this week
        days_ahead += 7
    next_sunday = today + timedelta(days_ahead)
    return next_sunday.replace(hour=0, minute=0, second=0, microsecond=0)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create an inline button
    button = InlineKeyboardButton("Who's on duty?", callback_data="duty_info")
    keyboard = InlineKeyboardMarkup([[button]])

    # Send a message with the button
    await update.message.reply_text(
        "click the button  bellow to check who's on duty! ",
        reply_markup=keyboard
    )

# Handle button press (callback query)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Get the current week number based on rotation
    week_number = context.user_data.get('week_number', 0)  # Default to 0 if not scheduled yet
    current_duty_person = duty_people[week_number % len(duty_people)]
    
    # Send a message with the current duty person
    await query.edit_message_text(f"This week is for {current_duty_person}.")

# Schedule the duty message
async def schedule_duty_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    week_number = 0  # Initialize week number to track the duty rotation
    
    # Calculate the timestamp for next Sunday at 12:00 AM
    next_sunday_time = next_sunday_midnight()

    # Schedule the job to run every Sunday at 12:00 AM
    context.job_queue.run_repeating(
        send_duty_message, interval=604800, first=next_sunday_time, 
        context={'chat_id': chat_id, 'week_number': week_number}
    )
    
    # Store week_number in user_data to access later in button callback
    context.user_data['week_number'] = week_number

    await update.message.reply_text("Scheduled to send duty messages every Sunday at 12:00 AM!")

# Handle all text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("click here /start to see who is on duty .This bot is only for cleaning updates on Sundays, not for chatting. click here to see who is on duty /start")

def main():
    # Create an Application object
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("schedule", schedule_duty_message))

    # Add callback query handler for button presses
    app.add_handler(CallbackQueryHandler(button_callback))

    # Add a message handler for all other text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()

