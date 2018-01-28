from .enums import TeamUpWith, TeamupSearch, QueryParam
from .exception import DaftInputException
from .request import Request
from .person import Person


class Teamup(object):

    def __init__(self):
        self.url = "http://www.daft.ie/searchteamup.daft?"
        self.team_up_with = TeamUpWith.ANY
        self.move_in_date = 0
        self.query_params = ""

    def set_team_up_with(self, team_up_with):
        """
        Who would you like to team up with?
        :param team_up_with:
        :return:
        """
        if not isinstance(team_up_with, TeamUpWith):
            raise DaftInputException("team_up_with should be an instance of TeamUpWith")
        self.query_params += str(TeamupSearch.TEAM_UP_WITH) + str(team_up_with)

    def set_county(self, county):
        """
        What county do you live in?
        :param county:
        :return:
        """
        self.query_params += str(TeamupSearch.COUNTY) + str(county) + str(TeamupSearch.AREA)

    def set_rent(self, rent):
        """
        How much rent would you be willing to pay each per month?
        :param rent:
        :return:
        """
        self.query_params += str(TeamupSearch.RENT) + str(rent)

    def set_move_in_date(self, move_in_date):
        """
        When would you be ready to start looking for a place?
        :param move_in_date:
        :return:
        """
        self.query_params += str(TeamupSearch.MOVE_IN_DATE) + str(move_in_date)

    def get_results(self):
        search_results = []
        self.url += self.query_params + str(QueryParam.FIND_TEAMUPS)
        request = Request()
        soup = request.get(self.url)
        results = soup.find_all('table', {'class': 'tenant_result'})
        [search_results.append(Person(result)) for result in results]
        return search_results
