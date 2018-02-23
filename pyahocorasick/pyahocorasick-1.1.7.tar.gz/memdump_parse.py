memory = {}

for line in open('aaa'):
    tmp = line.split()
    if tmp != 'XXX':
        continue

    if tmp[1] == 'allocted':
        addr = tmp[2]
        size = int(tmp[3])
        assert addr not in memory
        memory[addr] = size

    elif tmp[1] == 'freeing':
        addr = tmp[2]
        assert addr in memory
        del memory[addr]
    else:
        assert False

print memory
