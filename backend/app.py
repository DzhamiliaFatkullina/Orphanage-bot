from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from telegram import Update, Bot
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

# Function to send a message to the target chat
async def send_message_to_chat(message: str):
  await  bot.send_message(chat_id=TARGET_CHAT_ID, text=message)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global my_chat_id,TARGET_CHAT_ID
    my_chat_id = update.message.chat_id
    TARGET_CHAT_ID = my_chat_id
    await update.message.reply_text(f'Your chat ID is: {my_chat_id}')
    #await update.message.reply_text('Welcome! Let\'s register you. What\'s your name?')
    return NAME

# Collect name and ask for age
async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user_id'] = update.message.from_user.id
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

# Collect alumni status and ask for problem
async def alumni(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['alumni'] = update.message.text.lower() in ['yes', 'y']
    await update.message.reply_text('What problem do you want to address?')
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
        f'Thank you for registering!\n'
        f'Name: {user_data["name"]}\n'
        f'Age: {user_data["age"]}\n'
        f'Region: {user_data["region"]}\n'
        f'Orphanage: {user_data["orphanage"]}\n'
        f'Alumni: {"Yes" if user_data["alumni"] else "No"}\n'
        f'Problem: {user_data["problem"]}'
    )

    # Retrieve and send the event data
    #event_data_message = get_event_data()
    await send_message_to_chat("hello from the app ")

    return ConversationHandler.END

# Command to cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Registration cancelled. You can start over with /start.')
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

    # Start the Telegram bot in a separate thread
    loop = asyncio.get_event_loop()
    loop.create_task(application.run_polling())

    # Run the Flask app
    app.run(debug=True)

if __name__ == '__main__':
    main()




















#-------------------------------------------------------------
# from flask import Flask
# from database import db
# from models import Event, create_event, get_event, update_event, delete_event, get_all_events
# from process import pars_data, encdode
# from telegram import Update, ForceReply

# from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
# from models import register_route
# # Define states for conversation
# # Define states for conversation
# NAME, AGE, REGION, ORPHANAGE, ALUMNI, PROBLEM = range(6)
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
# #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)


# # Start command handler
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     await update.message.reply_text(
#         'Welcome! Let\'s register you. What\'s your name?'
#     )
#     return NAME

# # Collect name and ask for age
# async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     context.user_data['name'] = update.message.text
#     await update.message.reply_text('How old are you?')
#     return AGE

# # Collect age and ask for region
# async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     context.user_data['age'] = update.message.text
#     await update.message.reply_text('Which region are you from?')
#     return REGION

# # Collect region and ask for orphanage
# async def region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     context.user_data['region'] = update.message.text
#     await update.message.reply_text('What is the name of your orphanage?')
#     return ORPHANAGE

# # Collect orphanage and ask if they are alumni
# async def orphanage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     context.user_data['orphanage'] = update.message.text
#     await update.message.reply_text('Are you an alumni? (yes/no)')
#     return ALUMNI

# # Collect alumni status and ask for problem
# async def alumni(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     context.user_data['alumni'] = update.message.text.lower() in ['yes', 'y']
#     await update.message.reply_text('What problem do you want to address?')
#     return PROBLEM

# # Collect problem and finish the conversation
# async def problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     context.user_data['problem'] = update.message.text
#     user_data = context.user_data
#     await update.message.reply_text(
#         f'Thank you for registering!\n'
#         f'Name: {user_data["name"]}\n'
#         f'Age: {user_data["age"]}\n'
#         f'Region: {user_data["region"]}\n'
#         f'Orphanage: {user_data["orphanage"]}\n'
#         f'Alumni: {"Yes" if user_data["alumni"] else "No"}\n'
#         f'Problem: {user_data["problem"]}'
        
#     )
#     register_route(NAME, AGE, REGION, ORPHANAGE, ALUMNI, PROBLEM)
#     return ConversationHandler.END

# # Command to cancel the conversation
# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     await update.message.reply_text(
#         'Registration cancelled. You can start over with /start.'
#     )
#     return ConversationHandler.END

# def main() -> None:
#     # Create the Application and pass it your bot's token.
#     application = Application.builder().token("7305786297:AAFzC93nebvp7obQOl3NFOx634AnFOHzwyo").build()

#     # Set up conversation handler with the states
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler('start', start)],
#         states={
#             NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
#             AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
#             REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, region)],
#             ORPHANAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, orphanage)],
#             ALUMNI: [MessageHandler(filters.TEXT & ~filters.COMMAND, alumni)],
#             PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, problem)],
#         },
#         fallbacks=[CommandHandler('cancel', cancel)],
#     )

#     # Add conversation handler to dispatcher
#     application.add_handler(conv_handler)

#     # Start the Bot
#     application.run_polling()
#     app.run()
#     #app.app_context()


# def perform_database_operations():
#     with app.app_context():
#         # Now you can perform database operations within this context
#         # For example, creating a new event
#         event = Event(name='John', age=25, region='XYZ', orphanage='ABC', alumni='Yes', problem='None')
#         db.session.add(event)
#         db.session.commit()

# if __name__ == '__main__':
#     #perform_database_operations()
#     main()


#----------------------------------------------


# from flask import Flask, jsonify, request
# #from flask_cors import CORS  # Import CORS

# from database import db
# from models import Event, create_event, get_event, update_event, delete_event, get_all_events
# from process import pars_data, encdode

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)
# #CORS(app)  # Add this line to enable CORS for your Flask app
# @app.route('/register', methods=['POST'])
# def register_route():
#     data = request.json
#     data = pars_data(data)
    
#     event = create_event(**data)
#     return jsonify(event), 201


# @app.route('/create', methods=['POST'])
# def create_event_route():
#     data = request.json
#     data = pars_data(data)
    
#     event = create_event(**data)
#     return jsonify(event), 201

# @app.route('/get/<int:event_id>', methods=['GET'])
# def get_event_route(event_id):
#     event = get_event(event_id)
#     if event:
#         event_dict = encdode(event)
#         return jsonify(event_dict)
#     else:
#         return jsonify({'message': 'Event not found'}), 404

# @app.route('/update/<int:event_id>', methods=['PUT'])
# def update_event_route(event_id):
#     data = request.json
#     data = pars_data(data)
#     update_event(event_id, **data)
#     return '', 204

# @app.route('/delete/<int:event_id>', methods=['DELETE'])  # Fixed the route path here
# def delete_event_route(event_id):
#     delete_event(event_id)
#     return '', 204

# @app.route('/get', methods=['GET'])
# def get_all_events_route():
#     events = get_all_events()
#     return jsonify(events)

# if __name__ == '__main__':
#     app.run(debug=True)
