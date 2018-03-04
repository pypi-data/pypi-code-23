# from pathlib import Path

# a = Path('').is_file()
# b = open(a)
# print(a)


# from tkinter import *
#
# def callback():
#     print(var.get())
#
# def callback_st():
#     for m in range(4):
#         Radiobutton(frame, text=m, value=m, variable=var, command=callback).pack(anchor=W)

# import os
#
# print(os.system('pandoc test.txt -o test.docx'))

# import subprocess
# process = subprocess.Popen(['pandoc', 'test.txt', '-o', 'test.pdf'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# error = process.communicate()[1]
# # print(output)
# print(process.returncode)
# print(error.decode('utf-8'))


import pyshark
cap = pyshark.FileCapture('in0.pcap')
print(cap[1])


# root = Tk()
# var = IntVar()
# frame = Frame(root, bd=4)
# frame.pack()
# callback_st()
# # sv.trace_add('write', lambda name, index, mode, sv=sv: callback(sv))
# # e = Entry(root, textvariable=sv)
# # e.pack()
# root.mainloop()



# import re, os
# a = re.escape('in0.pcap')
# print(a)
# os.rename(a, '\/Users\/jarryshaw\/Documents\/GitHub\/PyProject\/Analyser\/project\/deprecated\/in1.pcap')


# FILE = re.compile(r'''
#     \A(?P<name>.*?)(?P<copy>\ copy)?(?P<fctr>\ [0-9]+)?[.](?P<exts>.*)\Z
# ''', re.VERBOSE)

# ifnm = '/Users/jarryshaw/Documents/GitHub/PyProject/Analyser/project/deprecated/in0.pcap'
# fnmt = FILE.match(ifnm)
# if fnmt is None:
#     print('NoneType')

# name = fnmt.group('name') or ''
# copy = fnmt.group('copy') or ''
# fctr = fnmt.group('fctr')
# exts = fnmt.group('exts') or ''
# print(fctr)

# if fctr:
#     sctr = int(fctr) + 1
#     fctr = ' ' + str(sctr)
# else:
#     print(copy)
#     if copy:
#         sctr = 2
#         fctr = ' ' + str(sctr)
#     else:
#         sctr = 1
#         fctr = ''

# cpnm = name + copy + fctr + '.' + exts
# print(cpnm)
