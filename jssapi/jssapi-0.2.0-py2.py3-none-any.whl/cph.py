# -*- coding: utf-8 -*-
####################################################################################################
#
# Copyright (c) 2015, JAMF Software, LLC.  All rights reserved.
#
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are met:
#               * Redistributions of source code must retain the above copyright
#                 notice, this list of conditions and the following disclaimer.
#               * Redistributions in binary form must reproduce the above copyright
#                 notice, this list of conditions and the following disclaimer in the
#                 documentation and/or other materials provided with the distribution.
#               * Neither the name of the JAMF Software, LLC nor the
#                 names of its contributors may be used to endorse or promote products
#                 derived from this software without specific prior written permission.
#
#       THIS SOFTWARE IS PROVIDED BY JAMF SOFTWARE, LLC "AS IS" AND ANY
#       EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#       WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#       DISCLAIMED. IN NO EVENT SHALL JAMF SOFTWARE, LLC BE LIABLE FOR ANY
#       DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#       (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#       LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#       ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#       SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#   Author: Ryan Meyers
#   Last Modified: 04/4/2016
#   Version: 1.0 Beta 1
#
#   Description:  This script will generate a configuration profile
#
#   Enter JSS URL as https://yourjssurl.com:8443
#
####################################################################################################


import uuid
import plistlib
try:
    from html import escape as htmlescape
except:
    from cgi import escape as htmlescape


class ConfigProfileHelper:

    profile_name = ""
    profile_description = ""
    profile_organization = ""
    profile_uuid = str(uuid.uuid4())

    payloads = []

    def __init__(self,name,description,organization):
        self.profile_name = name
        self.profile_description = description
        self.profile_organization = organization
        self.profile_uuid = str(uuid.uuid4())
        self.payloads[:] = []

    def add_restrictions_payload(self,restrictions):
        self.add_payload("com.apple.applicationaccess",restrictions)

    def add_payload(self,payload_type,content):
        payload_uuid = str(uuid.uuid4())
        content['PayloadUUID'] = payload_uuid
        content["PayloadOrganization"] = self.profile_organization
        content["PayloadIdentifier"] = payload_uuid
        content['PayloadDisplayName'] = self.profile_name
        content['PayloadType'] = payload_type
        content["PayloadVersion"] = 1
        content["PayloadEnabled"] = True

        self.payloads.append(content)



    # Where all the magic happens
    def generate_profile(self, escape=False):
        profile = {}

        profile['PayloadUUID'] = self.profile_uuid
        profile['PayloadType'] = "Configuration"
        profile['PayloadOrganization'] = self.profile_organization
        profile['PayloadIdentifier'] = self.profile_uuid
        profile['PayloadDisplayName'] = self.profile_name
        profile['PayloadDescription'] = self.profile_description
        profile['PayloadVersion'] = 1
        profile['PayloadEnabled'] = True
        profile['PayloadRemovalDisallowed'] = True

        profile['PayloadContent'] = self.payloads
        formatted_profile = plistlib.writePlistToString(profile)

        if escape:
            return htmlescape(formatted_profile)
        else:
            return formatted_profile
