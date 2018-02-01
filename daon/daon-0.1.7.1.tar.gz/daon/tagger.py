#! /usr/bin/python
# -*- coding: utf-8 -*-

from . import jvm


class Tagger:

  def parse(self, result):
    result = result.split()

    results = [tuple(m.rsplit('/',1)) for m in result]

    return results

  def pos(self, sentence, includeBit=-1, excludeBit=-1):
    """POS tagger.
    :param include: long, include bit.
    :param exclude: long, exclude bit.
    """

    result = self.daon.morphemes(sentence, includeBit, excludeBit)

    morphemes = self.parse(result)

    return morphemes

  def morphs(self, sentence):
    """Parse phrase to morphemes."""

    return [s for s, t in self.pos(sentence)]

  def nouns(self, sentence, includeBit=None, excludeBit=-1):
    """Noun extractor."""

    if includeBit is None:
      includeBit = self.defaultNounBit

    return [s for s, t in self.pos(sentence, includeBit=includeBit, excludeBit=excludeBit)]

  def makeTagBit(self, tags):

    l = jvm.get_jvm().java.util.ArrayList()

    for tag in tags:
      l.append(tag)

    return jvm.get_jvm().daon.core.util.Utils.makeTagBit(l)

  def __init__(self, model_path=None, url=None, timeout=30000):
    jvm.init_jvm()

    self.daon = jvm.get_jvm().daon.core.Daon()

    self.defaultNounBit = self.makeTagBit(['N','SL','SH'])

    if model_path:
      model = jvm.get_jvm().daon.core.util.ModelUtils.loadModelByFile(model_path)
      if model.isSuccess():
        jvm.get_jvm().daon.core.util.ModelUtils.setModel(model)
      else:
        print(model.getErrorMsg())
    elif url:
      model = jvm.get_jvm().daon.core.util.ModelUtils.loadModelByURL(url, timeout)
      if model.isSuccess():
        jvm.get_jvm().daon.core.util.ModelUtils.setModel(model)
      else:
        print(model.getErrorMsg())