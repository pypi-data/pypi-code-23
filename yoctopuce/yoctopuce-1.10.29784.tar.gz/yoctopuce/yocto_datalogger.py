# -*- coding: utf-8 -*-
# *********************************************************************
# *
# * $Id: yocto_datalogger.py 28125 2017-07-25 07:53:27Z seb $
# *
# * Implements yFindDataLogger(), the high-level API for DataLogger
# *
# * - - - - - - - - - License information: - - - - - - - - -
# *
# *  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
# *
# *  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
# *  non-exclusive license to use, modify, copy and integrate this
# *  file into your software for the sole purpose of interfacing
# *  with Yoctopuce products.
# *
# *  You may reproduce and distribute copies of this file in
# *  source or object form, as long as the sole purpose of this
# *  code is to interface with Yoctopuce products. You must retain
# *  this notice in the distributed source file.
# *
# *  You should refer to Yoctopuce General Terms and Conditions
# *  for additional information regarding your rights and
# *  obligations.
# *
# *  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
# *  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING
# *  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
# *  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
# *  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
# *  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
# *  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR
# *  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT
# *  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
# *  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
# *  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
# *  WARRANTY, OR OTHERWISE.
# *
# *********************************************************************/

__docformat__ = 'restructuredtext en'
from yoctopuce.yocto_api import *

# YDataLogger class has been moved to yocto_api.py