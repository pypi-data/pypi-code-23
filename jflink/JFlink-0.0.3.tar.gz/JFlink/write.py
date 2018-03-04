# 利用neutron和allStructure生成fispact输入文件
# 输入：文件地址，neutron，allStructure
# 输出：无

import os
import re

from .model import Data, ele, Avogadro, defaultInput, defaultArrayx, defaultCollapx, defaultPrintlib


def _mkdir(path):
    # 仅内部调用
    # 在完整路径处新建文件夹
    # path--input--建立文件夹位置
    # *--output--bool,是否成功建立文件夹
    assert type(path) == str
    path = path.strip()
    path = path.rstrip("\\")
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    else:
        return False

def _collapx(text, cell, path, func=None, call=False, clear=False):
    # 仅内部调用
    # 生成FISPACT输入文件collapx.i
    # text--input--初始化文件内容
    # cell--input--材料名称
    # path--input--FISPACT输入文件顶层路径
    assert type(text) == str
    assert type(cell) == str
    assert type(path) == str
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)

    _mkdir(path + '/' + cell)
    mode = re.compile('{[ \t\n]*title[ \t\n]*}')
    text = mode.sub('Irradiation of ' + cell, text)
    with open(path + '/' + cell + '/collapx.i', 'w') as f:
        f.write(text)

def _arrayx(text, cell, path, func=None, call=False, clear=False):
    # 仅内部调用
    # 生成FISPACT输入文件arrayx.i
    # text--input--初始化文件内容
    # cell--input--材料名称
    # path--input--FISPACT输入文件顶层路径
    assert type(text) == str
    assert type(cell) == str
    assert type(path) == str
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)

    _mkdir(path + '/' + cell)
    mode = re.compile('{[ \t\n]*title[ \t\n]*}')
    text = mode.sub('Irradiation of ' + cell, text)
    with open(path + '/' + cell + '/arrayx.i', 'w') as f:
        f.write(text)

def _printlib(text, cell, path, func=None, call=False, clear=False):
    # 仅内部调用
    # 生成FISPACT输入文件printlib.i
    # text--input--初始化文件内容
    # cell--input--材料名称
    # path--input--FISPACT输入文件顶层路径
    assert type(text) == str
    assert type(cell) == str
    assert type(path) == str
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)

    _mkdir(path + '/' + cell)
    mode = re.compile('{[ \t\n]*title[ \t\n]*}')
    text = mode.sub('Irradiation of ' + cell, text)
    with open(path + '/' + cell + '/printlib.i', 'w') as f:
        f.write(text)

def _input(text, neutron, allStructure, cell, genRate, path, func=None, call=False, clear=False):
    # 仅内部调用
    # 生成FISPACT输入文件input.i
    # text--input--初始化文件内容
    # neutron--input--由JMCT输出文件读取的所有材料物质信息
    # allStructure--input--由GDML文件读取的所有材料物质信息
    # cell--input--材料名称
    # genRate--input--光子产生速度
    # path--input--FISPACT输入文件顶层路径
    assert type(text) == str
    assert type(neutron) == Data
    assert type(allStructure) == dict
    assert type(cell) == str
    assert type(path) == str
    assert type(genRate) == float or type(genRate) == int
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)
    _mkdir(path + '/' + cell)
    eleDensity = {}
    allDensity = 0.
    for element in allStructure[cell].matGre:
        tmp = element[1] * element[3] / Avogadro
        allDensity += tmp
        eleDensity[element[0]] = tmp
    # 计算DENSITY
    # 单位g/cm^3
    density = '%E' % allDensity
    # 写入MASS
    tmp = float(allStructure[cell].matD) * float(neutron.cellInfo[cell][1])
    # 字符串mass
    mass = '%E' % tmp
    elements = [' %s %f\n' % (ele[element[2]], 100 * eleDensity[element[0]] / allDensity)for element in allStructure[cell].matGre]
    tmp = ['%d\n' % len(allStructure[cell].matGre)]
    tmp.extend(elements)
    elements = tmp
    # 字符串elements
    elements = ''.join(elements)[:-1]
    # 计算中子通量
    flux = '%E' % (neutron.cellInfo[cell][0] * genRate)

    # 替换
    mode = re.compile('{[ \t\n]*title[ \t\n]*}')
    text = mode.sub('Irradiation of ' + cell, text)
    mode = re.compile('{[ \t\n]*mass[ \t\n]*}')
    text = mode.sub(mass, text)
    mode = re.compile('{[ \t\n]*density[ \t\n]*}')
    text = mode.sub(density, text)
    mode = re.compile('{[ \t\n]*flux[ \t\n]*}')
    text = mode.sub(flux, text)
    mode = re.compile('{[ \t\n]*elements[ \t\n]*}')
    text = mode.sub(elements, text)

    with open(path + '/' + cell + '/input.i', 'w') as f:
        f.write(text)

def _genSource(cell, i, neutron, allDistributions, pre, split, func=None, call=False, clear=False):
    # 仅内部调用
    # 用于map操作
    if func:
        assert type(call) == bool
        assert type(clear) == bool
        if call:
            func(clear)

    tmp = []
    segments = []
    samProb = []
    distributions = allDistributions[cell][1]
    possibility = allDistributions[cell][0] * neutron.cellInfo[cell][1]
    for distribution in distributions:
        segments.append('%.2f, %.2f, ' % (distribution.leftBound, distribution.rightBound))
        samProb.append('%e, ' % distribution.perc)
    segments = ''.join(segments)
    samProb = ''.join(samProb)
    segments = segments[:-2]
    samProb = samProb[:-2]
    tmp.append('%sSource_%d {\n' % (pre, i))
    tmp.append('%s%sprobability                        = %e\n' % (pre, split, possibility))
    tmp.append('%s%scell_name                          = \"%s\"\n' % (pre, split, cell))
    tmp.append('%s%sprobability_of_energy_distribution = 1\n' % (pre, split))
    tmp.append('%s%senergy_distribution                = \"dist_%d\" \n' % (pre, split,  i))
    tmp.append('%s%sdist_%d {\n' % (pre, split, i))
    tmp.append('%s%sdistribution_type  = \"piecewise_uniform_spectrum\"\n' % (pre, split * 2))
    tmp.append('%s%ssegments           = %s\n' % (pre, split * 2, segments))
    tmp.append('%s%ssample_probability = %s\n' % (pre, split * 2, samProb))
    tmp.append('%s%s}\n%s}\n' % (pre, split, pre))
    return ''.join(tmp)

def writef(path, genRate, neutron, allStructure, _inputText = defaultInput, _collapxText = defaultCollapx, _arrayxText = defaultArrayx, _printlibText = defaultPrintlib, funcTime=None, funcOne=None, interval=100):
    # 生成FISPACT输入文件
    # ?text--input--初始化文件内容
    # neutron--input--由JMCT输出文件读取的所有材料物质信息
    # allStructure--input--由GDML文件读取的所有材料物质信息
    # genRate--input--光子产生速度
    # path--input--FISPACT输入文件顶层路径
    keys = neutron.cellInfo.keys()
    length = len(keys)
    inputTextList = [_inputText] * length
    collapxTextList = [_collapxText] * length
    arrayxTextList = [_arrayxText] * length
    neutronList = [neutron] * length
    allStructureList = [allStructure] * length
    genRateList = [genRate] * length
    pathList = [path] * length
    if funcTime:
        callTime = max(length // interval, 1)
        # 回调告知总调用次数
        funcOne(length // callTime, length)
        funList = [funcTime] * length
        callList = [True if i % callTime == 0 or i == 0 else False for i in range(length)]
        clearList = [False] * length
        clearList[0] = True
        # 每次回调告知进度
        list(map(_input, inputTextList, neutronList, allStructureList, keys, genRateList, pathList, funList, callList, clearList))
        list(map(_collapx, collapxTextList, keys, pathList, funList, callList, clearList))
        list(map(_arrayx, arrayxTextList, keys, pathList, funList, callList, clearList))
        if _printlibText:
            printlibList = [_printlibText] * length
            list(map(_printlib, printlibList, keys, pathList))
    else:
        list(map(_input, inputTextList, neutronList, allStructureList, keys, genRateList, pathList))
        list(map(_collapx, collapxTextList, keys, pathList))
        list(map(_arrayx, arrayxTextList, keys, pathList))
        if _printlibText:
            printlibList = [_printlibText] * length
            list(map(_printlib, printlibList, keys, pathList))

def writej(path, text, neutron, allDistributions, split, funcTime=None, funcOne=None, interval=100):
    # 生成JMCT输入文件
    # path--input--JMCT输入文件位置
    # neutron--input--由JMCT输出文件读取的所有材料物质信息
    # allStructure--input--由GDML文件读取的所有材料物质信息
    # split--input--括号缩进
    mode = re.compile('{[ \t\n]*source[ \t\n]*}')

    try:
        pos = mode.search(text).start()
    except Exception as e:
        raise e
    offset = pos - text.rfind('\n', 0, pos) - 1
    pre = offset * ' '
    numOfStus = len(neutron.cellInfo.keys())
    tmp = ['number_of_source = %d\n' % numOfStus]
    tmp.append('%sparticle_type    = 2\n' % pre)
    length = len(neutron.cellInfo)
    numList = [i for i in range(length)]
    neutronList = [neutron] * length
    allDisList = [allDistributions] * length
    preList = [pre] * length
    splitList = [split] * length
    if funcTime:
        callTime = max(length // interval, 1)
        # 回调告知总调用次数
        funcOne(length // callTime, neutron.cellNum)
        funList = [funcTime] * length
        callList = [True if i % callTime == 0 or i == 0 else False for i in range(length)]
        clearList = [False] * neutron.cellNum
        clearList[0] = True
        # 每次回调告知进度
        tmp.extend(list(map(_genSource, neutron.cellInfo.keys(), numList, neutronList, allDisList, preList, splitList, funList, callList, clearList)))
    else:
        tmp.extend(list(map(_genSource, neutron.cellInfo.keys(), numList, neutronList, allDisList, preList, splitList)))

    tmp = ''.join(tmp)
    text = mode.sub(tmp, text)

    with open(path, 'w') as f:
        f.write(text)
