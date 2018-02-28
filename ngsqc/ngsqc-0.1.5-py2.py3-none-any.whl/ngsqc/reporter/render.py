#!/usr/bin/env python
#coding=utf-8
from jinja2 import Template
import sys
import os
import base64
import xlrd
reload(sys)
sys.setdefaultencoding('utf-8')
class Argsor:

    def __init__(self,report):
        self.dir = report
        self.args = {}
        self.args["per_base_quality"] = []
        self.args["per_sequence_quality"] = []
        self.args["per_sequence_gc_content"] = []
        self.args["per_base_sequence_content"] =[]
        self.args["duplication_levels"] = []
        self.get_images() 
        self.get_table()

    def convert_table(self,table):
        data = xlrd.open_workbook(table)
        table_variable = data.sheets()[0]
        return table_variable   

    def get_images(self):
        for root,dirs,files in os.walk(report):
            for file in files:
                absfile = os.path.join(root,file)
                if file == "per_base_quality.png":
                    self.args["per_base_quality"].append(absfile)
                if file == "per_sequence_quality.png":
                    self.args["per_sequence_quality"].append(absfile)
                if file == "per_sequence_gc_content.png":
                    self.args["per_sequence_gc_content"].append(absfile)
                if file == "per_base_sequence_content.png":
                    self.args["per_base_sequence_content"].append(absfile)
                if file == "duplication_levels.png":
                    self.args["duplication_levels"].append(absfile)

    def get_table(self):
        for root,dirs,files in os.walk(report):
            for file in files:
                absfile = os.path.join(root,file)
                if file == "fastqsInfo.xls":
                    self.args["table3_4"] = self.convert_table(absfile)
                    return

    
def render(template,args):
    fp = open(template)
    tem = Template(fp.read())
    tem.globals['open'] = open
    tem.globals['base64'] = base64.b64encode
    md = tem.render(**args)
    return md
def main(report,template,out):
    argsor = Argsor(report)
    args = argsor.args
    md = render(template,args)

    fp = open(out,"w")
    fp.write(md)
    fp.close()

    
if __name__ == "__main__":

    usage='''
Usage:
  render.py -d <reportDir> -t <md> -o <md>
  render.py -h | --help

Options:
    -d <reportDir> --dir=<reportDir>    report directory
    -t <md> --template=<md>             markdown template
    -o <md> --out=<md>                  markdown rendered

    '''
    from docopt import docopt
    args = docopt(usage)
    report = args["--dir"]
    templ = args["--template"]
    out = args["--out"]
    main(report,templ,out)
