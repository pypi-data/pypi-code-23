#!/usr/bin/env python2.7

from __future__ import print_function

import sys

'''
Converts a parameter file from "formfiller" result to original format. 

Implemented changes:
 - Change all the columns info to a "$" sign convention. 
 - Add a sidebar section
 - Convert the RGB(rgb) to a semi-colon format. 
- Change the start of all the "Element" to "BAR"
- Change the start of all the "Title" to "TEXT"
- Convert the names of the figure types

- Remove the version number from the top?
- Do we need to handle spaces?
'''


def revert_from_formfiller(allList):
    print(allList)

    #Remove the header
    allList = allList[1:] 

    #Conver the element to bar
    for i in allList:
        if i[0]=="Element":
            i[0]="BAR"
    
    #Conver the figure types
    for i in allList:
        if len(i)>1:
            if i[1]=="Bar plot": i[1]="barplot"
            if i[1]=="Violin plot": i[1] ="violin"
            if i[1]=="Box plot": i[1]="boxplot"
    
    #Change the start of Title to TEXT
    for i in allList:
        if i[0]=="Title": i[0]="TEXT"

    for i in allList:
        if i[0]=="theme" and i[1]=="Light":
            i[1]="light"
        if i[0]=="theme" and i[1]=="Dark":
            i[1]="dark"   


    #Now, update each section: 
    figureSection = False
    for i in allList:
        if i[0]=="parameter" and i[1]=="figure":
            figureSection= True
            continue
        if i[0]=="parameter" and i[1]!="figure":
            figureSection = False
        if figureSection==True and len(i)>2 and i[0] in ["BAR"]:
            splitSections = i[2].split(",")
            newcolumn = list()
            for j in splitSections:
                if "-" in j:
                    newcolumn += [str(x) for x in range(int(j.split("-")[0]), int(j.split("-")[1])+1)]
                else:
                    newcolumn.append(j)
            newcolumn = [str(x) for x in newcolumn]
            i[2] = "$".join(newcolumn)
        if figureSection==True and i[0] in ["BAR", "TEXT"]:                
            if len(i)>4: 
                rgbValue = i[4].replace("rgb", "").replace(",", ";").replace(" ", "")
                i[4] = rgbValue
            else:
                i.append("(150;150;150)")
        if figureSection==True and i[0] in ["figuretype"]:
            if i[1]=="Title": i[1] = "title"                


    #Add sidebar section
    panelSection  = False
    panelList = list()
    for i in allList:
        if i[0]=="parameter" and i[1]=="panel":
            panelSection = True
            continue
        if i[0]=="parameter" and i[1]!="panel":
            panelSection = False
        if panelSection==True and i[0]=="panelkey":
            panelList.append(i[1])
        if panelSection==True and i[0]=="FIGURE":
            i[2] = str(float(i[2])*100)
            i[4] = str(int(i[4])+1)
            i[5] = str(int(i[5])+1)
        #Fix the rows
        
        
    allList.append(["parameter", "sidebar"])
    allList.append(["START"])
    allList.append(["SEARCH", "SEARCH"])
    allList.append(["SPACE"])
    for i in panelList:
        allList.append(["PANEL", i, i])

    fileOUT = open("tmp.csv", "w")
    for i in allList:
        fileOUT.write(",".join(i) + "\n")
    fileOUT.close()


    return allList




