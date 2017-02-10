from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask.ext.sqlalchemy import SQLAlchemy

import config
from email_sender import EmailSender

app = Flask(__name__)
app.config.from_object(config.APP_SETTINGS)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
db = SQLAlchemy(app)

from models import Email

CORS(app)

# automaticaly schedule all pending emails on load
sender = EmailSender()

@app.route('/emails', methods=['GET'])
def get_emails():
    sess = db_conn.Session()
    emails = sess.query(Email).all()
    db_conn.Session.remove()
    return jsonify(email_list=[e.serialize for e in emails])

# save emails to db and queue them
@app.route('/save_emails', methods=['POST'])
def save():
    sess = db_conn.Session()
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
        db_conn.Session.remove()

if __name__ == '__main__':
    app.run(debug=True)
