import pytz
import datetime


def get_tashkent_time():
    utc_now = datetime.datetime.utcnow()
    tashkent_tz = pytz.timezone('Asia/Tashkent')
    tashkent_time = utc_now.replace(tzinfo=pytz.utc).astimezone(tashkent_tz)
    return tashkent_time