from lib.fake_detector import FakeDetector
from glob import glob
from lib.user_exception import UserException as Ux

fake_detector = FakeDetector('ePhone7/features/steps', fake_tag=False)
fake_count = 0
real_count = 0
for fname in glob('ePhone7/features/*.feature'):
    print fname
    with open(fname) as f:
        lines = [line.strip() for line in f.readlines()]
        for line in lines:
            if not (line.startswith('Feature') or line.startswith('Scenario') or line == '' or line[0] == '@'):
                try:
                    if fake_detector.match(line[6:]):
                        fake_count += 1
                    else:
                        real_count += 1
                    # print "%80s: %s" % (line[6:], fake_detector.match(line[6:]))
                except Ux:
                    pass
print "fake_count: %d" % fake_count
print "real_count: %d" % real_count

# steps = [
#         'A fake step',
#         'A real step',
#         'Another real step',
#         'A step with a fake substep',
#         'A step with a real substep',
#         'A step with a parameter of some kind in the name',
#         'A step with a "parameter of some kind" in the name',
#         'Another step with a fake substep'
#         ]
# for step in steps:
#     print step, fake_detector.match(step)
