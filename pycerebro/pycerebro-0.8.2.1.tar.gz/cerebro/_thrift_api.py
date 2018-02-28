# Copyright 2017 Cerebro Data Inc.
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
# This packages contains the python compiled bindings from the thrift idl. We consider
# this as part of the client API.
#

# pylint: disable=wrong-import-position

from __future__ import absolute_import

import os
import sys

from thriftpy import load

# dynamically load the thrift modules
thrift_dir = os.path.join(os.path.dirname(__file__), 'thrift')
CerebroRecordService = load(os.path.join(thrift_dir, 'CerebroRecordService.thrift'),
                      include_dirs=[thrift_dir])
RecordService = load(os.path.join(thrift_dir, 'RecordService.thrift'),
                      include_dirs=[thrift_dir])
sys.modules[CerebroRecordService.__name__] = CerebroRecordService
sys.modules[RecordService.__name__] = RecordService

# import the thrift objects
from RecordService import (
    TGetDatabasesParams, TGetTablesParams, TPlanRequestParams,
    TExecTaskParams, TFetchParams, TNetworkAddress, TRecordFormat, TTypeId,
    TRequestType, RecordServiceWorker)
from CerebroRecordService import (
    CerebroRecordServicePlanner, TExecDDLParams)
