# class: EmailScheduler
# Description: Scheduling emails by timestamp and load pending form db

class EmailScheduler:
    def __init__(self):
        self.schedulePendingEmails()

    def schedulePendingEmails(self):
        session = Session()
        # retrieve not sent emails from db
        print('Retrieving pending emails...')
        pending_emails = session.query(Email).filter(Email.sent==False).all()
        print('Scheduling pending emails...')
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
            print("Scheduling email...")
            Timer(seconds, self.post, args=[email]).start()
            return True

    def post(self, email):
        session = Session()
        session.add(email)
        email.sent = True
        session.commit()
        print("Sending to " + str(email))
        Session.remove()
