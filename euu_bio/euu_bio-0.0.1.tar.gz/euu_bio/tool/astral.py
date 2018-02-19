#! /usr/bin/env python
#################################################################################
#     File Name           :     astral.py
#     Created By          :     qing
#     Creation Date       :     [2018-02-16 10:11]
#     Last Modified       :     [2018-02-16 11:19]
#     Description         :      
#################################################################################

def get_ids(astral_fasta_file_path):
    ids = []
    with open(astral_fasta_file_path) as fin:
        for line in fin:
            if not line.startswith('>'):
                continue
            id = line.split()[0][1:]
            ids.append(id)
    return ids
