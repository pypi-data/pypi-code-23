from asammdf import MDF


f = r'e:\02__PythonWorkspace\mdf\Examples\RecordLayout\NotByteAligned\Vector_NotByteAligned - Copy.mf4'
with open(f, 'rb+') as ff:
    for addr in (0x0430, 0x04F8, 0x05C0, 0x0688):
        ff.seek(addr+90)
        ff.write(b'\x02')

x = MDF(f)

for ch in 'ABCD':
    print(x.get('Channel '+ch, samples_only=True))
