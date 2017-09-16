import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, validates

from threading import Timer
from dateutil import parser

import email_scheduler
import email
import helpers
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
CORS(app)

db = SQLAlchemy(app)

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
SessionFactory = sessionmaker(bind=engine,autoflush=True,autocommit=False)
Session = flask_scoped_session(SessionFactory, app)

db.create_all()
db.session.commit()

# automaticaly schedule all pending emails on load
email_scheduler = EmailScheduler()

# define app routes

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
        task_result = email_scheduler.send(email)
        return jsonify(saved=True, scheduled=task_result, email=email.serialize)
    except ValueError as err:
        return jsonify(saved=False, scheduled=False, error=err.args)
    finally:
        Session.remove()

# execute module
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    app.run(host=host, port=port)
