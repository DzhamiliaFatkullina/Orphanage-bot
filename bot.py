from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import uuid  # Import the uuid library
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CallbackContext

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

import json

USER_DATA_FILE = 'user_data.json'

def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file)


async def help_command(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text('''
Hello I am your friendly bot. Here's how you can use me:
/start - Start chatting with the bot, set up profile
/set_profile - Set up profile, usually chage info, but not ID
/send_request - choose type of request and share problem
/report_error - let developers know what goes wrong
/cancel - at any point you can cancel whatever you are doing
and start over with a new command                                   
/help - Get help on how to use me.
''')



# Define states for conversation
NAME, AGE, REGION, ORPHANAGE, ALUMNI = range(5)

# Dictionary to store registration details temporarily, keyed by unique ID
registration_details = {}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    unique_id = str(uuid.uuid4())  # Generate a unique ID for the user
    
    # # Load existing user data from the file
    # existing_data = load_user_data()
    
    # # Check if the user is already registered
    # if unique_id in existing_data:
    #     await update.message.reply_text(
    #         "It looks like you've already registered. You can change your data, if you don't want to press /cancel"
    #     )
    #     # Proceed to the NAME state to allow the user to update their information
    #     return NAME
    # else:

    # add tab when this is tested
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

    # save_user_data(registration_details) # save to db

    await update.message.reply_text(
        f'Thank you for registering!\n'
        f'Unique ID: {unique_id}\n'
        f'Name: {user_data["name"]}\n'
        f'Age: {user_data["age"]}\n'
        f'Region: {user_data["region"]}\n'
        f'Orphanage: {user_data["orphanage"]}\n'
        f'Alumni: {"Yes" if user_data["alumni"] else "No"}\n'
    )
    await update.message.reply_text(
        f'Use /send_request to send a request. If you want something else see /help.'
    )

    return ConversationHandler.END

# Command to cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Action cancelled. You can start over by sending the command once again or use /help to se menu.'
    )
    return ConversationHandler.END

#this code sends buttons but doesn't respond to it. Should be a quick fix, maybe use AI. Im stuck.

# Define states for conversation
REQUEST_TYPE, SUBMIT_PROBLEM, VERIFY_PROBLEM = range(3)

# array of commands for /send_request
def build_request_buttons():
    keyboard = [
        [InlineKeyboardButton("Request Type 1", callback_data='type1')],
        [InlineKeyboardButton("Request Type 2", callback_data='type2')],
        [InlineKeyboardButton("Request Type 3", callback_data='type3')],
        [InlineKeyboardButton("Request Type 4", callback_data='type4')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_request(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose type of request", reply_markup=build_request_buttons())



async def button_pressed(update, context):
    query = update.callback_query
    query.answer()
    # Edit the original message to prompt the user to submit a problem
    await query.edit_message_text(text="Please write your problem.")
    # Return the next state
    return SUBMIT_PROBLEM


async def submit_problem(update, context):
    problem = update.message.text
    context.user_data['problem'] = problem
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Type of Request: {context.user_data['request_type']}\nProblem: {problem}\nIs this correct?(y/n)")
    return VERIFY_PROBLEM


async def verify_and_save_problem(update, context):
    verified = update.message.text.lower() == 'y'
    if verified:
        # Extract user_id from context or update; this depends on how you manage user IDs
        user_id = context.user_data.get('user_id')
        if user_id:
            # save_problem_to_database(user_id, context.user_data['problem']) #TODO 
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Your problem has been successfully saved.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="User ID not found. Please try again.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I didn't undersrand you :(. Please verify the problem again.(y/n)")


# #second time I tried, this time don't care if I understand what is going on
# # Placeholder for the database simulation
# problems_db = {}

# import logging
# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)


# def send_request(update: Update, context: CallbackContext) -> int:
#     try:
#         query = update.callback_query
#         if query is None:
#             logger.error("Received an update without a callback query.")
#             update.message.reply_text("It seems there was an issue with your request. Please try again.")
#             return ConversationHandler.END
#         query.answer()
        
#         keyboard = [
#             [InlineKeyboardButton(request_type, callback_data=request_type) for request_type in ["Type 1", "Type 2", "Type 3", "Type 4"]]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)
        
#         update.message.reply_text('Choose type of request:', reply_markup=reply_markup)
        
#         return REQUEST_TYPE
#     except ValueError as e:
#         logger.error(f"An error occurred in send_request: {e}")
#         update.message.reply_text("There was an error processing your request. Please try again.")
#         return ConversationHandler.END

# def button_pressed(update: Update, context: CallbackContext) -> int:
#     try:
#         query = update.callback_query
#         if query is None:
#             raise ValueError("Callback query is None")
        
#         query.answer()
        
#         selected_type = query.data
#         query.edit_message_text(text=f"You selected {selected_type}. Please write your problem.")
        
#         return SUBMIT_PROBLEM
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         update.message.reply_text("There was an error processing your request. Please try again.")
#         return ConversationHandler.END

# def submit_problem(update: Update, context: CallbackContext) -> int:
#     user_id = update.effective_user.id
#     problem = update.message.text
    
#     # Simulate saving the problem to a database
#     problems_db[user_id] = problem
    
#     return VERIFY_PROBLEM

# def verify_and_save_problem(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     verified = update.message.text.lower() == 'yes'
    
#     if verified:
#         # Simulate saving the problem as verified
#         problems_db[user_id] = "Verified Problem"
    
#     update.message.reply_text("Problem has been saved.")
    
#     return ConversationHandler.END


REPORT_PROBLEM = range(1)

# Function to handle the /report_error command
async def report_error(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="What is the problem?")
    return REPORT_PROBLEM

# Function to handle the user's response
async def handle_problem(update: Update, context: CallbackContext):
    problem = update.message.text
    # Process the problem or save it to a database
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for reporting the problem.")
    return ConversationHandler.END

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("7327293440:AAEwM4CqRoz-JXsqp-lE864M45B6OaOHZ7M").build()

    # Set up conversation handler with the states
    conv_handler_registration = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('set_profile', start)],
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
    application.add_handler(conv_handler_registration)

    # Create the help command handler
    help_handler = CommandHandler('help', help_command)

    # Add the help command handler to the application
    application.add_handler(help_handler)

    #send request conversation handler
    conv_handler_request = ConversationHandler(
    entry_points=[CommandHandler('send_request', send_request)],
    states={
        REQUEST_TYPE: [CallbackQueryHandler(button_pressed)],
        SUBMIT_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_problem)],
        VERIFY_PROBLEM: [MessageHandler(filters.Regex('^yes$|^no$'), verify_and_save_problem)]
    },
    fallbacks=[CommandHandler('cancel', cancel)] 
    )

    application.add_handler(conv_handler_request)

    conv_report_error = ConversationHandler(
    entry_points=[CommandHandler('report_error', report_error)],
    states={
        REPORT_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_problem)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]  # Implement cancel logic if needed
)

    application.add_handler(conv_report_error)
    
    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
