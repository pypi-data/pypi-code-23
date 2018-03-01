# The goal of these subclasses is to make it easier to create the linking
# tables required for microservers to work
#
# each microservice is expected to have 1 linking table back to the main "profile_id"
# the following subclasses makes it easier to use
 


from profile_ms_base_manager import ProfileMSBaseManager

from profile_ms_base_models import ProfileMSBaseModel

from profile_ms_base_serializer import ProfileMSBaseSerializer