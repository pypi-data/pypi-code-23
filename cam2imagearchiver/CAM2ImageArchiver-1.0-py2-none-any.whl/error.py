"""
Copyright 2017 Purdue University

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Define the exceptions raised by the camera package.
"""


class Error(Exception):
    """
    Represent a generic error.

    """
    pass


class UnreachableCameraError(Error):
    """
    Represent an error when a camera is unreachable.
    """
    pass


class CorruptedFrameError(Error):
    """
    Represent an error when a camera stream frame is corrupted.
    """
    pass


class ClosedStreamError(Error):
    """
    Represent an error when a stream is closed and a frame is requested.
    """
    pass
