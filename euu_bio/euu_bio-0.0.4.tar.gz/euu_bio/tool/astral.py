#! /usr/bin/env python
#################################################################################
#     File Name           :     astral.py
#     Created By          :     qing
#     Creation Date       :     [2018-02-16 10:11]
#     Last Modified       :     [2018-02-19 14:01]
#     Description         :      
#################################################################################
import os

def get_ids(astral_fasta_file_path):
    ids = []
    with open(astral_fasta_file_path) as fin:
        for line in fin:
            if not line.startswith('>'):
                continue
            id = line.split()[0][1:]
            ids.append(id)
    return ids

def split_fasta_file(astral_fasta_file_path, ids, output_path):
    def __save_file(cur_id, cur_file, ids, output_path):
        if cur_file and cur_id in ids:
            with open(os.path.join(output_path, cur_id + '.fasta'), 'w') as fout:
                fout.write('\n'.join(cur_file))
        cur_file.clear()

    ids = set(ids)
    cur_file = []
    cur_id = None
    with open(astral_fasta_file_path) as fin:
        for line in fin:
            if line.startswith('>'):
                __save_file(cur_id, cur_file, ids, output_path)
                cur_id = line.split()[0][1:]
            cur_file.append(line.strip())
    __save_file(cur_id, cur_file, ids, output_path)
