#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/23 9:56
# @Author  : chenjw
# @Site    : 
# @File    : html.py
# @Software: PyCharm Community Edition
# @Desc    :  do what
from base64 import b64encode


class Html:
    def __init__(self):
        self.default_css = '''
        .table1{
            line-height: 2em;
            font-family: Arial;
            border-collapse: collapse;
        }
        .thead_tr {
            color: #FF3333;
            background-color: #C0C0C0;
            border-bottom: 1px solid #fff;
        }
        .tbody_tr {
            color: #663333;
            font-size: 0.8em;
            border-bottom: 1px solid #fff;
            background-color: #DDDDDD;
        }
        .tbody_tr:hover {
            background-color: #FFFF33;
        }
        .th1 {
            font-weight: normal;
            text-align: left;
            padding: 0 10px;
            text-align: center;
        }
        '''
        self.default_title = '测试报告'
        self.body_context = ''
        pass

    def setTitle(self, title):
        self.default_title = title
        return self

    def setTable(self, header, detail):
        if isinstance(header, list) is False or isinstance(detail, list) is False:
            return self
        header_msg = ''
        for sin_header in header:
            header_msg += '''<th class="th1">%s</th>\n''' % sin_header
        header_msg = '''<thead><tr class="thead_tr th1">''' + header_msg + '''</tr></thead>'''
        detail_msg = ''
        for sin_line in detail:
            tmp_msg = ''
            for sin_cell in sin_line:
                tmp_msg += '''<td class="th1">%s</td>\n''' % sin_cell
            detail_msg += '''<tr class="tbody_tr th1">''' + tmp_msg + '''</tr>'''
        detail_msg = '''<tbody>''' + detail_msg + '''</tbody>'''
        self.body_context += '''<table class="table1">''' + header_msg + detail_msg + '''</table>'''
        return self

    def setH(self, desc, index=6):
        self.body_context += '''<h%d>%s</h%d>\n''' % (index, desc, index)
        return self

    def draw(self, x_names=range(10), l_range=[0, 10], r_range=None, x_name=None, l_name=None, r_name='', title=None,
             l_compare=[], r_compare=[], file_name=None, dpi=100, font='simsun'):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        if font is not None:
            plt.rcParams['font.sans-serif'] = [font]  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        fig = plt.figure()
        ax = fig.add_subplot(111)
        if r_range is not None or r_compare is not None:
            ax2 = ax.twinx()
        l_lns = []
        for sin_l_compare in l_compare:
            data = sin_l_compare['data']
            label = sin_l_compare['label']
            color = sin_l_compare['color']
            lns = ax.plot(x_names, data, color, label=label)
            l_lns.append(lns)

        r_lns = []
        for sin_r_compare in r_compare:
            data = sin_r_compare['data']
            label = sin_r_compare['label']
            color = sin_r_compare['color']
            lns = ax2.plot(x_names, data, color, label=label)
            r_lns.append(lns)

        def add_lns(lns, lns_list):
            for sin_lns in lns_list:
                if lns is None:
                    lns = sin_lns
                else:
                    lns += sin_lns
            return lns

        lns = None
        lns = add_lns(lns, l_lns)
        lns = add_lns(lns, r_lns)
        labs = [l.get_label() for l in lns]
        ax.legend(lns, labs, loc=0)
        ax.grid()

        if x_name is not None:
            ax.set_xlabel(x_name)

        if l_range is not None:
            ax.set_ylim(l_range[0], l_range[1])

        if l_name is not None:
            ax.set_ylabel(l_name)
        if title is not None:
            ax.set_title(title)

        if r_range is not None:
            ax2.tick_params(axis='y', colors='red')  # 刻度颜色
            ax2.spines['right'].set_color('red')  # 纵轴颜色
            ax2.set_ylim(r_range[0], r_range[1])
            if r_name is not None:
                ax2.set_ylabel(r_name)
        if file_name is not None:
            plt.savefig(file_name, dpi=dpi, bbox_inches='tight')

    def setImg(self, x_names=range(10), l_range=[0, 10], r_range=None, x_name=None, l_name=None, r_name='', title=None,
               l_compare=[], r_compare=[], dpi=100):
        file_name = 'default.png'
        self.draw(x_names, l_range, r_range, x_name, l_name, r_name, title, l_compare, r_compare, file_name, dpi)
        with open(file_name, 'rb') as imgFile:
            data = imgFile.read()
            self.body_context += '''<img src="%s"></img>''' % (
                'data:default/png;base64,' + str(b64encode(data), 'utf-8'))

    def save(self, file_name):
        with open(file_name, 'wb') as f:
            msg = '''<!DOCTYPE html>
            <html>
            <head>
            <title>%s</title>
            <style type="text/css">
            %s
            </style>
            </head>
            <body>
            %s
            </body>
            </html>
            ''' % (self.default_title, self.default_css, self.body_context)
            f.write(bytes(msg, 'utf-8'))
