import logging
import os
import sys

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    UpdateAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# from commons import error_conf
from models import (
    Message
)
from serializers import (
    MessageSerializer,
    MessageViewSerializer
)
from system_error import (
    check_for_private_message_error,
    # check_for_retrive_feeds_error,
    # check_for_update_message_error
)


###############################################################################
# Private Messages Between User and Assigned ticket
###############################################################################
class MessageList(ListCreateAPIView):
    """
    This Class is for Creating and searching
    Message API
    """
    queryset = Message.objects.all()
    serializer_class = MessageViewSerializer

    def get(self, request, format=None, **kwargs):
        """
        This Method Retrieve all the message of given ticket
        if request user is part of same
        """
        data = request.GET
        room_id = data.get('room_id')
        messgae_obj = Message.objects.filter(room_id=room_id)

        if not messgae_obj:
            response_obj = {
                "count": 0,
                "next": None,
                "previous": None,
                "results": []
            }
            return Response(response_obj)

        messgae_obj = messgae_obj[0]

        message_data = Message.objects.filter(room_id=room_id).order_by('-created_at')

        page = self.paginate_queryset(message_data)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(message_data, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        """
        This method checks whether the request is coming
        from the User or Admin and saves
        Message
        """

        error_checks = check_for_private_message_error(request)
        if error_checks:
            return Response(error_checks,
                            status=status.HTTP_412_PRECONDITION_FAILED)

        message_data   = request.data

        serializer = MessageSerializer(data=message_data)
        if serializer.is_valid():
            message = serializer.save()

            serializer = MessageViewSerializer(message)
            return Response({"message": serializer.data,
                             "success": True},
                            status=status.HTTP_201_CREATED)
        else:
            logging.info(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)


# ###############################################################################
# # Private Messages Between User and AAssigned ticket
# ###############################################################################
# class MessageActivity(UpdateAPIView):
#     """
#     This Class is for Creating and searching
#     Message API
#     """
#     queryset = Message.objects.all()
#     serializer_class = MessageSerializer
#     authentication_classes = [OAuth2Authentication]
#     permission_classes = [IsAuthenticated]

#     def put(self, request, *args, **kwargs):
#         return Response(status.HTTP_405_METHOD_NOT_ALLOWED)

#     def patch(self, request, format=None):
#         """
#         This method checks whether the request is coming
#         from the sender or receiver and performs acction according to
#         Message action
#         """

#         message_data = request.data

#         error_checks = check_for_update_message_error(request)

#         if error_checks:
#             return Response(error_checks,
#                             status=status.HTTP_412_PRECONDITION_FAILED)

#         message_obj = Message.objects.get(id=message_data.get('message_id'))

#         if request.user == message_obj.receiver and message_data['action'] == 'READ':
#             message_data['to_user_read'] = True
#         elif request.user == message_obj.receiver and message_data['action'] == 'UNREAD':
#             message_data['to_user_read'] = False
#         elif request.user == message_obj.receiver and message_data['action'] == 'DELETE':
#             message_data['to_user_delete'] = True
#         elif request.user == message_obj.sender and message_data['action'] == 'DELETE':
#             message_data['from_user_delete'] = True
#         else:
#             return Response(error_conf.UNAUTHORIZED_ACCESS,
#                             status=status.HTTP_403_FORBIDDEN)

#         del message_data['action']

#         serializer = MessageSerializer(message_obj,
#                                        data=message_data,
#                                        partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,
#                             status=status.HTTP_200_OK)
#         return Response(serializer.errors,
#                         status=status.HTTP_400_BAD_REQUEST)


# ###############################################################################
# # Private Messages  Latest Feeds API
# ###############################################################################
# class RetrieveLatestFeed(APIView):
#     """
#     This Class is for Creating and searching
#     Message API
#     """
#     queryset = Message.objects.all()
#     serializer_class = MessageSerializer
#     authentication_classes = [OAuth2Authentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request, format=None):

#         if request.data:

#             inputDetails = request.data

#             error_checks = check_for_retrive_feeds_error(request)
#             if error_checks:
#                 return Response(error_checks,
#                                 status=status.HTTP_412_PRECONDITION_FAILED)

#             room_id = inputDetails.get('room_id')
#             latest_message_id = inputDetails.get('latest_message_id')

#             message_filtering_kwargs = {
#                 'room_id': room_id,
#                 'id__gt': latest_message_id
#             }

#             latest_private_message = Message.objects.filter(**message_filtering_kwargs)
#             message_serializer = MessageViewSerializer(
#                     latest_private_message,
#                     many=True
#             )

#             return Response({
#                 'success': True,
#                 'latest_chat_messages': message_serializer.data
#             })
#         return Response({
#             'success': False,
#             status: status.HTTP_412_PRECONDITION_FAILED
#             })


# ###############################################################################
# # Private Messages Detail API
# ###############################################################################
# class MessageDetailAPI(APIView):
#     """
#     This Class is for Details of 
#     Message API
#     """
#     queryset = Message.objects.all()
#     serializer_class = MessageSerializer
#     authentication_classes = [OAuth2Authentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, id, format=None):

#         message_obj = Message.objects.get(id=id)
#         message_serializer = MessageViewSerializer(
#                 message_obj
#         )

#         return Response(message_serializer.data)
