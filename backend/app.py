from flask import Flask
from database import db
from models import Event, create_event, get_event, update_event, delete_event, get_all_events
from process import pars_data, encdode
from telegram import Update, ForceReply

from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from models import register_route
# Define states for conversation
# Define states for conversation
NAME, AGE, REGION, ORPHANAGE, ALUMNI, PROBLEM = range(6)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Welcome! Let\'s register you. What\'s your name?'
    )
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

# Collect alumni status and ask for problem
async def alumni(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['alumni'] = update.message.text.lower() in ['yes', 'y']
    await update.message.reply_text('What problem do you want to address?')
    return PROBLEM

# Collect problem and finish the conversation
async def problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['problem'] = update.message.text
    user_data = context.user_data
    await update.message.reply_text(
        f'Thank you for registering!\n'
        f'Name: {user_data["name"]}\n'
        f'Age: {user_data["age"]}\n'
        f'Region: {user_data["region"]}\n'
        f'Orphanage: {user_data["orphanage"]}\n'
        f'Alumni: {"Yes" if user_data["alumni"] else "No"}\n'
        f'Problem: {user_data["problem"]}'
        
    )
    register_route(NAME, AGE, REGION, ORPHANAGE, ALUMNI, PROBLEM)
    return ConversationHandler.END

# Command to cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Registration cancelled. You can start over with /start.'
    )
    return ConversationHandler.END

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("7305786297:AAFzC93nebvp7obQOl3NFOx634AnFOHzwyo").build()

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

    # Start the Bot
    application.run_polling()
    app.run()
    #app.app_context()


def perform_database_operations():
    with app.app_context():
        # Now you can perform database operations within this context
        # For example, creating a new event
        event = Event(name='John', age=25, region='XYZ', orphanage='ABC', alumni='Yes', problem='None')
        db.session.add(event)
        db.session.commit()

if __name__ == '__main__':
    #perform_database_operations()
    main()





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
