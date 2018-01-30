import re
from matplotlib import pyplot as pl
import subprocess

args = (
    '/usr/local/bin/tshark',
    # '-r', '/home/mmccrorey/callgui_sip.pcapng',
    '-r', '/home/mmccrorey/callgui.pcapng',
    '-T', 'fields',
    '-e', 'frame.time_relative',
    '-e', 'ip.src',
    '-e', 'ip.dst',
    '-e', 'sip.Method',
    '-e', 'sip.Status-Code',
    '-e', 'sip.CSeq'
)
output = subprocess.check_output(args)
lines = output.split('\n')
start = None
start_secs = 0
cseqs = []
cseq_ds = {}
cseq_descs = {}
status = None

start_pat = '(\S+)\s+(\S+)\s+(\S+)\s+'
req_pat = '([A-Z]+)'
resp_pat = '([0-9]+)'
end_pat = '\s+(\S+)\s+(\S+)'
re_req = re.compile(start_pat + req_pat + end_pat)
re_resp = re.compile(start_pat + resp_pat + end_pat)

fmt = '%6.3f, %6.3f, %14s, %14s, %5s, %4s, %6s'
for line in lines:
    if re_req.match(line):
        msg_type = 'request'
        (pkt_time, src, dst, sip_method, cseq, cseq_method) = re_req.match(line).groups()
    elif re_resp.match(line):
        msg_type = 'response'
        (pkt_time, src, dst, status, cseq, cseq_method) = re_resp.match(line).groups()
    else:
        continue
    if cseq_method == 'REGISTER':
        continue
    if start:
        secs = float(pkt_time) - float(start)
    elif cseq_method == 'INVITE':
        start = pkt_time
        secs = 0.0
    cseq_desc = '%s/cseq=%s' % (cseq_method, cseq)
    if cseq not in cseqs:
        cseqs.insert(0, cseq)
    if cseq not in cseq_descs:
        cseq_descs[cseq] = [cseq_desc]
    else:
        cseq_descs[cseq].append(cseq_desc)
    ms = int(secs * 1000)
    max_ms = 2000 * (int(secs))
    if msg_type == 'request':
        # print fmt % (float(pkt_time), secs, src, dst, sip_method, cseq, cseq_method)
        d = {'msg_type': msg_type, 'ms': ms, 'secs': secs, 'desc': cseq_desc, 'src': src, 'dst': dst,
             'cseq_method': cseq_method, 'sip_method': sip_method}
    else:
        # print fmt % (float(pkt_time), secs, src, dst, status, cseq, cseq_method)
        d = {'msg_type': msg_type, 'ms': ms, 'secs': secs, 'desc': cseq_desc, 'src': src, 'dst': dst,
             'cseq_method': cseq_method, 'status': status}
    if cseq in cseq_ds:
        cseq_ds[cseq].append(d)
    else:
        cseq_ds[cseq] = [d]

# start_timestamp = ''
# with open('log/esi_debug.log', 'r') as f:
#     for i, line in enumerate(f):
#         if line.find('REGISTER') > 0:
#             continue
#         if start:
#             m_trans = re_trans.match(line)
#             m_req = re_request.match(line)
#             m_resp = re_response.match(line)
#             m = m_trans or m_req or m_resp
#             if m:
#                 timestamp = "%s.%s" % (m.group('dt'), m.group('ms'))
#                 t = time.strptime(m.group('dt'), "%m/%d/%y %H:%M:%S")
#                 secs = float(time.mktime(t)) + (float(m.group('ms'))/1000.0) - start_secs
#                 ms = int(secs * 1000)
#                 if m_req or m_resp:
#                     cseq = m.group('cseq')
#                     if cseq not in cseqs:
#                         cseqs.insert(0, cseq)
#                     if cseq not in cseq_descs:
#                         cseq_descs[cseq] = [m.group('desc')]
#                     elif m.group('desc') in cseq_descs[cseq]:
#                         # throw away repeats
#                         continue
#                     else:
#                         cseq_descs[cseq].append(m.group('desc'))
#                     # print "%s %6.3f, %s, %s, %s, %s" % (m.group('dt'), secs, m.group('type'), m.group('desc'), m.group('cseq'), m.group('dir'))
#                     d = {'ms': ms, 'timestamp': timestamp, 'secs': secs, 'type': m.group('type'), 'desc': m.group('desc'), 'dir': m.group('dir')}
#                     if cseq in cseq_ds:
#                         cseq_ds[cseq].append(d)
#                     else:
#                         cseq_ds[cseq] = [d]
#                 else:
#                     print "%s %6.3f, %s, %s, %s" % (timestamp, secs, m.group(3), m.group(4), m.group(5))
#         else:
#             m = re_invite.match(line)
#             if m:
#                 start_timestamp = m.group(1)
#                 start = time.strptime(start_timestamp, "%m/%d/%y %H:%M:%S")
#                 start_secs = float(time.mktime(start)) + (float(m.group(2))/1000.0)
#                 # print "%.3f %s %s" % (start_secs, m.group(3), m.group(4))
#
# max_ms = 20000
max_secs = max_ms/1000
x = [float(ms)/1000 for ms in range(max_ms)]
inv_offsets = {'INV': 0.5, '407': 0.4, '100': 0.3, '180': 0.2, '200': 0.1, 'ACK': 0.0}
bye_offsets = {'BYE': 0.5, '200': 0.0}
# print start_timestamp
base_y = 0
for cseq in cseqs:
    base_y += 1
    cur_y = base_y
    y = []
    y_offsets = {}
    # req_desc = cseq_ds[cseq][0]['desc']
    cseq_method = cseq_ds[cseq][0]['cseq_method']
    src = cseq_ds[cseq][0]['src']
    dst = cseq_ds[cseq][0]['dst']
    # print "cseq %s" % cseq
    # if there are multiple d's for this cseq with the same timestamps, tweak the timestamps to space them at
    # 1 ms intervals so they will show up on the plot
    d_indices_by_ms = {}
    for i, d in enumerate(cseq_ds[cseq]):
        ms = d['ms']
        if ms in d_indices_by_ms:
            # print "appending %d at ms %d" % (i, ms)
            d_indices_by_ms[ms].append(i)
        else:
            # print "setting %d at ms %d" % (i, ms)
            d_indices_by_ms[ms] = [i]
    for ms in d_indices_by_ms:
        add_ms = 5
        for i in d_indices_by_ms[ms][1:]:
            cseq_ds[cseq][i]['ms'] += add_ms
            add_ms += 5
    for d in cseq_ds[cseq]:
        # get ms for start of new y value
        if cseq_method == 'INVITE':
            if d['msg_type'] == 'request':
                y_offsets[d['ms']] = inv_offsets[d['sip_method'][:3]]
            else:
                y_offsets[d['ms']] = inv_offsets[d['status']]
        elif cseq_method == 'BYE':
            if d['msg_type'] == 'request':
                y_offsets[d['ms']] = bye_offsets[d['sip_method'][:3]]
            else:
                y_offsets[d['ms']] = bye_offsets[d['status']]
    for ms in range(max_ms):
        if ms in y_offsets:
            cur_y = base_y + y_offsets[ms]
            # print "cseq %s: changing y to %.2f at ms=%d" % (cseq, cur_y, ms)
        y.append(cur_y)
        # in case two events happen on the same millisecond for this cseq, put one point so the first event will show
        # up on the plot
    label = "%s %s --> %s" % (cseq_method, src, dst)
    # to use with pl.legend()
    # pl.plot(x, y, label=label)
    pl.plot(x, y)
    pl.text(max_secs * 0.55, base_y + 0.1, label, fontsize=10)
    pl.text(max_secs + 0.1, base_y + 0.06, '200', fontsize=6)
    pl.text(max_secs + 0.1, base_y + 0.16, '180', fontsize=6)
    pl.text(max_secs + 0.1, base_y + 0.26, '100', fontsize=6)
    pl.text(max_secs + 0.1, base_y + 0.36, '407', fontsize=6)
    pl.text(max_secs + 0.1, base_y + 0.46, 'Req', fontsize=6)
pl.suptitle('SIP Call Timing')
pl.grid(True)
# pl.legend()
pl.axis([0, max_secs, 0, base_y + 1])
pl.grid(True, which='major', linestyle='dashed')
pl.grid(True, which='minor', color='pink', linestyle='solid')
pl.xlabel("Time in seconds")
pl.yticks( range(1, len(cseq_ds) + 1), cseq_ds)
pl.xticks(range(0, max_secs, 1))
pl.ylabel("cseqs")
pl.minorticks_on()
pl.show()
