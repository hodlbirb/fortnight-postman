import datetime
from dateutil import parser
import pytz

utc = pytz.utc

def seconds_from_now(dt_str):
    dt = parser.parse(dt_str)
    sec = (to_utc(dt) - utcnow()).total_seconds()
    return sec

def to_utc(dt):
    try:
        return utc.localize(dt)
    except:
        return utc.normalize(dt)

def utcnow():
    return datetime.datetime.now(tz=utc)
