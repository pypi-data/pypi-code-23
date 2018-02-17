# from commons import error_conf


def check_for_private_message_error(request):
    """
    Error Handling For Private Message API
    """
    data = request.data

    if not data.get('room_id'):
        return "error_conf.ROOM_ID_NOT_PROVIDED"

    if not data.get("position_id"):
        return "error_conf.POSITION_ID_NOT_PROVIDED"

    return False


# def check_for_retrive_feeds_error(request):
#     """
#     Error Handling For Message Feeds API
#     """
#     data = request.data

#     if not data.get('latest_message_id'):
#         return error_conf.LATEST_MESSAGE_ID_NOT_PROVIDED

#     if not data.get('room_id'):
#         return error_conf.ROOM_ID_NOT_PROVIDED

#     return False


# def check_for_update_message_error(request):
#     """
#     Error Handling For Chat Message Update API
#     """
#     data = request.data

#     if not data.get('action'):
#         return error_conf.CHAT_ACTION_NOT_PROVIDED

#     if not data.get('message_id'):
#         return error_conf.MESSAGE_ID_NOT_PROVIDED

#     return False
