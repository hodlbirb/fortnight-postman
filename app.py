from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, validates

from threading import Timer
from dateutil import parser

import helpers
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
CORS(app)

db = SQLAlchemy(app)

#
# class: EmailSender
# Description: Scheduling emails by timestamp and load pending form db
#


class EmailSender:
    def __init__(self):
        self.schedulePendingEmails()

    def schedulePendingEmails(self):
        print('Scheduling pending emails...')
        session = Session()
        # retrieve not sent emails from db
        pending_emails = session.query(Email).filter(Email.sent==False).all()
        for e in pending_emails:
            seconds = helpers.seconds_from_now(e.timestamp)
            if seconds > 0:
                # email's timestamp is not expired
                Timer(seconds, self.post, args=[e]).start()
                print("Scheduled " + str(e))
        Session.remove()

    def send(self, email):
        seconds = helpers.seconds_from_now(email.timestamp)
        if seconds < 0:
            # email's timestamp is expired
            return False
        else:
            Timer(seconds, self.post, args=[email]).start()
            return True

    def post(self, email):
        session = Session()
        session.add(email)
        email.sent = True
        session.commit()
        print("Sending to " + str(email))
        Session.remove()


#
# class: Email
# Description: Descibes email model
#


class Email(db.Model):
    __tablename__ = 'email'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(255), default="")
    content = db.Column(db.Text(), default="")
    timestamp = db.Column(db.String(255), nullable=False)
    sent = db.Column(db.Boolean, default=False)

    def __init__(self, event_id, subject, content, timestamp):
        self.event_id = event_id
        self.subject = subject
        self.content = content
        self.timestamp = timestamp

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def __str__(self):
        return 'event id: {0}, subject: {1}, on: {2}'.format(self.event_id,self.subject,self.timestamp)

    @property
    def serialize(self):
       """Return object data in serializeable format"""
       return {
           'id': self.id,
           'event_id': self.event_id,
           'subject': self.subject,
           'content': self.content,
           'timestamp': self.timestamp,
           'sent': self.sent
       }

    @validates('timestamp')
    def validate_timestamp(self, key, ts):
        ts_str = ""
        try:
            ts_str = str(helpers.to_utc(parser.parse(ts)))
        except ValueError:
            raise ValueError("Invalid timestamp format")
        is_exp = helpers.seconds_from_now(ts_str) < 0
        if is_exp:
            raise ValueError("Timestamp is expired")
        return ts_str


db.create_all()
db.session.commit()

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
SessionFactory = sessionmaker(bind=engine,autoflush=True,autocommit=False)
Session = flask_scoped_session(SessionFactory, app)


# automaticaly schedule all pending emails on load
sender = EmailSender()

#
# Define app routes
#

# retrieve emails from db
@app.route('/emails', methods=['GET'])
def get_emails():
    sess = Session()
    emails = sess.query(Email).all()
    Session.remove()
    return jsonify(email_list=[e.serialize for e in emails])

# save emails to db and queue them
@app.route('/save_emails', methods=['POST'])
def save():
    sess = Session()
    args = request.args
    event_id = args['event_id']
    subject = args['email_subject']
    content = args['email_content']
    timestamp = args['timestamp']

    try:
        email = Email(event_id=event_id,
                subject=subject,
                content=content,
                timestamp=timestamp)
        sess.add(email)
        sess.commit()
        return jsonify(saved=True, scheduled=sender.send(email), email=email.serialize)
    except ValueError as err:
        return jsonify(saved=False, scheduled=False, error=err.args)
    finally:
        Session.remove()


#
# execute module
#

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    app.run(host=host, port=port)
