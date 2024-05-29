from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from telegram import Update, Bot
from telegram.ext import CallbackQueryHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import asyncio

# Initialize SQLAlchemy without an application context
db = SQLAlchemy()
my_chat_id = None
# Define your models
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)  # Using user_id as the primary key
    user_id = db.Column(db.Integer)
    name = db.Column(db.String)
    age = db.Column(db.Integer)
    region = db.Column(db.String)
    orphanage = db.Column(db.String)
    alumni = db.Column(db.Boolean)
    problem = db.Column(db.String)

# Application factory function
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'  # Replace with your database URI
    db.init_app(app)
    return app

app = create_app()

# Ensure the database is created
with app.app_context():
    db.create_all()

# Define conversation states
NAME, AGE, REGION, ORPHANAGE, ALUMNI, PROBLEM = range(6)

# Define the bot token and the target chat ID

BOT_TOKEN = "7305786297:AAFzC93nebvp7obQOl3NFOx634AnFOHzwyo"
#admin id 
TARGET_CHAT_ID = "TARGET_CHAT_ID"

# Initialize the bot
bot = Bot(token=BOT_TOKEN)


# def user_id_exists(user_id):
#     # Query the Event table for the specified user_id
#     existing_event = Event.query.filter_by(user_id=user_id).first()
    
#     # Check if an event with the specified user_id exists
#     if existing_event:
#         return True
#     else:
#         return False

# Function to retrieve and format event data
def get_event_data():
    with app.app_context():
        events = Event.query.all()
        if not events:
            return "No events found."
        
        event_messages = []
        for event in events:
            message = (
                f"User ID: {event.user_id}\n"
                f"Name: {event.name}\n"
                f"Age: {event.age}\n"
                f"Region: {event.region}\n"
                f"Orphanage: {event.orphanage}\n"
                f"Alumni: {'Yes' if event.alumni else 'No'}\n"
                f"Problem: {event.problem}\n"
                "-------------------\n"
            )
            event_messages.append(message)
        
        return "\n".join(event_messages)
#-------------------not working good ----------------------------

#this code sends buttons but doesn't respond to it. Should be a quick fix, maybe use AI. Im stuck.

# Define states for conversation
REQUEST_TYPE, SUBMIT_PROBLEM, VERIFY_PROBLEM = range(3)

# Function to build the keyboard for request types
def build_request_buttons():
    keyboard = [
        [InlineKeyboardButton("Мне нужна помощь психолога", callback_data='psy')],
        [InlineKeyboardButton("Мне нужна помощь юриста", callback_data='law')],
        [InlineKeyboardButton("Мне нужен репетитор", callback_data='tut')],
        [InlineKeyboardButton("Мне нужна работа", callback_data='work')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Handler to start the conversation and send the request type options
async def send_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Как ты думаешь, кто тебе может помочь?", reply_markup=build_request_buttons())
    return REQUEST_TYPE

# Handler to process the button press and ask for the problem description
async def button_pressed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['request_type'] = query.data  # Store the selected request type
    await query.edit_message_text(text="Опиши свою проблему")
    return SUBMIT_PROBLEM

# Handler to capture the problem description from the user
async def submit_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    problem = update.message.text
    context.user_data['problem'] = problem
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Тип запроса: {context.user_data['request_type']}\nПроблема: {problem}\nВсе верно? (да или /cancel)")
    return VERIFY_PROBLEM

# Handler to verify and save the problem description
async def verify_and_save_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    verified = update.message.text.lower() == 'да'
    if verified:
        user_id = update.message.from_user.id  # Get user ID from the message
        if user_id:
            user_data = context.user_data
    
                        # Perform the database operation within the Flask app context
            with app.app_context():
                user_id = update.message.from_user.id
                existing_event = Event.query.filter_by(user_id=user_id).first()
                if existing_event:
                    print("User ID exists in the database.")
                else:
                    print("User ID does not exist in the database.")
                try:
                    user =await bot.get_chat_member(chat_id=user_id, user_id=user_id)
                    if user.user.username:
                        print( user.user.username)
                        await send_message_to_chat(user.user.username)

                    else:
                        print( "User doesn't have a username.")
                except Exception as e:
                    print( f"Error: {e}")

                new_event = Event(
                    user_id=existing_event.user_id,
                    name=existing_event.name,
                    age=existing_event.age,
                    region=existing_event.region,
                    orphanage=existing_event.orphanage,
                    alumni=existing_event.alumni,
                    problem=user_data['problem']
                )
                db.session.add(new_event)
                db.session.commit()

            # await update.message.reply_text(
            #     f'Thank you for registering!\n'
            #     f'Name: {user_data["name"]}\n'
            #     f'Age: {user_data["age"]}\n'
            #     f'Region: {user_data["region"]}\n'
            #     f'Orphanage: {user_data["orphanage"]}\n'
            #     f'Alumni: {"Yes" if user_data["alumni"] else "No"}\n'
            #     f'Problem: {user_data["problem"]}'
            # )

            # Retrieve and send the event data
            #event_data_message = get_event_data()
            #await send_message_to_chat("hello from the app ")
            # Save problem to the database (function to be implemented)
            # save_problem_to_database(user_id, context.user_data['problem'])  # TODO: Implement this function
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Мы сохранили ваш запрос. С вами свяжутся! Новый запрос можно отправить использовав команду /send_request")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Я не распознал ваш ID :(.  Вы уверены что вы зарегестрировались?")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Я вас не понял :(. Пожалуйста попробуйте еще раз. (да или /cancel)")
    return ConversationHandler.END  # End the conversation

# this is a dublicate, dont need this
# Handler to cancel the request
# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     await update.message.reply_text('Запрос был отменет. Если хотите попробовать еще раз нажмите /send_request.')
#     return ConversationHandler.END



#--------------------not working good ----------------------------


async def help_command(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text('''
Привет, я бот для отправки запросов волонтерам. Я распознаю следующие команды:
/start - Начать общаться, регистрация
/send_request - Отправить запрос
/report_error - Сообщить об ошибке бота
/cancel - Отменить запрос                                   
/help - Посмотреть доступные команды
''')
    


REPORT_PROBLEM = range(1)

# Function to handle the /report_error command
async def report_error(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Сообщи о проблеме")
    return REPORT_PROBLEM

# Function to handle the user's response
async def handle_problem(update: Update, context: CallbackContext):
    problem = update.message.text
    # Process the problem or save it to a database
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо, я направил сообщение админу.")
    return ConversationHandler.END



# Function to send a message to the target chat
async def send_message_to_chat(message: str):
  await  bot.send_message(chat_id=TARGET_CHAT_ID, text=message)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global my_chat_id,TARGET_CHAT_ID
    my_chat_id = update.message.chat_id
    TARGET_CHAT_ID = my_chat_id
    #await update.message.reply_text(f'Your chat ID is: {my_chat_id}')
    await update.message.reply_text('Welcome! Let\'s register you. What\'s your name?')
    return NAME

# Collect name and ask for age
async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user_id'] = update.message.from_user.id
    context.user_data['name'] = update.message.text
    await update.message.reply_text('Сколько тебе лет?')
    return AGE

# Collect age and ask for region
async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['age'] = update.message.text
    await update.message.reply_text('Из какого ты региона России?')
    return REGION

# Collect region and ask for orphanage
async def region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['region'] = update.message.text
    await update.message.reply_text('Ты из интерната или деткого дома?')
    return ORPHANAGE

# Collect orphanage and ask if they are alumni
async def orphanage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['orphanage'] = update.message.text
    await update.message.reply_text('Являешься ли ты выпускником интерната или деткого дома? (да/нет)')
    return ALUMNI

# Collect alumni status and ask for problem
async def alumni(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['alumni'] = update.message.text.lower() in ['да', 'д']
    await update.message.reply_text('Расскажи о своей проблеме')
    return PROBLEM

# Collect problem and finish the conversation
async def problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['problem'] = update.message.text
    user_data = context.user_data
    
    

    # Perform the database operation within the Flask app context
    with app.app_context():
        user_id = update.message.from_user.id
        existing_event = Event.query.filter_by(user_id=user_id).first()
        if existing_event:
            print("User ID exists in the database.")
        else:
            print("User ID does not exist in the database.")
        try:
            user =await bot.get_chat_member(chat_id=user_id, user_id=user_id)
            if user.user.username:
                print( user.user.username)
                await send_message_to_chat(user.user.username)

            else:
                print( "User doesn't have a username.")
        except Exception as e:
            print( f"Error: {e}")

        new_event = Event(
            user_id=update.message.from_user.id,
            name=user_data['name'],
            age=user_data['age'],
            region=user_data['region'],
            orphanage=user_data['orphanage'],
            alumni=user_data['alumni'],
            problem=user_data['problem']
        )
        db.session.add(new_event)
        db.session.commit()

    await update.message.reply_text(
        f'Спасибо за регистрацию!\n'
        f'Имя: {user_data["name"]}\n'
        f'Возраст: {user_data["age"]}\n'
        f'Регион: {user_data["region"]}\n'
        f'Интернат или детский дом: {user_data["orphanage"]}\n'
        f'Выпускник или нет: {"Да" if user_data["alumni"] else "Нет"}\n'
        f'Запрос: {user_data["problem"]}'
    )

    # Retrieve and send the event data
    #event_data_message = get_event_data()
    #await send_message_to_chat("hello from the app ")

    return ConversationHandler.END

# Command to cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Запрос отменен. Используйте команду /help чтобы увидеть доступные команды')
    return ConversationHandler.END

def main():
    # Create the Telegram bot application
    application = Application.builder().token(BOT_TOKEN).build()

    # Set up conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, region)],
            ORPHANAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, orphanage)],
            ALUMNI: [MessageHandler(filters.TEXT & ~filters.COMMAND, alumni)],
            PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, problem)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )


    # Add conversation handler to dispatcher
    application.add_handler(conv_handler)
    help_handler = CommandHandler('help', help_command)

    # Add the help command handler to the application
    application.add_handler(help_handler)





    conv_report_error = ConversationHandler(
    entry_points=[CommandHandler('report_error', report_error)],
    states={
        REPORT_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_problem)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]  # Implement cancel logic if needed
)

    application.add_handler(conv_report_error)

#------------------------------------------------------

    # Define the conversation handler with the states and fallbacks
    conv_handler_request = ConversationHandler(
        entry_points=[CommandHandler('send_request', send_request)],
        states={
            REQUEST_TYPE: [CallbackQueryHandler(button_pressed)],
            SUBMIT_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_problem)],
            VERIFY_PROBLEM: [MessageHandler(filters.Regex('^(yes|no)$'), verify_and_save_problem)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_user=False  # Track the conversation per user instead of per message
        #per_message=True
    )

    application.add_handler(conv_handler_request)

    
#---------------------------------------------------------

    # Start the Telegram bot in a separate thread
    loop = asyncio.get_event_loop()
    loop.create_task(application.run_polling())

    # Run the Flask app
    app.run(debug=True)

if __name__ == '__main__':
    main()

