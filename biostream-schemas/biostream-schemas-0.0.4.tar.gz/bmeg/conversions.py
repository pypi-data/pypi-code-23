import json
import bmeg.hugo_ensembl

def build_mapping(inpath, outpath):
    i = open(inpath, 'r')
    lines = []
    for line in i:
        lines.append(line.split('\t'))
    lines = lines[1:]
    i.close()

    mapping = {}
    for line in lines:
        mapping[line[1]] = line[36] if len(line[18]) == 0 else line[18]
    out = json.dumps(mapping)
    o = open(outpath, 'w')
    o.write(out)
    o.close()

def hugo_ensembl(hugo):
    return bmeg.hugo_ensembl.hugo_ensembl(hugo)
