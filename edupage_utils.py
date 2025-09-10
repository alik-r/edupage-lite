import os

from edupage_api import Edupage, Timetable
from edupage_api.exceptions import BadCredentialsException, CaptchaException

from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

EDUPAGE_USERNAME = os.getenv("EDUPAGE_USERNAME", "")
EDUPAGE_PASSWORD = os.getenv("EDUPAGE_PASSWORD", "")
EDUPAGE_SCHOOL_SUBDOMAIN = os.getenv("EDUPAGE_SCHOOL_SUBDOMAIN", "")

edupage = Edupage()

try:
    edupage.login(EDUPAGE_USERNAME, EDUPAGE_PASSWORD, EDUPAGE_SCHOOL_SUBDOMAIN)
except BadCredentialsException:
    print("Wrong username or password!")
except CaptchaException:
    print("Captcha required")
except Exception as e:
    print(f"error: {str(e)}")

students = edupage.get_students()
if not students:
    raise Exception("Couldn't get list of students")

student = list(filter(lambda student: student.person_id == -6030, students))[0]

def get_next_ringing_time() -> str:
    now = datetime.now()
    next_ringing_time = edupage.get_next_ringing_time(now)
    return str(next_ringing_time.time)

def get_next_lesson() -> str:
    now = datetime.now()
    timetable = edupage.get_timetable(target=student, date=now)
    if not timetable:
        return ""
    
    lessons = timetable.lessons
    lessons = sorted(lessons, key=lambda l: l.start_time)

    for lesson in lessons:
        lesson_start = datetime.combine(now.date(), lesson.start_time)
        if lesson_start > now:
            room_name = lesson.classrooms[0].name if lesson.classrooms and len(lesson.classrooms) > 0 else "N/A"
            subject_name = lesson.subject.name if lesson.subject else "N/A"
            return f"Next lesson at {lesson_start:%Y.%m.%d %H:%M}\nRoom {room_name}\n{subject_name}"
    return "No more lessons today"