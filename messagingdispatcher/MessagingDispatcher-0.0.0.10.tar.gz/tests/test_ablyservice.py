import base64, json, logging, mock, os, sys, unittest
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path + '/../') 
from messagingdispatcher.pubsub.ablyservice import AblyService


class TestAblyService(unittest.TestCase):
    """ Test Class for AblyService """

    def test_init_success(self):
        """ Test ensures proper api key format will instantiate an AblyRest Object """
        api_key = 'zEkI4A.ndGQtw:kDKYDEpWrryXn67W'
        ablyservice = AblyService(api_key)
        self.assertEqual(ablyservice._api_key, api_key)

    def test_publish_throw_exception(self):
        """ Test ensures publish throws an Ably Exception on invalid input """
        logging.disable(logging.ERROR)
        with self.assertRaises(Exception):
            ablyservice = AblyService('zEkI4A.ndGQtw:kDKYDEpWrryXn67W')
            ablyservice.publish('order.mocked', {1, 2, 3}, '300')

    @mock.patch('messagingdispatcher.pubsub.ablyservice.requests.post')
    def test_publish_success(self, requests_post):
        """ Test ensures that publish is triggered with correct argument """
        channel_name = 'cars'
        event = 'car.ordered'
        payload = '{"name": "Honda"}'
        authorization_value = base64.b64encode('123:123'.encode()).decode("utf-8")

        ablyservice = AblyService('123:123')
        ablyservice.publish(channel_name=channel_name, event=event, payload=payload)
        requests_post.assert_called_with('https://rest.ably.io/channels/{}/messages'.format(channel_name), 
                                          data=json.dumps({'name': event, 'data': payload}),
                                          headers={"content-type":"application/json", "Authorization":"Basic {}".format(authorization_value)})

if __name__ == '__main__':
    unittest.main()