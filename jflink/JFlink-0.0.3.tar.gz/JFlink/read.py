# 从fispact输出文件中读取光谱信息
# 输入：文件地址
# 输出：list[model.energyDis *24]

import re
import os
from lxml import etree
from .model import energyDis, Data, Volume


def _extractDis(allItem, maxFlag, modeF, modeS, modeT, modeL, func=None, call=False, clear=False):
    # 仅内部调用
    # 用于map操作
    # 从FISPACT输出文件特定的文本中解析出光谱
    # allItem--input--某FISPACT文件内容
    # maxFlag--input--光子分布无穷大等效值
    # distributes--output--提取出的一种材料的光谱类
    assert type(allItem) == str
    assert type(maxFlag) == float
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)

    distributes = []
    targetPart = modeF.findall(allItem)[-1]

    items = modeS.findall(targetPart)
    items = [items[i] for i in range(len(items)) if i % 2 == 1]

    bound = modeT.findall(targetPart)

    for i, item in enumerate(items):
        distribute = energyDis()
        result = modeL.findall(bound[i])
        distribute.leftBound = float(result[0])
        distribute.rightBound = float(result[1]) if len(result) == 2 else maxFlag
        distribute.perc = float(item)
        distributes.append(distribute)
    return distributes

def _extractGamma(allItem, modeF, modeS, func=None, call=False, clear=False):
    # 仅内部调用
    # 用于map操作
    # 从FISPACT输出文件特定的文本中解析出光子产额
    # allItem--input--某FISPACT文件内容
    # gamma--output--光子产额总量
    assert type(allItem) == str
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)

    tmp = modeF.findall(allItem)[-1]

    gamma = float(modeS.search(tmp).group(0))
    return gamma

def _getAllItem(path, dir, func=None, call=False, clear=False):
    # 仅内部调用
    # 用于map操作
    # 从FISPACT工作目录里解析出文件
    # path--input(list)--FISPACT工作目录
    # dir--input(list)--材料对应目录
    # *--output--所有output文件内容
    assert type(path) == str
    assert type(dir) == str
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)

    files = os.listdir(path + '/' + dir)
    files = list(filter(lambda name: name[-2:] == '.o', files))
    assert len(files) == 1
    with open(path + '/' + dir + '/' + files[0]) as f:
        return f.read()

def _extractVol(structure, solids, materials, elements, func=None, call=False, clear=False):
    # 仅内部调用
    # 用于map操作
    # structure--input--list--解析的源文本
    # solids--input--list--物体信息
    # materials--input--list--材料信息
    # elements--input--list--元素信息
    # volume--output--list--物质信息
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)

    solidRef = structure.xpath('solidref/@ref')[0]
    materialRef = structure.xpath('materialref/@ref')[0]
    if solids.__contains__(solidRef):
        volume = solids[solidRef]
    else:
        volume = Volume(solidRef)
    items = materials[materialRef]
    volume.matName = materialRef
    volume.matD = items[0]
    volume.matGre = [item + elements[item[0]] for item in items[1]]
    return volume


def _defineVol(name, volume, func=None, call=False, clear=False):
    # 仅内部调用
    # 用于map操作
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)

    newVol = Volume(name)
    newVol.property = volume.tag
    return newVol

def _m2ev(raw, flag):
    # 仅内部调用
    # 将MeV转换为eV
    # raw--input--list，原始数据集合
    # flag--input--str，'e'或'E'，科学记数法的表示方式
    # result--output--list，处理后的数据集合
    assert type(raw) == list
    assert type(flag) == str
    result = []
    for i in range(len(raw)):
        tmp = raw[i].split(flag)
        if len(tmp) == 1:
            raw[i] = float(tmp[0]) * 1000000
        else:
            raw[i] = float(tmp[0]) * (10 ** (6 + int(tmp[1])))
        tmp = '%E' % raw[i]
        tmp = tmp.replace('+', '')
        mode = re.compile(r'E0+$')
        tmp = mode.sub('', tmp)
        mode = re.compile(r'E0+')
        tmp = mode.sub('E', tmp)
        mode = re.compile(r'E-0+')
        tmp = mode.sub('E-', tmp)
        result.append(tmp)
    return result

def _getName(mode, mid, i, func=None, call=False, clear=False):
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)
    return mode.search(mid[i]).group(0)[6:-1]

def _getEnergy(mode, mid, i, func=None, call=False, clear=False):
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)
    return float(mode.search(mid[i]).group(0)[16:])

def _getVolume(mode, mid, i, func=None, call=False, clear=False):
    if func:
        assert type(call) == bool
        assert type(clear) == bool
    if call:
        func(clear)
    return float(mode.search(mid[i]).group(0)[14:])

def readf(path, maxFlag=20., funcTime=None, funcOne=None, interval=100):
    # 读取FISPACT输出文件并解析出所有材料的光谱分布
    # path--input--FISPACT输出文件顶层目录
    # maxFlag--input--光子分布无穷大等效值
    # allDistributes--output--提取出的所有材料的光谱类
    if type(maxFlag) == int:
        maxFlag = float(maxFlag)

    dirs = os.listdir(path)
    length = len(dirs)

    maxFlagList = [maxFlag] * length
    pathList = [path] * length
    gModeF = re.compile(r'Total gammas \(per cc per second\) {6}\d\.\d{5}E[+-]\d{2}')
    gModeFList = [gModeF] * length
    gModeS = re.compile(r'\d.\d+E[+-]\d*')
    gModeSList = [gModeS] * length
    dModeF = re.compile(r'\(0.0 -0.01 {2}MeV\).+?DOSE', re.S)
    dModeFList = [dModeF] * length
    dModeSList = gModeSList
    dModeT = re.compile(r'\(\d+.\d+ *-+>?\d*.*\d* *MeV\)')
    dModeTList = [dModeT] * length
    dModeL = re.compile(r'\d{1,2}\.\d{1,2}')
    dModeLList = [dModeL] * length
    if funcTime:
        callTime = max(length // interval, 1)
        # 回调告知总调用次数
        funcOne(length // callTime, length)
        funList = [funcTime] * length
        callList = [True if i % callTime == 0 or i == 0 else False for i in range(length)]
        clearList = [False] * length
        clearList[0] = True
        # 每次回调告知进度
        allItemList = list(map(_getAllItem, pathList, dirs, funList, callList, clearList))
        gammaList = list(map(_extractGamma, allItemList, gModeFList, gModeSList, funList, callList, clearList))
        disList = list(map(_extractDis, allItemList, maxFlagList, dModeFList, dModeSList, dModeTList, dModeLList, funList, callList, clearList))
    else:
        allItemList = list(map(_getAllItem, pathList, dirs))
        gammaList = list(map(_extractGamma, allItemList, gModeFList, gModeSList))
        disList = list(map(_extractDis, allItemList, maxFlagList, dModeFList, dModeSList, dModeTList, dModeLList))
    allDistributes = dict(zip(dirs, zip(gammaList, disList)))

    return allDistributes

def readg(path, funcTime=None, funcOne=None, interval=100):
    # 读取GDML文件并解析出各材料物质信息
    # path--input--GDML文件位置
    # allStructure--output--所有材料填充物质信息
    try:
        root = etree.parse(path)
    except:
        raise FileNotFoundError

    # 获取元素定义
    eleTree = root.xpath('./materials/element')
    eleName = [ele.xpath('@name')[0] for ele in eleTree]
    # 序号0-3为int原子序数，double原子质量，string 原子简称
    # eleInf = [(ele.xpath('@Z')[0],ele.xpath('atom/@value')[0],ele.xpath('@formula')[0]) for ele in eleTree ]
    # 暂定不需要formula
    eleInf = [(int(ele.xpath('@Z')[0]), float(ele.xpath('atom/@value')[0])) for ele in eleTree]
    elements = dict(zip(eleName, eleInf))

    # 定义原子数-元素名字典
    tmp = [e[0] for e in eleInf]
    zElements = dict(zip(tmp, eleName))
    # 获取材料定义
    # 对于无引用的材料，定义同名新元素，假装引用
    matTree = root.xpath('./materials/material')
    matName = [mat.xpath('@name')[0] for mat in matTree]
    matD = [mat.xpath('D/@value')[0] for mat in matTree]
    matEles = [
        [(fac.xpath('@ref')[0], float(fac.xpath('@n')[0])) for fac in mat.xpath('fraction')] if len(
            mat.xpath('@Z')) == 0 else [(
            zElements[int(mat.xpath('@Z')[0])], float(mat.xpath('D/@value')[0]))] for mat in matTree]

    materials = dict(zip(matName, zip(matD, matEles)))

    # 获取栅元定义
    solid = root.xpath('./solids')[0]

    nameList = list(map(lambda v: v.xpath('@name')[0], solid))
    if funcTime:
        length = len(solid)
        callTime = max(length // interval, 1)
        # 回调告知总调用次数
        funcOne(length // callTime, length)
        funList = [funcTime] * length
        callList = [True if i % callTime == 0 or i == 0 else False for i in range(length)]
        clearList = [False] * length
        clearList[0] = True
        # 每次回调告知进度
        volList = list(map(_defineVol, nameList, solid, funList, callList, clearList))
    else:
        volList = list(map(_defineVol, nameList, solid))
    solids = dict(zip(nameList, volList))

    # 补充栅元的物质信息和空间信息
    structures = root.xpath('./structure/volume')
    strucLen = len(structures)
    solidList = [solids] * strucLen
    matList = [materials] * strucLen
    eleList = [elements] * strucLen
    if funcTime:
        vols = list(map(_extractVol, structures, solidList, matList, eleList, funList, callList, clearList))
    else:
        vols = list(map(_extractVol, structures, solidList, matList, eleList))
    names = list(map(lambda structure: structure.xpath('@name')[0][6:], structures))

    deleteInx = -1

    try:
        deleteInx = names.index('')
    except ValueError:
        raise
    if deleteInx > -1:
        names.pop(deleteInx)
        vols.pop(deleteInx)
    allStructure = dict(zip(names, vols))
    return allStructure

def readj(path, funcTime=None, funcOne=None, interval=100):
    # 读取JMCT输出文件并解析出各材料物质信息
    # path--input--JMCT输出文件位置
    # neutron--output--所有材料物质信息
    assert type(path) == str
    neutron = Data('Transporting')
    with open(path, 'r') as f:
        allItem = f.read()

    mode = re.compile(r'energy_bin[ \de\-,=.]+')
    mid = mode.search(allItem).group(0)
    mid = mid.replace(' ', '')
    mid = mid.strip('energy_bin=')
    mode = re.compile(r'^/c+$')
    mid = mode.sub('', mid)
    mid = mid.split(',')
    neutron.eneBin = _m2ev(mid, 'e')
    neutron.eneNum = len(neutron.eneBin)

    # 几何体相关信息储存
    mode = re.compile('Tally4_0,(.+?)---', re.S)
    mid = mode.findall(allItem)
    # 储存关心的几何体数量
    neutron.cellNum = len(mid)
    midList = [mid] * neutron.cellNum
    iList = [i for i in range(neutron.cellNum)]
    nameMode = re.compile(r'cell: (.+?),', re.S)
    nameModeList = [nameMode] * neutron.cellNum
    eneMode = re.compile(r'total +\d.\d+e[+-]\d{2,3}')
    eneModeList = [eneMode] * neutron.cellNum
    volMode = re.compile(r'volume\(cm\^3\): \d+.\d+e?[+-]?\d{0,2}')
    volModeList = [volMode] * neutron.cellNum
    if funcTime:
        callTime = max(neutron.cellNum // interval, 1)
        # 回调告知总调用次数
        funcOne(neutron.cellNum // callTime, neutron.cellNum)
        funList = [funcTime] * neutron.cellNum
        callList = [True if i % callTime == 0 or i == 0 else False for i in range(neutron.cellNum)]
        clearList = [False] * neutron.cellNum
        clearList[0] = True
        # 每次回调告知进度
        name = list(map(_getName, nameModeList, midList, iList, funList, callList, clearList))
        energy = list(map(_getEnergy, eneModeList, midList, iList, funList, callList, clearList))
        volume = list(map(_getVolume, volModeList, midList, iList, funList, callList, clearList))
    else:
        name = list(map(_getName, nameModeList, midList, iList))
        energy = list(map(_getEnergy, eneModeList, midList, iList))
        volume = list(map(_getVolume, volModeList, midList, iList))

    deleteInx = -1
    try:
        deleteInx = name.index('World')
    except ValueError:
        raise
    if deleteInx > -1:
        name.pop(deleteInx)
        energy.pop(deleteInx)
        volume.pop(deleteInx)
    neutron.cellInfo = dict(zip(name, zip(energy, volume)))
    return neutron