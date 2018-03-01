#from datetime import datetime
#import socket
#
#from system_cmd import CmdException
#
#from .ipfs_utils import IPFSInterface, InvalidHash
#from .ipfs_utils import MakeIPFS2
#from .packaging import find_more_information, UnexpectedFormat
from duckietown_swarm.ipfs_utils import IPFSInterface
from system_cmd.structures import CmdException

#def publisher_summary(mi, channel_name):
#    KEY_NAME = 'summary'
#    known = set()
#
#    ipfsi = IPFSInterface()
#    keys = ipfsi.get_keys()
#    path = '/ipns/' + keys[KEY_NAME]
#    print('You will see my summaries at %s' % path)
#
#    ipfsi = IPFSInterface()
#
#    previous_hash = None
#    while True:
#        timeout = 5
#
#        hashes = mi.get_at_least_one_publisher(timeout)
#        changes = 0
#        for x in hashes:
#            what, ipfs_hash = x
#            if what == 'add':
#                if not ipfs_hash in known:
#                    print('publisher: adding %s' % ipfs_hash)
#                    known.add(ipfs_hash)
#                    changes += 1
#            elif what == 'remove':
#                if ipfs_hash in known:
#                    known.remove(ipfs_hash)
#                    changes += 1
#                    print('publisher: remove %s' % ipfs_hash)
#            else:
#                assert False, x
#
#        if changes == 0:
#            continue
#        #print('get_at_least_one: %.1f s' % (time.time() - t0))
#
#        print('Creating summary for %d more, %d changes' % (len(known), changes))
#
#        summary_hash = get_summary(ipfsi, known, permanent=path, out_queues=write_to)
#        print('summary: %s' % summary_hash)
#
#        if previous_hash != summary_hash:
#            print('summary hash: %s' % summary_hash)
#
#            mi.send_to_ipns_publisher('summary', summary_hash)
#
#            previous_hash = summary_hash
#
#            msg = {'mtype': 'summary', 'details': {'ipfs': summary_hash}}

#            for q in write_to:
#                q.put((KEY_NAME, msg), block=False)


def publish_ipns(mi):
    ipfsi = IPFSInterface(mi.ipfs_path)
    keys = ipfsi.get_keys()

    while True:
        #print('summary')
        timeout = 5
        what = mi.get_many_for_me(timeout=timeout)
        if what:
            to_add = {}
            for envelope in what:
                key, v = envelope.contents
                to_add[key] = v

            for key, v in to_add.items():

                if not key in keys:
                    print('Generating new key %r' % key)
                    ipfsi.gen_key(key, 'rsa', 2048)
                    keys = ipfsi.get_keys()
                try:
                    print('publishing to key %r: %s' % (key, v))
                    ipfsi.publish(key, v)
                except CmdException as e:
                    print(e)  # XXX
                else:
                    path = '/ipns/' + keys[key]
                    print('ipns: published with key %s  %s -> /ipfs/%s ' % (key, path, v))

#def get_summary(ipfsi, known, permanent, out_queues):
#    from duckietown_swarm.pinner import advertise_invalid
#    m = MakeIPFS2()
#    s = '<html><head></head><body><pre>\n'
#
#    s += '\n Created: %s' % str(datetime.now())[:16]
#    s += '\n Host: %s' % socket.gethostname()
#    s += '\n Permanent path: <a href="%s">%s</a>' % (permanent, permanent)
#
#    s += '\n'
#    found = []
#    others = []
#    invalid = []
#    for k in known:
#        try:
#            f = find_more_information(ipfsi, k)
#            found.append(f)
#        except UnexpectedFormat:
#            others.append(k)
#        except InvalidHash:
#            invalid.append(k)
#
#    s += '<h2>Good uploads</h2>'
#    already = set()
#    redundant = []
#    found = sorted(found, key=lambda _: _.ctime)
#
#    def description(f):
#        ss = ''
#        ss += '<a href="/ipfs/%s">info</a>' % (f.ipfs_info)
#        ss += ' <a href="/ipfs/%s">raw</a>' % (f.ipfs)
#        ss += ' providers %3d %3d' % (len(f.providers_info), len(f.providers_payload))
#        ss += ' ' + str(f.ctime)[:16]
#        ss += ' %5d MB' % (f.size / (1000.0 * 1000))
#        ss += ' <a href="/ipfs/%s">%s</a>' % (f.ipfs_payload, '%20s' % f.filename)
#        ss += ' uploaded by %s : %s @ %s' % (f.upload_node, f.upload_user, f.upload_host)
#        return ss
#
#    for f in found:
#        if f.ipfs_payload in already:
#            redundant.append(f)
#            continue
#        already.add(f.ipfs_payload)
#        m.add_file(f.ipfs_payload, f.ipfs_payload, f.size)
#        m.add_file(f.ipfs_info, f.ipfs_info, 0)
#        s += '\n' + description(f)
#
#    if redundant:
#        s += '<h2>Different uploads of same payload</h2>'
#        for h in redundant:
#            s += '\n' + description(h)
#
#            advertise_invalid(out_queues, h.ipfs, comment="redundant")
#
#    if others:
#        s += '<h2>Other uploads</h2>'
#        for h in others:
#            m.add_file(h, h, 0)
#            s += '\n<a href="%s">%s</a>' % (h, h)
#
#    if invalid:
#        s += '<h2>Invalid hashes</h2>'
#        for h in invalid:
#            s += '\n' + h
#
#    s += '\n</pre></body>'
#
#    m.add_file_content('index.html', s)
#
#    return m.get_ipfs_hash()

