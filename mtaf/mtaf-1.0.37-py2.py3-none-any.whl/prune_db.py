from pymongo import MongoClient
import argparse
from os import getenv
import datetime
import re

# log =mtaf_logging.get_logger('mtaf.run_features')


def prune_db(db_name, server, operation, number_to_keep, max_age):
    re_cfg = re.compile(', installed[^,]*, installed[^,]*')
    if operation=='list':
        print 'pruning %s on server %s to latest %d test runs within last %d days' % (
            db_name, server, number_to_keep, max_age)
    client = MongoClient(server)
    db = client[db_name]
    starts = db['test_starts'].find({}, {'date': 1, 'time': 1, 'configuration': 1})
    starts_by_cfg={}
    now = datetime.datetime.now()
    for start in starts:
        timestamp = '%s-%s' % (start['date'], start['time'])
        dt = datetime.datetime.strptime(timestamp, "%m/%d/%y-%H:%M:%S")
        age = now - dt
        days = age.total_seconds() / datetime.timedelta(1).total_seconds()
        _id = start['_id']
        cfg = repr(start['configuration'])
        d = {'_id': _id, 'timestamp': timestamp, 'cfg': cfg, 'days': days}
        if cfg in starts_by_cfg:
            starts_by_cfg[cfg].append(d)
        else:
            starts_by_cfg[cfg] = [d]
    keep_start_ids = []
    remove_start_ids = []
    keep_feature_ids = []
    remove_feature_ids = []
    keep_screenshot_ids = []
    remove_screenshot_ids = []
    for cfg in starts_by_cfg:
        removed = 0
        remaining = 0
        for i, d in enumerate(sorted(starts_by_cfg[cfg], key=lambda x: x['days'], reverse=False)):
            too_many = i >= number_to_keep
            too_old = d['days'] > max_age
            removable = too_many or too_old
            why_msgs = []
            if too_many:
                why_msgs.append("count > %d" % number_to_keep)
            if too_old:
                why_msgs.append("age > %d days" % max_age)
            if removable:
                print 'cfg = "%s": _id = %s: removing test data [%s]' % (cfg, d['_id'], ', '.join(why_msgs))
                remove_start_ids.append(d['_id'])
            else:
                keep_start_ids.append(d['_id'])
            features = []
            for doc in db['features'].find({'start_id': d['_id']}):
                features.append(doc)
            for feature in features:
                if removable:
                    remove_feature_ids.append(feature['_id'])
                else:
                    keep_feature_ids.append(feature['_id'])
                for scenario in feature['scenarios']:
                    for step in scenario['steps']:
                        if not removable and 'screenshot_id' in step:
                            keep_screenshot_ids.append(step['screenshot_id'])
    for doc in db['screenshots'].find():
        if doc['_id'] not in keep_screenshot_ids:
            remove_screenshot_ids.append(doc['_id'])
    if operation == 'list':
        print "keep_start_ids: %s" % keep_start_ids
        print "remove_start_ids: %s" % remove_start_ids
        print "keep_feature_ids: %s" % keep_feature_ids
        print "remove_feature_ids: %s" % remove_feature_ids
        print "keep_screenshot_ids: %s" % keep_screenshot_ids
        print "remove_screenshot_ids: %s" % remove_screenshot_ids
    elif operation == 'prune':
        for _id in remove_start_ids:
            db['test_starts'].delete_one({'_id': _id})
        for _id in remove_feature_ids:
            db['features'].delete_one({'_id': _id})
        for _id in remove_screenshot_ids:
            db['screenshots'].delete_one({'_id': _id})

if __name__ == '__main__':

    try:
        # get db hostfrom environment
        mtaf_db_host = getenv('MTAF_DB_HOST')
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description='  runs behave test on specified features directory and saves' +
                                                     '  the results on a mongodb running on a specified server\n')
        parser.add_argument("-d", "--db_name", type=str, default='e7_results', help="name of db")
        parser.add_argument("-s", "--server", type=str, default=mtaf_db_host,
                            help="(optional) specify mongodb server, default vqda1")
        parser.add_argument("-n", "--number_to_keep", type=int, default=10,
                            help="number of test runs to keep for each configuration")
        parser.add_argument("-a", "--age", type=int, default=30,
                            help="max age in days to keep in database")
        parser.add_argument("-o", "--operation", type=str, choices=['list', 'prune'], default='list',
                            help="operation to perform")
        args = parser.parse_args()
        prune_db(args.db_name, args.server, args.operation, args.number_to_keep, args.age)
    except:
        pass
