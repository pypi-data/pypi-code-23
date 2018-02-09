from db import create_session
from models import CC, CalendarDay, Attendance, Section, Test, SchoolCourse, Course

session = create_session()
# cc = session.query(CC).first()
# att = session.query(Attendance).first()
# calendar_day = session.query(CalendarDay).first()
# sec = session.query(Section).first()
# test = session.query(Test).first()
school_course = session.query(SchoolCourse)
# course = session.query(Course)
for sc in school_course \
        .filter(SchoolCourse.course.has(Course.name == 'Computer Programming I') & SchoolCourse.course.has(Course.credit_hours == 0.5)) \
        .filter(SchoolCourse.school_id == 704) \
        .filter(SchoolCourse.year_id == 28) \
        .all():
    print(sc.course.name)
