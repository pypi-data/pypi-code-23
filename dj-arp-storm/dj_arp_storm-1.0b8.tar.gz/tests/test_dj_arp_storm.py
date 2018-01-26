#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_dj_arp_storm
----------------------------------

Tests for `dj_arp_storm` module.
"""

import unittest
import mock
import pygame
import os
from time import sleep
from dj_arp_storm.player import Player, suppress_stdout_stderr

channel_available = False


class MockChannel():

    notes = []

    @classmethod
    def queue(cls, note):
        cls.notes.append(note)


def mock_find_channel():
    global channel_available
    if channel_available:
        return MockChannel
    else:
        channel_available = True
        return None


class TestPlayer(unittest.TestCase):

    def setUp(self):
        global channel_available
        channel_available = False
        MockChannel.notes = []

    def tearDown(self):
        pass

    def test_mixer_init(self):
        """Creating a Player initializes the pygame mixer."""
        p = Player('')
        self.assertIsNotNone(pygame.mixer.get_init())

    def test_load(self):
        """load loads sound objects from specified directory."""
        p = Player('tests/files/assets')
        p.load()
        self.assertTrue(set(['violin']) == set(p.sounds.keys()))
        self.assertTrue(set(p.sounds['violin'].keys()), set(['a.ogg', 'b.ogg']))
        v = [isinstance(n, pygame.mixer.Sound) for n in p.sounds['violin'].values()]
        self.assertTrue(all(v))

    @mock.patch('pygame.mixer.find_channel', side_effect=mock_find_channel)
    def test_play(self, find_channel):
        """play should loop to find a channel and queue the given sound in it."""
        global channel_available
        p = Player('')
        self.assertFalse(channel_available)
        self.assertFalse(MockChannel.notes)
        p.play('a note')
        self.assertEqual(find_channel.call_count, 2)
        self.assertTrue(channel_available)
        self.assertTrue('a note' in MockChannel.notes)

    @mock.patch('dj_arp_storm.player.Player.play', side_effect=mock.MagicMock())
    def test_delay_play(self, play):
        """play should not be called until delay has elapsed."""
        p = Player('')
        p.delay_play('note', delay=3)
        self.assertEqual(play.call_count, 0)
        sleep(4)
        self.assertEqual(play.call_count, 1)
        play.assert_called_with('note')

    @mock.patch('dj_arp_storm.player.Player.delay_play', side_effect=mock.MagicMock())
    def test_scale_play(self, delay_play):
        """delay_play should be called with notes in order, and the correct delay."""
        p = Player('tests/files/assets')
        p.load()
        p.scale(p.sounds['violin'], mod=2)
        sounds = list(p.sounds['violin'].values())
        self.assertEqual(mock.call(sounds[0], 2), delay_play.mock_calls[0])
        self.assertEqual(mock.call(sounds[1], 4), delay_play.mock_calls[1])


class Testsuppress_stdout_stderr(unittest.TestCase):

    def test_suppress_stdout_std_err(self):
        # import pdb;pdb.set_trace()
        stdout, stderr = os.fstat(1), os.fstat(2)
        orig_stdout_info = (stdout.st_mode, stdout.st_uid, stdout.st_gid)
        orig_stderr_info = (stderr.st_mode, stderr.st_uid, stderr.st_gid)
        with suppress_stdout_stderr():
            null_stdout, null_stderr = os.fstat(1), os.fstat(2)
            null_stdout_info = (null_stdout.st_mode, null_stdout.st_uid, null_stdout.st_gid)
            null_stderr_info = (null_stderr.st_mode, null_stderr.st_uid, null_stderr.st_gid)
            self.assertNotEqual(orig_stdout_info, null_stdout_info)
            self.assertNotEqual(orig_stderr_info, null_stderr_info)
        new_stdout, new_stderr = os.fstat(1), os.fstat(2)
        new_stdout_info = (new_stdout.st_mode, new_stdout.st_uid, new_stdout.st_gid)
        new_stderr_info = (new_stderr.st_mode, new_stderr.st_uid, new_stderr.st_gid)
        self.assertEqual(orig_stdout_info, new_stdout_info)
        self.assertEqual(orig_stderr_info, new_stderr_info)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
