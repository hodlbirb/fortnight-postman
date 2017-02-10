import helpers
from threading import Timer
import db_conn
from models import Email


#
# class: EmailSender
# Description: Scheduling emails by timestamp and load pending form db
#

class EmailSender:
    def __init__(self):
        self.schedulePendingEmails()

    def schedulePendingEmails(self):
        print('Scheduling pending emails...')
        session = db_conn.Session()
        # retrieve not sent emails from db
        pending_emails = session.query(Email).filter(Email.sent==False).all()
        for e in pending_emails:
            seconds = helpers.seconds_from_now(e.timestamp)
            if seconds > 0:
                # email's timestamp is not expired
                Timer(seconds, self.post, args=[e]).start()
                print("Scheduled " + str(e))
        db_conn.Session.remove()

    def send(self, email):
        seconds = helpers.seconds_from_now(email.timestamp)
        if seconds < 0:
            # email's timestamp is expired
            return False
        else:
            Timer(seconds, self.post, args=[email]).start()
            return True

    def post(self, email):
        session = db_conn.Session()
        session.add(email)
        email.sent = True
        session.commit()
        print("Sending to " + str(email))
        db_conn.Session.remove()
