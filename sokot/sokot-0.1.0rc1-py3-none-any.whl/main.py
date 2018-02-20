import fire

from sokot.aggregator import SokotAggretator
from sokot.configuration import SokotConfiguration
from sokot.group import SokotGroup
from sokot.requester import SokotRequester


class Sokot():
    def __init__(self):
        self._config = SokotConfiguration()
        self._requester = SokotRequester()
        self._aggregator = SokotAggretator()
        self.group = SokotGroup()

    def configure(self):
        self._config.create()
        return 'OK'

    def available(self):
        token = self._config.check()
        resp = self._requester.get('/tokens/{}/available'.format(token), token)
        return resp['available']

    def overtime(self, agg_type='sum'):
        """
        sum: チームの残業時間合計
        per_member: sum をメンバー数で割った時間
        """
        self._config.check()
        result = self._aggregator.aggregate(agg_type)
        print(result)


def main():
    fire.Fire(Sokot(), name='sokot')


if __name__ == '__main__':
    main()
