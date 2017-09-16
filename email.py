# class: Email
# Description: Descibes email model

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
