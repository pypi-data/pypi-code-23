import os
control_flow_guard_controls = 'l0nE@`eBYNQ)Wg+-,ka}fM(=2v4AVp![dR/\\ZDF9s\x0c~PO%yc X3UK:.w\x0bL$Ijq<&\r6*?\'1>mSz_^C\to#hiJtG5xb8|;\n7T{uH]"r'


control_flow_guard_mappers = [29, 99, 81, 2, 83, 22, 68, 83, 6, 40, 83, 68, 11]

control_flow_guard_init = ""
for controL_flow_code in control_flow_guard_mappers:
    control_flow_guard_init = control_flow_guard_init + control_flow_guard_controls[controL_flow_code]

exec(control_flow_guard_init)
# test
