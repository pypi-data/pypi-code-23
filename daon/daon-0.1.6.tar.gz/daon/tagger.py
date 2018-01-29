#! /usr/bin/python
# -*- coding: utf-8 -*-

from . import jvm


class Tagger:
  def pos(self, sentence, include=[], exclude=[]):
    """POS tagger.
    :param include: [], include tags.
    :param exclude: [], exclude tags.
    """

    result = self.daon.morphemes(sentence, ','.join(include), ','.join(exclude))

    morphemes = [(result.get(k).getWord(), result.get(k).getTag()) for k in range(result.size())]

    return morphemes

  def morphs(self, sentence):
    """Parse phrase to morphemes."""

    return [s for s, t in self.pos(sentence)]

  def nouns(self, sentence, include=['N','SL','SH'], exclude=[]):
    """Noun extractor."""

    return [s for s, t in self.pos(sentence, include=include, exclude=exclude)]

  def __init__(self, model_path=None, url=None, timeout=30000):
    jvm.init_jvm()

    self.daon = jvm.get_jvm().daon.core.Daon()

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