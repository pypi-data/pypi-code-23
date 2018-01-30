# coding=utf-8
import unittest
from mailchimp.objects import MCCampaignDefaults


class TestMCCampaignDefaults(unittest.TestCase):
    def get_campaign_defaults(self):
        return {
            'from_name': 'from_name_value',
            'from_email': 'from_email_value',
            'subject': 'subject_value',
            'language': 'language_value'
        }

    def test_item_url(self):
        campaign_defaults = MCCampaignDefaults()
        self.assertIsNone(campaign_defaults.item_url)

    def test_valid_search_params(self):
        campaign_defaults = MCCampaignDefaults()
        self.assertEqual(['offset', 'count', 'fields', 'exclude_fields'],
                         campaign_defaults.valid_search_params)

    def test_none_init(self):
        campaign_defaults = MCCampaignDefaults(None)

        for prop in ['from_name', 'from_email', 'subject', 'language']:
            self.assertIsNone(getattr(campaign_defaults, prop))

    def test_empty_init(self):
        campaign_defaults = MCCampaignDefaults()

        for prop in ['from_name', 'from_email', 'subject', 'language']:
            self.assertIsNone(getattr(campaign_defaults, prop))

    def test_init(self):
        campaign_defaults = MCCampaignDefaults(self.get_campaign_defaults())

        self.assertEqual('from_name_value', campaign_defaults.from_name)
        self.assertEqual('from_email_value', campaign_defaults.from_email)
        self.assertEqual('subject_value', campaign_defaults.subject)
        self.assertEqual('language_value', campaign_defaults.language)

    def test_to_str(self):
        campaign_defaults = MCCampaignDefaults(self.get_campaign_defaults())
        self.assertEqual('', str(campaign_defaults))

    def test_repr(self):
        campaign_defaults = MCCampaignDefaults(self.get_campaign_defaults())
        self.assertEqual('<MCCampaignDefaults: >', str(repr(campaign_defaults)))
