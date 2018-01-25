"""
hudai.resources.tweet
"""
from ..helpers.resource import Resource


class TweetResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/people/tweets')
        self.resource_name = 'Tweet'

    def list(self, person_id, min_importance=None, page=None):
        query_params = self._set_limit_offset({
            'person_id': person_id,
            'min_importance': min_importance,
            'page': page
        })

        return self.http_get('/', query_params=query_params)

    def create(self, person_id, twitter_tweet_id, twitter_created_at, text, importance_score=None):
        return self.http_post('/',
                              data={
                                  'twitter_tweet_id': twitter_tweet_id,
                                  'twitter_created_at': twitter_created_at,
                                  'person_id': person_id,
                                  'text': text,
                                  'importance_score': importance_score,
                              })

    def fetch(self, tweet_id):
        return self.http_get('/{id}', params={'id': tweet_id})

    def fetch_by_twitter_id(self, twitter_tweet_id):
        return self.http_get('/by-twitter-id/{id}', params={'id': twitter_tweet_id})

    def delete(self, tweet_id):
        return self.http_delete('/{id}', params={'id': tweet_id})
