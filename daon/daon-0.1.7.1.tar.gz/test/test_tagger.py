import unittest

from daon import Tagger


class TestTagger(unittest.TestCase):

  def setUp(self):
    self.tagger = Tagger()

  def test_parse(self):
    results = self.tagger.parse('한글/NNG 이/JKS 좋/VA 아/EC //SP')

    self.assertListEqual([('한글', 'NNG'), ('이', 'JKS'), ('좋', 'VA'), ('아', 'EC'), ('/', 'SP')], results)

  def test_pos(self):
    morphemes = self.tagger.pos('한글이 좋아/')

    self.assertListEqual([('한글', 'NNG'), ('이', 'JKS'), ('좋', 'VA'), ('아', 'EC'), ('/', 'SP')], morphemes)

  def test_morphs(self):
    morphemes = self.tagger.morphs('한글이 좋아/')

    self.assertListEqual(['한글', '이', '좋', '아', '/'], morphemes)

  def test_nouns(self):
    nouns = self.tagger.nouns('한글이 좋아/ as')

    self.assertListEqual(['한글', 'as'], nouns)

if __name__ == '__main__':
  unittest.main()