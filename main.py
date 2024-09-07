import os
import re

from edupage_api import Edupage
from edupage_api.exceptions import BadCredentialsException
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()

EDUPAGE_USERNAME = os.getenv("EDUPAGE_USERNAME")
EDUPAGE_PASSWORD = os.getenv("EDUPAGE_PASSWORD")
EDUPAGE_SCHOOL_SUBDOMAIN = os.getenv("EDUPAGE_SCHOOL_SUBDOMAIN")

edupage = Edupage()

try:
    edupage.login(EDUPAGE_USERNAME, EDUPAGE_PASSWORD, EDUPAGE_SCHOOL_SUBDOMAIN)
except BadCredentialsException:
    print("Wrong username or password!")
    exit()
    

class MyRingingTime:
    def __init__(self):
        self.ringing_time_str = str(self.get_next_ringing_time_now())
        self.datetime = self.parse_datetime(self.ringing_time_str)
    
    def get_next_ringing_time_now(self):
        now = datetime.now()
        return edupage.get_next_ringing_time(now)

    def parse_datetime(self, ringing_time_str):
        match = re.search(r"datetime\.datetime\(([\d, ]+)\)", ringing_time_str)
        
        if match:
            datetime_values = match.group(1).split(", ")
            date = datetime(
                year=int(datetime_values[0]),
                month=int(datetime_values[1]),
                day=int(datetime_values[2]),
                hour=int(datetime_values[3]),
                minute=int(datetime_values[4])
            )
            return date
        else:
            return None

    def __str__(self):
        return self.datetime.strftime("%A, %d %B %Y at %I:%M %p")

# ringing_time = MyRingingTime()
# print(ringing_time)

date_after_tomorrow = datetime.now() + timedelta(days=2)

print(edupage.get_my_timetable(date_after_tomorrow))