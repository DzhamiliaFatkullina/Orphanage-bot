from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import uuid  # Import the uuid library

# Define states for conversation
NAME, AGE, REGION, ORPHANAGE, ALUMNI = range(5)

# Dictionary to store registration details temporarily, keyed by unique ID
registration_details = {}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    unique_id = str(uuid.uuid4())  # Generate a unique ID for the user
    await update.message.reply_text(
        'Welcome Let\'s register you. What\'s your name?'
    )
    context.chat_data['unique_id'] = unique_id  # Store the unique ID in chat_data
    return NAME

# Collect name and ask for age
async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text('How old are you?')
    return AGE

# Collect age and ask for region
async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['age'] = update.message.text
    await update.message.reply_text('Which region are you from?')
    return REGION

# Collect region and ask for orphanage
async def region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['region'] = update.message.text
    await update.message.reply_text('What is the name of your orphanage?')
    return ORPHANAGE

# Collect orphanage and ask if they are alumni
async def orphanage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['orphanage'] = update.message.text
    await update.message.reply_text('Are you an alumni? (yes/no)')
    return ALUMNI

# Collect alumni status and print message
async def alumni(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['alumni'] = update.message.text.lower() in ['yes', 'y']
    unique_id = context.chat_data['unique_id']  # Retrieve the unique ID
    user_data = context.user_data
    registration_details[unique_id] = {
        'name': user_data['name'],
        'age': user_data['age'],
        'region': user_data['region'],
        'orphanage': user_data['orphanage'],
        'alumni': user_data['alumni'],
    }
    await update.message.reply_text(
        f'Thank you for registering!\n'
        f'Unique ID: {unique_id}\n'
        f'Name: {user_data["name"]}\n'
        f'Age: {user_data["age"]}\n'
        f'Region: {user_data["region"]}\n'
        f'Orphanage: {user_data["orphanage"]}\n'
        f'Alumni: {"Yes" if user_data["alumni"] else "No"}\n'
    )
    return ConversationHandler.END

# Command to cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Registration cancelled. You can start over with /start.'
    )
    return ConversationHandler.END

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("7327293440:AAEwM4CqRoz-JXsqp-lE864M45B6OaOHZ7M").build()

    # Set up conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, region)],
            ORPHANAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, orphanage)],
            ALUMNI: [MessageHandler(filters.TEXT & ~filters.COMMAND, alumni)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    # Add conversation handler to dispatcher
    application.add_handler(conv_handler)

    
    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
