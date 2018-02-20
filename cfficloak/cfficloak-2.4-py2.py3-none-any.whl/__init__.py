# Copyright (c) 2017, Andrew Leech <andrew@alelec.net>
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# The full license is also available in the file LICENSE.apache-2.0.txt


''' A collection of convenience classes and functions for CFFI wrappers. '''

from __future__ import absolute_import
from .ffi import FFI
from .wrap import wrap, wrapall
from .arrays import nparrayptr, nparray, carray
from .cstruct import CStruct, CStructType, CUnion, CUnionType
from .enums import wrapenum
from .functions import CFunction, cmethod, function_skeleton, outarg, cproperty, cstaticmethod, NullError
from .typedef import CType
from .patches import *

def cloak(mod):
    """
    Initial use function to wrap all attributes in a cffi library

    :param mod: either a build cffi module or the return from ffi.dlopen('library')
    :return: wrapped version of the provided lib
    """
    with FFI(mod) as ffi:
        return wrapall(ffi=ffi, lib=mod.lib)



