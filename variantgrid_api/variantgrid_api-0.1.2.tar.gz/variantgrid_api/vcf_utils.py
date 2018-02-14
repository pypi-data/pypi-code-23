'''
Created on 13Feb.,2018

@author: dlawrence
'''


def get_vcf_header_lines(top_lines=[], info_dict={}, formats=[], contigs=[], samples=[]):
    ''' info_dict - values of ('number', 'type', 'description')
        contigs - tuples of (contig, length, assembly)
    '''

    header_lines = ['##fileformat=VCFv4.1']
    header_lines.extend(top_lines)
    for (info_id, data) in info_dict.items():
        data['id'] = info_id
        line_template = '##INFO=<ID=%(id)s,Number=%(number)s,Type=%(type)s,Description="%(description)s">'
        line = line_template % data
        header_lines.append(line)

    use_format = samples and formats 
    if use_format:
        header_lines.extend(formats)

    for (contig, length, assembly) in contigs:
        line = '##contig=<ID=%s,length=%d,assembly=%s>' % (contig, length, assembly)
        header_lines.append(line)


    colnames = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO']
    if use_format:
        colnames += ['FORMAT'] + samples

    header_lines.append('#' + '\t'.join(colnames))

    return header_lines


def get_info(info_dict):
    if info_dict:
        infos_list = []
        for info_name, info_data in info_dict.items():
            infos_list.append('%s=%s' % (info_name, info_data))
        info = ';'.join(infos_list)
    else:
        info = '.'

    return info