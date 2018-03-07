import unittest
import os
import random
import string
import time
import requests
import challonge


class PowerChallongeError(UserWarning):
    '''Raised in tests if output is not as expected'''
    pass


def generate_random_string():
    return "powerchallonge_tests_" + ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(30))


def genererate_random_list_of_random_strings():
    random_list = []
    for i in range(0, 10):
        random_list.append(generate_random_string())
    return random_list


def get_api_key():
    api_key = os.environ["CHALLONGE_API_KEY"]
    if not api_key:
        raise Warning(
            "environment variable CHALLONGE_API_KEY"
            " must be set to run the tests")
    return api_key


class SetUserSettngsTests(unittest.TestCase):

    def test_set_user_settings(self):
        api_key = get_api_key()
        challonge.set_user_settings(api_key)

    def test_set_user_settings_advanced(self):
        api_key = get_api_key()
        easy_tournament_identifier = False
        query_type = ".json"
        raw_response = False
        verbose_level = 0
        test_mode = True
        challonge.set_user_settings_advanced(api_key,
                                             easy_tournament_identifier,
                                             query_type, raw_response,
                                             verbose_level, test_mode)


class ParamsConvertersTests(unittest.TestCase):

    def setUp(self):
        xml_file = open('sample_tournament_template.xml', 'w')
        xml_content = ('<?xml version="1.0" encoding="UTF-8"?>'
                       '\n<tournament>\n    '
                       '<name>tournament1</name>\n    '
                       '<url>tournament1</url>\n</tournament>'
                       )

        xml_file.write(xml_content)
        xml_file.close()

        json_file = open('sample_tournament_template.json', 'w')
        json_content = ('{\n  "tournament": {\n    "name": "tournament1",'
                        '\n    '
                        '"url": "tournament1"\n  }\n}'
                        )

        json_file.write(json_content)
        json_file.close()

    def tearDown(self):
        os.remove('sample_tournament_template.xml')
        os.remove('sample_tournament_template.json')

    def test_xml_to_params(self):
        # Content of the xml file
        expected_params = {'name': 'tournament1', 'url': 'tournament1'}

        # Trying the conversion
        myparams = challonge.xml_to_params('sample_tournament_template.xml')
        self.assertEqual(expected_params, myparams)

    def test_json_to_params(self):
        # Content of the json file

        expected_params = {'name': 'tournament1', 'url': 'tournament1'}

        # Trying the conversion
        myparams = challonge.json_to_params('sample_tournament_template.json')
        self.assertEqual(expected_params, myparams)


class TournamentsTests(unittest.TestCase):
    '''
    A tournament is created then deleted for each
    Challonge API method tested below.
    The create and destroy are tested this way
    '''

    def setUp(self):
        api_key = get_api_key()
        challonge.set_user_settings(api_key)
        # Default starting time, current time UTC+30mins, checkin underway
        self.random_name = generate_random_string()
        self.random_url = self.random_name

        # Default starting time, UTC+30mins
        timestamp = time.time() + 1800
        utc_time = time.gmtime(timestamp)
        utc_time_date = time.strftime('%Y/%m/%d', utc_time)
        utc_time_time = time.strftime('%H:%M:%S', utc_time)
        utc_time_final = utc_time_date + "T" + utc_time_time + "+00:00"

        myparams = {'name': self.random_name,
                    'url': self.random_url, 'start_at': utc_time_final,
                    'check_in_duration': 60}
        challonge.tournaments.create(params=myparams)

        myparams = {}
        myparams['name'] = ['player1', 'player2']
        challonge.participants.bulk_add(self.random_url, params=myparams)

    def tearDown(self):
        challonge.tournaments.destroy(self.random_url)

    def test_index(self):
        r = challonge.tournaments.index()
        if isinstance(r, list) == False:
            raise PowerChallongeError('Invalid output, check the code')

    def test_tournaments_show(self):
        r = challonge.tournaments.show(self.random_url)
        if isinstance(r, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        self.assertEqual(self.random_name, r['name'])

    def test_tournaments_update(self):
        myparams = {'description': 'powerchallonge_tests_description'}
        r = challonge.tournaments.update(self.random_url, params=myparams)
        if isinstance(r, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')

        r2 = challonge.tournaments.show(self.random_url)
        self.assertEqual(myparams['description'], r2['description'])

    def test_tournaments_process_check_ins(self):
        challonge.tournaments.process_check_ins(self.random_url)
        r = challonge.tournaments.show(self.random_url)
        if r['state'] != 'checked_in':
            raise PowerChallongeError(
                'Operation did not succeed, check the code')
        if isinstance(r, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')

    def test_tournaments_abort_check_in(self):
        challonge.tournaments.process_check_ins(self.random_url)
        challonge.tournaments.abort_check_in(self.random_url)
        r = challonge.tournaments.show(self.random_url)
        if r['state'] != 'pending':
            raise PowerChallongeError(
                'Operation did not succeed, check the code')
        if isinstance(r, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')

    def test_tournaments_start(self):

        challonge.tournaments.process_check_ins(self.random_url)
        challonge.tournaments.start(self.random_url)
        r = challonge.tournaments.show(self.random_url)
        if r['state'] != 'underway':
            raise PowerChallongeError(
                'Operation did not succeed, check the code')
        if isinstance(r, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')

    def test_tournaments_finalize(self):
        challonge.tournaments.process_check_ins(self.random_url)
        challonge.tournaments.start(self.random_url)
        r0 = challonge.matches.index(self.random_url)
        for match in r0:
            myparams = {}
            myparams['scores_csv'] = "1-0"
            myparams['winner_id'] = match['player1_id']
            challonge.matches.update(self.random_url, match[
                                     'id'], params=myparams)

        r = challonge.tournaments.finalize(self.random_url)
        if r['state'] != 'complete':
            raise PowerChallongeError(
                'Operation did not succeed, check the code')
        if isinstance(r, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')

    def test_tournaments_reset(self):
        challonge.tournaments.process_check_ins(self.random_url)
        challonge.tournaments.start(self.random_url)
        r0 = challonge.matches.index(self.random_url)
        for match in r0:
            myparams = {}
            myparams['scores_csv'] = "1-0"
            myparams['winner_id'] = match['player1_id']
            challonge.matches.update(self.random_url, match[
                                     'id'], params=myparams)

        challonge.tournaments.finalize(self.random_url)
        r = challonge.tournaments.reset(self.random_url)
        if r['state'] != 'pending':
            raise PowerChallongeError(
                'Operation did not succeed, check the code')
        if isinstance(r, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')


class ParticipantsTests(unittest.TestCase):

    '''
    A tournament is created then deleted for each
    Challonge API method tested below.
    '''

    def setUp(self):
        api_key = get_api_key()
        challonge.set_user_settings(api_key)
        # Default tournament parameters
        self.random_name = generate_random_string()
        self.random_url = self.random_name
        self.random_p_name = generate_random_string()
        self.random_p_name2 = generate_random_string()
        self.random_p_names = [self.random_p_name, self.random_p_name2]
        self.random_list_of_str = genererate_random_list_of_random_strings()

        # Default starting time, UTC+30mins
        timestamp = time.time() + 1800
        utc_time = time.gmtime(timestamp)
        utc_time_date = time.strftime('%Y/%m/%d', utc_time)
        utc_time_time = time.strftime('%H:%M:%S', utc_time)
        utc_time_final = utc_time_date + "T" + utc_time_time + "+00:00"

        myparams = {'name': self.random_name,
                    'url': self.random_url, 'start_at': utc_time_final,
                    'check_in_duration': 60}
        challonge.tournaments.create(params=myparams)

    def tearDown(self):
        challonge.tournaments.destroy(self.random_url)

    def test_participants_index(self):
        r = challonge.participants.index(self.random_url)
        if isinstance(r, list) == False:
            raise PowerChallongeError('Invalid output, check the code')

    def test_participants_create(self):
        myparams = {'name': self.random_p_name}
        r = challonge.participants.create(self.random_url, params=myparams)
        participant_id = r['id']
        r2 = challonge.participants.show(self.random_url, participant_id)

        if isinstance(r, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')

        self.assertEqual(self.random_p_name, r2['name'])

    def test_participants_bulk_add(self):
        myparams = {'name': self.random_p_names}
        r = challonge.participants.bulk_add(self.random_url, params=myparams)
        r2 = challonge.participants.index(self.random_url)
        if isinstance(r, list) == False:
            raise PowerChallongeError('Invalid output, check the code')
        if len(r2) != 2:
            raise PowerChallongeError(
                'Operation did not succeed, check the code')

    def test_participants_show(self):
        myparams = {'name': self.random_p_name}
        challonge.participants.create(self.random_url, params=myparams)
        r = challonge.participants.index(self.random_url)
        participant_id = r[0]['id']
        r2 = challonge.participants.show(self.random_url, participant_id)
        if isinstance(r2, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        self.assertEqual(self.random_p_name, r2['name'])

    def test_participants_update(self):
        myparams = {'name': self.random_p_name}
        challonge.participants.create(self.random_url, params=myparams)
        r = challonge.participants.index(self.random_url)
        participant_id = r[0]['id']
        original_name = r[0]['name']
        new_p_name = self.random_p_name + "_new"
        myparams = {'name': new_p_name}
        r2 = challonge.participants.update(
            self.random_url, participant_id, params=myparams)
        if isinstance(r2, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        r3 = challonge.participants.show(self.random_url, participant_id)
        self.assertEqual(new_p_name, r3['name'])

    ''' Untested due to known issue, check readme
    def test_participants_check_in(self):
        myparams = {'name': self.random_p_name}
        r = challonge.participants.create(self.random_url, params=myparams)
        participant_id = r['id']
        # The participant is auto checked in when created because checkin is
        # underway

        if r['checked_in'] == True:
            r0 = challonge.participants.undo_check_in(
                self.random_url, participant_id)
            r0_2 = challonge.participants.show(self.random_url, participant_id)

        r2 = challonge.participants.check_in(self.random_url, participant_id)
        if isinstance(r2, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        r3 = challonge.participants.show(self.random_url, participant_id)
        not_checked_in = False
        self.assertNotEqual(r3['checked_in'], not_checked_in)
    '''

    def test_participants_undo_check_in(self):
        # Check explanation in previous function
        myparams = {'name': self.random_p_name}
        r = challonge.participants.create(self.random_url, params=myparams)
        participant_id = r['id']
        r2 = challonge.participants.undo_check_in(
            self.random_url, participant_id)
        if isinstance(r2, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        r3 = challonge.participants.show(self.random_url, participant_id)
        checked_in = True
        self.assertNotEqual(r3['checked_in'], checked_in)

    def test_participants_destroy(self):
        myparams = {'name': self.random_p_name}
        challonge.participants.create(self.random_url, params=myparams)
        r = challonge.participants.index(self.random_url)
        if len(r) == 1:
            participant_id = r[0]['id']
            r2 = challonge.participants.destroy(
                self.random_url, participant_id)
            if isinstance(r2, dict) == False:
                raise PowerChallongeError('Invalid output, check the code')
            r3 = challonge.participants.index(self.random_url)
            if len(r3) != 0:
                raise PowerChallongeError(
                    'Operation did not succeed, check the code')

        else:
            raise PowerChallongeError(
                'more than 1 participant in index output, check code')

    def test_participants_randomize(self):
        myparams = {'name': self.random_list_of_str}
        challonge.participants.bulk_add(self.random_url, params=myparams)
        r = challonge.participants.index(self.random_url)
        seed_list = []
        for participant in r:
            seed_list.append(
                str(participant['seed']) + ":" + participant['name'])
        r2 = challonge.participants.randomize(self.random_url)
        if isinstance(r2, list) == False:
            raise PowerChallongeError('Invalid output, check the code')
        r3 = challonge.participants.index(self.random_url)
        seed_list2 = []
        for participant in r3:
            seed_list2.append(
                str(participant['seed']) + ":" + participant['name'])
        self.assertNotEqual(seed_list, seed_list2)


class MatchesTests(unittest.TestCase):

    '''
    A tournament is created then deleted for each
    Challonge API method tested below.
    '''

    def setUp(self):
        api_key = get_api_key()
        challonge.set_user_settings(api_key)
        # Default tournament parameters
        self.random_name = generate_random_string()
        self.random_url = self.random_name
        self.random_p_name = generate_random_string()
        self.random_p_name2 = generate_random_string()
        self.random_p_names = [self.random_p_name, self.random_p_name2]
        self.random_list_of_str = genererate_random_list_of_random_strings()

        # Default starting time, UTC+30mins
        timestamp = time.time() + 1800
        utc_time = time.gmtime(timestamp)
        utc_time_date = time.strftime('%Y/%m/%d', utc_time)
        utc_time_time = time.strftime('%H:%M:%S', utc_time)
        utc_time_final = utc_time_date + "T" + utc_time_time + "+00:00"

        myparams = {'name': self.random_name,
                    'url': self.random_url, 'start_at': utc_time_final,
                    'check_in_duration': 60}
        challonge.tournaments.create(params=myparams)
        myparams = {'name': self.random_list_of_str}
        challonge.participants.bulk_add(self.random_url, params=myparams)
        challonge.tournaments.process_check_ins(self.random_url)
        challonge.tournaments.start(self.random_url)

    def tearDown(self):
        challonge.tournaments.destroy(self.random_url)

    def test_matches_index(self):
        r = challonge.matches.index(self.random_url)
        if isinstance(r, list) == False:
            raise PowerChallongeError('Invalid output, check the code')

    def test_matches_show(self):
        r = challonge.matches.index(self.random_url)
        match_id = r[0]['id']
        players_ids_original = [r[0]['player1_id'], r[0]['player2_id']]

        r2 = challonge.matches.show(self.random_url, match_id)
        if isinstance(r2, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        players_ids_new = [r2['player1_id'], r2['player2_id']]
        self.assertEqual(players_ids_original, players_ids_new)

    def test_matches_update(self):
        r = challonge.matches.index(self.random_url)
        match_id = r[0]['id']
        state_original = r[0]['state']
        myparams = {}
        myparams['scores_csv'] = "1-0"
        myparams['winner_id'] = r[0]['player1_id']
        r2 = challonge.matches.update(
            self.random_url, match_id, params=myparams)
        if isinstance(r2, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        state_new = r2['state']
        self.assertNotEqual(state_original, state_new)

    def test_matches_reopen(self):
        r = challonge.matches.index(self.random_url)
        match_id = r[0]['id']
        state_original = r[0]['state']
        myparams = {}
        myparams['scores_csv'] = "1-0"
        myparams['winner_id'] = r[0]['player1_id']
        r2 = challonge.matches.update(
            self.random_url, match_id, params=myparams)
        state_new = r2['state']
        if state_new != state_original:
            r3 = challonge.matches.reopen(self.random_url, match_id)
            if isinstance(r3, dict) == False:
                raise PowerChallongeError('Invalid output, check the code')
            state_new2 = r3['state']
            self.assertNotEqual(state_new, state_new2)
        else:
            raise PowerChallongeError(
                "match sate wasn't changed before trying to reopen it, "
                "check previous code")


class MatchAttachmentsTests(unittest.TestCase):

    def setUp(self):
        api_key = get_api_key()
        challonge.set_user_settings(api_key)
        # Default tournament parameters
        self.random_name = generate_random_string()
        self.random_url = self.random_name
        self.random_p_name = generate_random_string()
        self.random_p_name2 = generate_random_string()
        self.random_p_names = [self.random_p_name, self.random_p_name2]
        self.random_list_of_str = genererate_random_list_of_random_strings()

        # Default starting time, UTC+30mins
        timestamp = time.time() + 1800
        utc_time = time.gmtime(timestamp)
        utc_time_date = time.strftime('%Y/%m/%d', utc_time)
        utc_time_time = time.strftime('%H:%M:%S', utc_time)
        utc_time_final = utc_time_date + "T" + utc_time_time + "+00:00"

        myparams = {'name': self.random_name,
                    'url': self.random_url, 'start_at': utc_time_final,
                    'check_in_duration': 60, 'accept_attachments': "true"}
        challonge.tournaments.create(params=myparams)
        myparams = {'name': self.random_list_of_str}
        challonge.participants.bulk_add(self.random_url, params=myparams)
        challonge.tournaments.process_check_ins(self.random_url)
        challonge.tournaments.start(self.random_url)

        # Generating asset file
        file = open('asset1.txt', 'w')
        file.write('scoreboard, gg wp')
        file.close()

    def tearDown(self):
        challonge.tournaments.destroy(self.random_url)
        os.remove('asset1.txt')

    def test_matchattachments_index(self):
        r = challonge.matches.index(self.random_url)
        match_id = r[0]['id']
        r2 = challonge.match_attachments.index(self.random_url, match_id)
        if isinstance(r2, list) == False:
            raise PowerChallongeError('Invalid output, check the code')

    def test_matchattachments_create_non_asset(self):
        # Test will be performed using url
        r = challonge.matches.index(self.random_url)
        match_id = r[0]['id']
        myparams = {'url': 'http://github.com', 'description': 'github'}
        r2 = challonge.match_attachments.create(
            self.random_url, match_id, params=myparams)
        if isinstance(r2, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        r3 = challonge.match_attachments.index(self.random_url, match_id)
        myparams_new = {'url': r3[0]['url'],
                        'description': r3[0]['description']}
        self.assertEqual(myparams, myparams_new)

    '''Untested due to known issue, check readme
    def test_matchattachments_create_asset(self):
        # Currently not working (Error 500 from Challonge API)
        r = challonge.matches.index(self.random_url)
        match_id = r[0]['id']
        myparams = {'asset': ('asset1.txt',
                              open('asset1.txt', 'rb'))}
        myparams_simple = {'asset_file_name': 'asset1.txt'}
        r2 = challonge.match_attachments.create(
            self.random_url, match_id, params=myparams)
        if isinstance(r2, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        r3 = challonge.match_attachments.index(self.random_url, match_id)
        myparams_new = {'asset_file_name': [r3]['asset_file_name']}
        print(myparams_simple)
        print(myparams_new)
        self.assertEqual(myparams_simple, myparams_new)
    '''

    def test_matchattachments_show(self):
        r = challonge.matches.index(self.random_url)
        match_id = r[0]['id']
        myparams = {'url': 'http://github.com', 'description': 'github'}
        r2 = challonge.match_attachments.create(
            self.random_url, match_id, params=myparams)
        attachment_id = r2['id']

        r3 = challonge.match_attachments.show(
            self.random_url, match_id, attachment_id)
        if isinstance(r3, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        myparams_new = {'url': r3['url'], 'description': r3['description']}
        self.assertEqual(myparams, myparams_new)

    ''' Untested due to known issue, check readme
    def test_matchattachments_update_non_asset(self):
        # The fields don't get updated but the attachment content is updated
        # properly on the website, this test check will fail so the last line
        # is commentend until the issue is fixed

        r = challonge.matches.index(self.random_url)
        match_id = r[0]['id']
        myparams = {'url': 'http://github.com'}
        r2 = challonge.match_attachments.create(
            self.random_url, match_id, params=myparams)
        attachment_id = r2['id']
        r3 = challonge.match_attachments.show(
            self.random_url, match_id, attachment_id)

        # Checking that the attachment just created is as expected
        myparams_new = {'url': r3['url']}
        self.assertEqual(myparams, myparams_new)

        myparams_new2 = {'url': 'http://google.com'}

        r4 = challonge.match_attachments.update(
            self.random_url, match_id, attachment_id, params=myparams_new2)
        # print(r4)
        if isinstance(r4, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        r5 = challonge.match_attachments.show(
            self.random_url, match_id, attachment_id)

        self.assertEqual(myparams_new2['url'], r5['url'])
    '''

    '''Untested due to known issue, check readme
    def test_matchattachments_update_asset(self):
        # The fields don't get updated but the attachment content is updated
        # properly on the website
        r = challonge.matches.index(self.random_url)
        match_id = r[0]['id']
        myparams = {'description': 'test_description'}
        r2 = challonge.match_attachments.create(
            self.random_url, match_id, params=myparams)
        attachment_id = r2['id']
        r3 = challonge.match_attachments.show(
            self.random_url, match_id, attachment_id)
    # Checking that the attachment just created is as expected
        myparams_new = {'url': r3['url']}
        self.assertEqual(myparams, myparams_new)
        myparams_new2 = {'asset': ('asset1.txt',
                              open('asset1.txt', 'rb'))}
        myparams_simple = {'asset_file_name': 'asset1.txt'}
        r4 = challonge.match_attachments.update(
            self.random_url, match_id, attachment_id, params=myparams_new2)
        # print(r4)
        if isinstance(r4, dict) == False:
            raise PowerChallongeError('Invalid output, check the code')
        r5 = challonge.match_attachments.show(
            self.random_url, match_id, attachment_id)
        myparams_new = {'asset_file_name': [r3]['asset_file_name']}
        self.assertEqual(myparams_simple, myparams_new2)
    '''

    def test_matchattachments_destroy(self):
        r = challonge.matches.index(self.random_url)
        match_id = r[0]['id']
        myparams = {'url': 'http://github.com'}
        r2 = challonge.match_attachments.create(
            self.random_url, match_id, params=myparams)
        attachment_id = r2['id']
        r3 = challonge.match_attachments.index(
            self.random_url, match_id)
        if len(r3) != 1:
            raise PowerChallongeError(
                "Attachment creation failed before trying to destroy it,"
                "check previous code")
            attachment_id = r3[0]['id']
        elif len(r3) == 1:
            r4 = challonge.match_attachments.destroy(
                self.random_url, match_id, attachment_id)
            if isinstance(r4, dict) == False:
                raise PowerChallongeError('Invalid output, check the code')
        r5 = challonge.match_attachments.index(
            self.random_url, match_id)
        if len(r5) != 0:
            raise PowerChallongeError('Invalid output, check the code')


if __name__ == "__main__":
    unittest.main()
