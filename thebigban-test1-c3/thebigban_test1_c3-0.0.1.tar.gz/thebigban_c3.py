from collections import OrderedDict

class A(object):
    pass


class B(A):
    pass


class C(A):
    pass


class D(A):
    pass


class E(B):
    pass


class F(C):
    pass

class G(D):
    pass

class H(E, F):
    pass

class I(F, G):
    pass

class J(H, I):
    pass

def get_P(cls, d=dict()):  #通过__bases__获取继承关系中的各个类的父类
    d[cls.__name__] = cls.__bases__
    if cls.__bases__[0] != object:
        for c in cls.__bases__:
            d.update(get_P(c, d))
    return d


def filter_dict(order_dict):  #get_P函数中获取的是类作为值的字典，filter_dict则将它的值转化成类名（str)
    temp_dict = OrderedDict()
    for i,j in order_dict.items():
        x = []
        for v in j:
            x.append(v.__name__)
        temp_dict[i] = x
    return temp_dict


def get_Child(order_dict):  #通过获取的继承关系中的类的父类字典，将其转换成各个类的子类的字典。
    temp = {}
    L = list(set(order_dict.keys()))
    for i in L:
        temp_list = []
        for j, k in order_dict.items():
            if i in k:
                temp_list.append(j)
        temp[i] = temp_list
    return temp


frame = []
n_frame = []


def get_frame(list_cls):  #获取继承关系网中的层级结构。
    if list_cls == [object]:
        return
    sub_frame = []
    name_frame = []
    for i in list_cls:
        if not sub_frame:
            for j in i.__bases__:
                sub_frame.append(j)
                name_frame.append(j.__name__)
        else:
            for k in i.__bases__:
                if k not in sub_frame:
                    sub_frame.append(k)
                    name_frame.append(k.__name__)
    frame.append(sub_frame)
    n_frame.append(name_frame)
    get_frame(sub_frame)


def countMax(L, count=[]):#计算层级结构中的最大层，返回最大层的类的数量。
    for i in L:
        if isinstance(i, list):
            countMax(i)
            count.append(len(i))
    return count





def fake_C3(o_dict, frame_list):  #模拟的C3算法
    print('start:', o_dict)
    if not o_dict:
        mro.append('object')
        return
    L = []
    for i, j in o_dict.items():
        if not j:
            L.append(i)
    if len(L) == 1:
        mro.append(L[0])
        o_dict.pop(L[0])
        print(L[0])
        for i, j in o_dict.items():
            if L[0] in j:
                o_dict[i].remove(L[0])
    else:
        sort_list = []
        max_len = max(countMax(frame_list))
        for i in L:
            sort_list.append([i, max_len])
        #sort_dict = OrderedDict.fromkeys(L, )
        for i, j in enumerate(sort_list):
            for k in frame_list:
                if j[0] in k:
                    pos = k.index(j[0])
                    if pos < j[1]:
                        sort_list[i][1] = pos
            # for n in frame_list:
            #     if k in n:
            #         #pos = n.index(k) - frame_list.index(n)
            #         pos = n.index(k)
            #         if pos < sort_dict[k]:
            #             sort_dict[k] = pos
        #sort_list = list(sort_dict.items())
        #print('before:',sort_list)
        sort_list = sorted(sort_list, key=lambda x: x[1])
        #print('after:',sort_list)
        first = sort_list[0][0]
        # for i in sort_dict:
        #     first = i
        #     break
        mro.append(first)
        #print(first)
        o_dict.pop(first)
        for i, j in o_dict.items():
            if first in j:
                o_dict[i].remove(first)
                
    fake_C3(o_dict, frame_list)

get_frame([F])
print(n_frame)
# print(countMax(n_frame))
z = filter_dict(get_P(F))
# print(z)
z = get_Child(z)
# print(z)
mro = []
# n_frame = [['D', 'E'], ['B', 'C'], ['A'], ['object']]
#
fake_C3(z, n_frame)
print(mro)
print(list(map(lambda x: x.__name__, F.__mro__)))

