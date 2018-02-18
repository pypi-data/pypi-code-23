'''
--------------------------------------------------------------------------
Copyright (C) 2017-2018 Lukasz Laba <lukaszlab@o2.pl>

This file is part of Tebe.

Tebe is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Tebe is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

import os
import subprocess

import app_utils

class Rst2PdfBuilder():
    def __init__(self):
        #---
        self.confdir = app_utils.abspath('pycore/rst2pdf_conf_template')
        self.where_pdf_saved = None

    def build_pdf_from_rst_file(self, source_rst_filname_path, out_pdf_filname_path):
        self.where_pdf_saved = None
        #---
        #out_pdf_filname_path = source_rst_filname_path.replace('.rst', '.pdf')
        proc = subprocess.Popen([   'rst2pdf',
                                    source_rst_filname_path,
                                    out_pdf_filname_path        ])
        proc.wait()
        #---
        self.where_pdf_saved = out_pdf_filname_path 
        print 'Rst2PdfBuilder build_pdf done'