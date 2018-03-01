#!/usr/bin/env python2.7

from __future__ import print_function


'''
outputPath is not used 

'''

import os
import helper_funcs as HF

class PanelClass():
    def __init__(self):
        self.paramDict = dict()

    def initialize_from_mat(self, paramMat):
        self.paramDict = HF.initialize_from_paramMat(paramMat)
        HF.setVar(self, self.paramDict)

    def setup(self):
        pass

    # def __init__(self, buttonName, buttonKey, buttonPath):
    #     self.buttonName = buttonName
    #     self.buttonKey = buttonKey
    #     self.buttonPath = buttonPath
    #     self.paramDir = os.path.dirname(buttonPath)
    #     self.buttonParamDict = dict()
    #     self.figureList = list()

    #     self.read_in_button_file()

    # def read_in_button_file(self):
    #     with open(self.buttonPath) as F:
    #         startFlag = 0
    #         self.layoutList = list()
    #         for i in F:
    #             i=i.rstrip().split(",")
    #             if startFlag==0:
    #                 if i[0]=="setkey": self.buttonParamDict["setkey"] = i[1]
    #                 elif i[0]=="search": self.buttonParamDict["search"] = i[1]
    #                 elif i[0]=="citetext": self.buttonParamDict["citetext"] = ", ".join(i[1:])
    #                 elif i[0]=="citelink": self.buttonParamDict["citelink"] = i[1]
    #                 elif i[0]=="setname": self.buttonParamDict["setname"] = ", ".join(i[1:])
    #                 elif i[0]=="info": self.buttonParamDict["info"] = ", ".join(i[1:])
    #                 elif i[0]=="dataset": self.buttonParamDict["dataset"] = i[1]
    #                 elif i[0]=="skip": self.buttonParamDict["skip"] = i[1]
    #                 elif i[0]=="gcol": self.buttonParamDict["gcol"] = i[1]
    #                 elif i[0]=="ylab": self.buttonParamDict["ylab"] = i[1]
    #                 elif i[0]=="START": startFlag = 1
    #             else:
    #                 if i[0] in ["FIGURE", "TITLE"]:
    #                     figureObject = FC.FigureClass(i[1], self.paramDir)
    #                     self.figureList.append(figureObject)
    #                     self.layoutList.append([i[0], figureObject.figurekey, i[2:]])
    #                 elif i[0] == "BREAKER":
    #                     self.layoutList.append([i[0], "breaker", i[2:]])
    #                 elif i[0] =="SPACER":
    #                     self.layoutList.append([i[0], "spacer", i[2:]])


    #     self.buttonParamDict["layoutList"] = self.layoutList



