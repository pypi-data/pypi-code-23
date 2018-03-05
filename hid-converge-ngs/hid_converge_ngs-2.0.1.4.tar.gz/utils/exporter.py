import os,sys
import xlsxwriter #python3 -m easy_install xlsxwriter

class STRExport(object):
    def __init__(self,fileName):

        self.fileName = fileName
        self.workbook = xlsxwriter.Workbook(self.fileName)
        self.columns = ['sample_uid','sample_name','marker','allele','status','coverage','short sequence','long sequence','rsid']
        self.fontSize = 12

    def addWorksheet(self,name):
        if self.workbook:
            return self.workbook.add_worksheet(name)

    def setColumns(self,worksheet,columns):
        self.columns = columns

    def write(self,worksheet,rows):
        worksheet.set_column(0,len(self.columns),self.fontSize)
        worksheet.write('A1',"Verstion 1.0")
        worksheet.write_row('A2',self.columns)
        count = 2
        for row in rows:
                rowNum = "A" + str(count+1)
                worksheet.write_row(rowNum, row)
                count += 1






