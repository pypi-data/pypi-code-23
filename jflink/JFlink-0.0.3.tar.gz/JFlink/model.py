# 定义所使用的数据结构

# 数据类，来自input文件
class Data(object):
    name = ''

    def __init__(self, name=''):
        self._notNull = False if name == '' else True
        self.name = name
        self.eleNum = 0
        self.eleName = []
        self.eleEner = []
        self.cellNum = 0
        self.cellInfo = {}
        self.eneNum = 0
        self.eneBin = []

    def __str__(self):
        m = str(self.eleNum) + ' elements\n' + str(self.cellNum) + ' cells\n' + str(self.eneNum) + ' energy bins'
        return m

    def __bool__(self):
        return self._notNull


# 栅元类，来自gmdl文件
class Volume(object):
    name = ''
    property = ''
    # 物质信息，名称/密度/体积/质量
    matName = ''
    matD = ''
    matV = ''
    matM = ''
    # 物质信息，成分[(元素名称，原子序数，原子质量，比例)，...]
    matGre = []

    def __init__(self, name):
        self.name = name
        self.matName = ''
        self.matD = ''
        self.matGre = []


# 光子分布类
class energyDis:
    def __init__(self):
        self.leftBound = 0.
        self.rightBound = 0.
        self.perc = 0.


# 阿伏伽德罗常数
Avogadro = 0.602

# 元素原子量对应表
ele = ['', 'H', 'HE', 'LI', 'BE', 'B', 'C', 'N', 'O', 'F', 'NE', 'NA', 'MG', 'AL', 'SI', 'P', 'S', 'CL', 'AR', 'K',
       'CA', 'SC', 'TI', 'V', 'CR', 'MN', 'FE', 'CO', 'NI', 'CU', 'ZN', 'GA', 'GE', 'AS', 'SE', 'BR', 'KR', 'RB', 'SR',
       'Y', 'ZR', 'NB', 'MO', 'TC', 'RU', 'RH', 'PD', 'AG', 'CD', 'IN', 'SN', 'SB', 'TE', 'I', 'XE', 'CS', 'BA', 'LA',
       'CE', 'PR', 'ND', 'PM', 'SM', 'EU', 'GD', 'TB', 'DY', 'HO', 'ER', 'TM', 'YB', 'LU', 'HF', 'TA', 'W', 'RE', 'OS',
       'IR', 'PT', 'AU', 'HG', 'TL', 'PB', 'BI', 'PO', 'AT', 'RN', 'FR', 'RA', 'AC', 'TH', 'PA', 'U', 'NP', 'PU', 'AM',
       'CM', 'BK', 'CF', 'ES', 'FM']
defaultInput = 'NOHEAD\nMONITOR 1\nAINP\nFISPACT\n* {title}\nDENSITY {density}\nMASS {mass} {elements}\nMIND ' \
               '1.0\nHALF\nGRAPH 2 0 0 1 2\n{flux}\nATOMS\nLEVEL 100 1\nTIME 1.0\nHALF\nDOSE 1\nATOMS\nNOSTABLE\nLEVEL ' \
               '20 1\nFLUX 0.\nZERO\nTIME 1.0 HOURS ATOMS\nEND\n* END\n/*\n '
defaultCollapx = 'MONITOR 1\nCOLLAPSE 175\nFISPACT\n* {title}\nEND\n* END ' \
                 'OF RUN\n/*\n '
defaultArrayx = 'MONITOR 1\nSPEK\nENFA\n* {title}\nTAPA\nFISPACT\n* WRITE DATA TO ARRAY FILE.\nEND\n* END OF ' \
                'RUN\n/*\n '
defaultPrintlib = ''

defaultFILES = '03  <case>\spectra\n05  input\n06  output\n07  <eaf>\eaf_un_20070\n08  <eaf>\eaf_<0>_asscfy_20070\n' \
               '09  <eaf>\eaf_<0>_fis_20070\n10  graph\n11  <eaf>\eaf_a2_20070\n12  collapx\n13  arrayx\n' \
               '14  <eaf>\eaf_haz_20070\n15  summaryx\n16  <eaf>\eaf_dec_20070.001\n17  collapx\n' \
               '18  <eaf>\eaf_index_20070\n19  <eaf>\eaf_<0>_gxs_<1>_<2>_20070\n20  fluxes\n' \
               '21  <eaf>\eaf_stop_pro_20070\n22  <eaf>\eaf_stop_deu_20070\n23  <eaf>\eaf_stop_alp_20070\n' \
               '24  <eaf>\eaf_stop_tri_20070\n25  <eaf>\eaf_stop_he3_20070\n26  <eaf>\eaf_xn_pn_20070\n' \
               '27  <eaf>\eaf_xn_dn_20070\n28  <eaf>\eaf_xn_an_20070\n29  <eaf>\eaf_xn_tn_20070\n' \
               '30  <eaf>\eaf_xn_hn_20070\n31  <eaf>\eaf_xn_d2n_20070\n32  <eaf>\eaf_xn_t2n_20070\n' \
               '33  <eaf>\eaf_spec_pt1_20070\n34  <eaf>\eaf_spec_pt2_20070\n35  <eaf>\eaf_spec_pt3_20070\n' \
               '36  <eaf>\eaf_spec_pt4_20070\n37  <eaf>\eaf_spec_pt5_20070\n38  halfunc\n39  <eaf>\eaf_abs_20070\n' \
               '40  <eaf>\eaf_clear_20070\n41  <eaf>\eaf_xn_p2n_20070\n42  <eaf>\eaf_xn_a2n_20070\n' \
               '43  <eaf>\eaf_xn_h2n_20070'
