from .base_model import (
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin,
        )

from .context import Context
from .team import Team
from .comment import Comment
from .wrappers import inside_lib

class Activity(
        BaseModel, GetAllMixin, GetSpecificMixin,
        DeleteMixin, NewMixin, UpdateMixin
        ):
    #TODO(kuba): activity_schedule_list endpoint
    #COMPLEX_FIELDS is filled after the class declaration
    COMPLEX_FIELDS = None
    TRANSLATE_BY_ID = (
            "context"
            )
    RO_FIELDS = (
            "children",
            "id",
            "participant",
            "executor_status",
            "supervisor_status",
            "team_status",
            "priority",
            "deleted",
            "comments",
            )
    W_FIELDS = (
            "custom_order",
            "context",
            "name",
            "description",
            "status",
            "type",
            "executor",
            "supervisor",
            "team",
            "schedule",
            "execution_deadline",
            "event_duration",
            "execution_breakable",
            "work_initial",
            "work_done",
            "work_left",
            )
    FIELDS = RO_FIELDS + W_FIELDS

    def __init__(self, id=None, client=None, dictionary=None):
        super().__init__(id, client, dictionary)


    def _default_call(self, data, endpoint, method='POST'):
        client = BaseModel.default_client if self._client is None else self._client
        client._call_singular(endpoint, method, json_body=data)


    def assignment_ask(self, assignment_list):
        endpoint = 'api/activity_assignment_ask/'
        data = {
                "activity_id": self.id,
                "assignee_list": assignment_list,
                }
        self._default_call(data, endpoint)


    def execution_ask(self, email):
        data = {
                "activity_id": self.id,
                "executor_email": email,
                }
        endpoint = 'api/activity_parent_change/'
        self._default_call(data, endpoint)


    def finish(self):
        data = {
                "activity_id": self.id,
                }
        endpoint = 'api/activity_finish/'
        self._default_call(data, endpoint)


    def order_change(self, custom_order):
        endpoint = '/api/activity_order_change/'
        data = {
                'activity_id' : self.id,
                'custom_order' : custom_order,
                }
        self._default_call(data, endpoint)


    def parent_change(self, id=None):
        #TODO(kuba): thinking if we should keep all objects in a list and
        # for example update parent object when someone calls parent_change to
        # that object
        endpoint = 'api/activity_parent_change/'
        client = BaseModel.default_client if self._client is None else self._client
        data = {'activity_id': self.id}
        if id is not None:
            data["new_parent_id"] = id

        self._default_call(data, endpoint)


    def participation_ask(self, participant_profile_list):
        endpoint = 'api/activity_participation_ask/'
        data = {
                'activity_id' : self.id,
                'participant_profile_list' : participant_profile_list,
                }
        self._default_call(data, endpoint)


    def progress_update(self, start_time, end_time):
        endpoint = 'api/activity_progress_update/'
        data = {
                'activity_id' : self.id,
                'start_time' : start_time,
                'end_time' : end_time,
                }
        self._default_call(data, endpoint)


    def respond_accept(self):
        endpoint = 'api/activity_respond_accept/'
        data = {
                'activity_id' : self.id,
                }
        self._default_call(data, endpoint)


    def respond_reject(self):
        endpoint = 'api/activity_respond_reject/'
        data = {
                'activity_id' : self.id,
                }
        self._default_call(data, endpoint)


    def schedule_add(self, priority, comment):
        endpoint = 'api/activity_schedule_add/'
        data = {
                'activity_id' : self.id,
                'priority' : priority,
                'comment' : comment,
                }
        self._default_call(data, endpoint)


    def schedule_remove(self, comment):
        endpoint = 'api/activity_schedule_remove/'
        data = {
                'activity_id' : self.id,
                'comment' : comment,
                }
        self._default_call(data, endpoint)


    def supervision_ask(self, supervisor_email):
        endpoint = 'api/activity_supervision_ask/'
        data = {
                'activity_id' : self.id,
                'supervisor_email' : supervisor_email,
                }
        self._default_call(data, endpoint)


    def team_ask(self, team_id):
        endpoint = 'api/activity_team_ask/'
        data = {
                'activity_id' : self.id,
                'team_id' : team_id,
                }
        self._default_call(data, endpoint)



#Hack to allow Activity to be value in dictionary
#when it was in class declaration Activity wasn't defined
Activity.COMPLEX_FIELDS = {
        "children" : [Activity],
        "context": Context,
        "team": Team,
        "comments": [Comment],
    }
