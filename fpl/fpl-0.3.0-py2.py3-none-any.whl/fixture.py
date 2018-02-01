class Fixture(object):
    def __init__(self, fixture):
        self.team_h_score = fixture["team_h_score"]
        self.team_a_score = fixture["team_a_score"]
        self.kickoff_time = fixture["kickoff_time_formatted"]
        self.team_a = fixture["team_a"]
        self.team_h = fixture["team_h"]
        self.stats = fixture["stats"]
        self.gameweek = fixture["event"]

    def __str__(self):
        return "{} {}-{} {} - Gameweek {} - {}".format(self.team_h,
            self.team_h_score, self.team_a_score, self.team_a, self.gameweek,
            self.kickoff_time)