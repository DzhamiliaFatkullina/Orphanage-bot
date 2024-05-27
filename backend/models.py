from database import db
from process import encdode
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.String(50))
    region = db.Column(db.String(50))
    orphanage = db.Column(db.String(100))
    alumni = db.Column(db.String(100))
    problem = db.Column(db.String(100))

    def __repr__(self):
        return f"<Event {self.id}: >"
    
#register_route

def register_route(name, age, region, orphanage, alumni,problem):
    
    event = Event(name=name, age=age, region=region, orphanage=orphanage,
                    alumni=alumni, problem=problem)
    try:
        db.session.add(event)
    except Exception as e:
        print(f'str1{e}')
    try:    
        db.session.commit()
        #event_dict = encdode(event)
        # event_dict = {
        #         'id': event.id,
        #         'title': event.title,
        #         'start': event.start_time,
        #         'end': event.end_time,

        #         "extendedProps": {
        #             "room": event.room,
        #             "course": event.target_course,
        #             "group":  event.target_group,
        #             "instructorName":  event.instructor
        #         }
                
        #     }

        #return event_dict
    except Exception as e:
        print(f'str2{e}')

def create_event(title, start, end, instructorName, room, course, group):
    event = Event(title=title, start_time=start, end_time=end, instructor=instructorName,
                  room=room, target_course=course, target_group=group)
    db.session.add(event)
    db.session.commit()
    event_dict = encdode(event)
  

    return event_dict

def get_event(event_id):
    return Event.query.get(event_id)

def update_event(id,title, start, end, instructorName, room, course, group):
    event = Event.query.get(id)
    event.title = title
    event.start_time = start
    event.end_time = end
    event.instructor = instructorName
    event.room = room
    event.target_course = course
    event.target_group = group
    db.session.commit()

def delete_event(event_id):
    event = Event.query.get(event_id)
    db.session.delete(event)
    db.session.commit()

def get_all_events():
    events_json = []
    events = Event.query.all()

    # Serialize each Event object into a dictionary representation
    for event in events:
        event_dict = encdode(event)
        # event_dict = {
        #     'id': event.id,
        #     'title': event.title,
        #     'start': event.start_time,
        #     'end': event.end_time,

        #     "extendedProps": {
        #         "room": event.room,
        #         "course": event.target_course,
        #         "group":  event.target_group,
        #         "instructorName":  event.instructor
        #     }
            
        # }
        events_json.append(event_dict)

    # jsonify the list of dictionaries
    return events_json
    #eturn Event.query.all()
# {
#   "title": "string",
#   "start": "string",
#   "end": "string",
#   "extendedProps": {
#     "room": "",
#     "course": "",
#     "group": "",
#     "instructorName": ""
#   }
# }




