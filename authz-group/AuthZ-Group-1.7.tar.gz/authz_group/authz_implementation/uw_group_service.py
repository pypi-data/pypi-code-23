# This class requires the UW-RestClients-GWS app, here mainly as an example
# package

from authz_group.models import Person, GWSCrowdOwner
from uw_gws import GWS


class UWGroupService():
    def is_member_of_group(self, user_name, group_source_id):
        gws = GWS()
        if gws.is_effective_member(group_source_id, user_name):
            return True
        return False

    def group_display_name(self, source_id):
        return source_id

    def group_membership_url(self, group_source_id):
        return "https://groups.uw.edu/group/%s/member" % group_source_id

    @staticmethod
    def get_groups_for_user(login_name):
        person = Person.objects.get(login_name=login_name)

        crowd_owners = GWSCrowdOwner.objects.filter(person_id=person.pk)

        crowds = []
        for owner in crowd_owners:
            crowds.append(owner.gws_crowd)

        return crowds

    @staticmethod
    def get_source_type():
        return 'Catalyst::Model::GroupSource::GWS'

    @staticmethod
    def get_css_source_type():
        return 'Catalyst--Model--GroupSource--GWS'

    @staticmethod
    def json_data_structure():
        return {
            'source_type': UWGroupService.get_source_type(),
            'display_name': 'UW Groups',
            'css_source_type': UWGroupService.get_css_source_type(),
        }
