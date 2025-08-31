import os

from edupage_api import *
from edupage_api.exceptions import *

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

EDUPAGE_USERNAME = os.getenv("EDUPAGE_USERNAME")
EDUPAGE_PASSWORD = os.getenv("EDUPAGE_PASSWORD")
EDUPAGE_SCHOOL_SUBDOMAIN = os.getenv("EDUPAGE_SCHOOL_SUBDOMAIN")

edupage = Edupage()

try:
    edupage.login(EDUPAGE_USERNAME, EDUPAGE_PASSWORD, EDUPAGE_SCHOOL_SUBDOMAIN)
    now = datetime.now()
    next_ringing_time = edupage.get_next_ringing_time(now)
    print("Next ringing time is " + str(next_ringing_time.time))
except BadCredentialsException:
    print("Wrong username or password!")
except CaptchaException:
    print("Captcha required")
except Exception as e:
    print(f"error: {str(e)}")
finally:
    exit()