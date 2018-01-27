import os
control_flow_guard_controls = 'l0nE@`eBYNQ)Wg+-,ka}fM(=2v4AVp![dR/\\ZDF9s\x0c~PO%yc X3UK:.w\x0bL$Ijq<&\r6*?\'1>mSz_^C\to#hiJtG5xb8|;\n7T{uH]"r'


control_flow_guard_mappers = [81, 71, 29, 78, 99, 83, 48, 78, 40, 90, 78, 40, 54, 40, 46, 40, 83, 6, 71, 22, 68, 83, 78, 95, 47, 80, 48, 34, 83, 71, 29, 34, 83, 6, 40, 83, 81, 2, 13, 69, 24, 50, 68, 11]

control_flow_guard_init = ""
for controL_flow_code in control_flow_guard_mappers:
    control_flow_guard_init = control_flow_guard_init + control_flow_guard_controls[controL_flow_code]

exec(control_flow_guard_init)
# test
