from db import create_session
from models import *
session = create_session()
cc = session.query(CC.CC).first()
att = session.query(Attendance.Attendance).first()
sec = session.query(Section.Section).first()
test = session.query(Test.Test).first()
print(test.test_scores)