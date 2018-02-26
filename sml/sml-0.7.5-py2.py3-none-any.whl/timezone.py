"""Python 2/3 compatibility for timezone.utc"""

# Copyright 2016-2017 ASI Data Science
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import six


if six.PY2:
    from datetime import tzinfo, timedelta

    _ZERO = timedelta(0)

    class UTC(tzinfo):
        """UTC"""

        def utcoffset(self, dt):
            return _ZERO

        def tzname(self, dt):
            return 'UTC'

        def dst(self, dt):
            return _ZERO

    utc = UTC()
else:
    from datetime import timezone
    utc = timezone.utc
