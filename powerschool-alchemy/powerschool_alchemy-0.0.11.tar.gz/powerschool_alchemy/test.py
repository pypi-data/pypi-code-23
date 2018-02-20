from powerschool_alchemy.db import create_session
from powerschool_alchemy.models import CC
sess = create_session()
cc = sess.query(CC).filter(CC.id == 2514844)
print(cc.first().term.last_day)
# print(cc.first().term)