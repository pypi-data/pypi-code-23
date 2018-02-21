from powerschool_alchemy.db import create_session
from powerschool_alchemy.models import CC
sess = create_session()
cc = sess.query(CC).filter(CC.id == 2514844)
cc_course = cc.first().section.course
print(cc_course.get_alt_course_number(cc_course.id, sess))