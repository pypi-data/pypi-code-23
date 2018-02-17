#/********************************************************************************
#* AUDETEMI INC. ("COMPANY") CONFIDENTIAL
#*_______________________________________
#*
#* Unpublished Copyright (c) 2015-2017 [AUDETEMI INC].
#* http://www.audetemi.com.
#* All Rights Reserved.
#*
#* NOTICE:  All information contained herein is, and remains the property of COMPANY. * The intellectual and #technical concepts contained herein are proprietary to COMPANY * and may be covered by U.S. and Foreign Patents, #patents in process, and are
#* protected by trade secret or copyright law.
#* Dissemination of this information or reproduction of this material is strictly
#* forbidden unless prior written permission is obtained from COMPANY.
#* Access to the source code contained herein is hereby forbidden to anyone except
#* current COMPANY employees, managers or contractors who have executed
#* Confidentiality and Non-disclosure agreements explicitly covering such access.
#*
#* The copyright notice above does not evidence any actual or intended publication or * disclosure of this source #code, which includes information that is confidential
#* and/or proprietary, and is a trade secret, of the COMPANY.
#*
#* ANY SUB-LICENSING, REPRODUCTION, REVERSE ENGINEERING, DECOMPILATION, MODIFICATION, * DISTRIBUTION, PUBLIC #PERFORMANCE, OR PUBLIC DISPLAY OF OR THROUGH USE OF THIS
#* SOURCE CODE WITHOUT THE EXPRESS WRITTEN CONSENT OF COMPANY IS STRICTLY PROHIBITED,
#* AND IN VIOLATION OF APPLICABLE LAWS AND INTERNATIONAL TREATIES.  THE RECEIPT OR
#* POSSESSION OF THIS SOURCE CODE AND/OR RELATED INFORMATION DOES NOT CONVEY OR IMPLY * ANY RIGHTS TO REPRODUCE, #DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO MANUFACTURE,
#* USE, OR SELL ANYTHING THAT IT MAY DESCRIBE, IN WHOLE OR IN PART.
#*/
from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from multimedia_chat import views


urlpatterns = [
    url(r'^chat/$', views.MessageList.as_view(),
        name='chat'),
    # url(r'^chat/feeds/$', views.RetrieveLatestFeed.as_view(),
    #     name='chat_feeds'),
    # url(r'^update/chat/$', views.MessageActivity.as_view(),
    #     name='update_chat'),
    # url(r'^message/(?P<id>[0-9]+)/$', views.MessageDetailAPI.as_view(),
    #     name='message_detail'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
