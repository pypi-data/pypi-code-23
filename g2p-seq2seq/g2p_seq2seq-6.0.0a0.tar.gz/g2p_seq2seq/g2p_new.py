# Copyright 2016 AC Technologies LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Binary for training translation models and decoding from them.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import operator
import tensorflow as tf
import numpy as np
import re

from g2p_seq2seq import g2p_trainer_utils
from tensor2tensor.utils import registry
from tensor2tensor.utils import trainer_utils
from tensor2tensor.utils import usr_dir
from tensor2tensor.utils import decoding

from tensor2tensor.data_generators import text_encoder

from IPython.core.debugger import Tracer
from six.moves import input
from six import text_type

from tensorflow.python.estimator import estimator as estimator_lib

EOS = text_encoder.EOS


class G2PModel(object):
  """Grapheme-to-Phoneme translation model class.
  """
  def __init__(self, params, file_path="", is_training=False):
    # Point out the current directory with t2t problem specified for g2p task.
    usr_dir.import_usr_dir(os.path.dirname(os.path.abspath(__file__)))
    self.params = params
    self.file_path = file_path
    # Register g2p problem.
    self.problem = registry._PROBLEMS[self.params.problem_name](
        self.params.model_dir, file_path=file_path, is_training=is_training)
    trainer_utils.log_registry()
    if not os.path.exists(self.params.model_dir):
      os.makedirs(self.params.model_dir)
    self.train_preprocess_file_path, self.dev_preprocess_file_path = None, None
    self.estimator, self.decode_hp = self.__prepare_decode_model()
    self.word_processed = tf.get_variable("word_processed", dtype=tf.bool, initializer=tf.constant(True))
    self.inputs = [tf.get_variable("inputs", [100], dtype=tf.int32)]
    #self.problem_choice = tf.get_variable("problem_choice", [1], dtype=tf.int32)
    ##inp =  {"inputs": np.array(x).astype(np.int32),
    ##        "problem_choice": np.array(problem_id).astype(np.int32)}
    self.inputs_placeholder = tf.placeholder(tf.int32, [None], name="inputs_placeholder")
    ##self.outputs_placeholder = tf.placeholder(tf.int32, [None], name="outputs_placeholder")

  def prepare_datafiles(self, train_path, dev_path):
    """Prepare preprocessed datafiles."""
    self.train_preprocess_file_path, self.dev_preprocess_file_path =\
        self.problem.generate_preprocess_data(train_path, dev_path)

  def train(self):
    """Run training."""
    g2p_trainer_utils.run(
        params=self.params,
        problem_instance=self.problem,
        train_preprocess_file_path=self.train_preprocess_file_path,
        dev_preprocess_file_path=self.dev_preprocess_file_path)

  def __prepare_decode_model(self):
    """Prepare utilities for decoding."""
    Tracer()()
    hparams = trainer_utils.create_hparams(
        self.params.hparams_set,
        self.params.data_dir,
        passed_hparams=self.params.hparams)
    estimator, _ = g2p_trainer_utils.create_experiment_components(
        params=self.params,
        hparams=hparams,
        run_config=trainer_utils.create_run_config(self.params.model_dir),
        problem_instance=self.problem)

    decode_hp = decoding.decode_hparams(self.params.decode_hparams)
    decode_hp.add_hparam("shards", 1)
    return estimator, decode_hp

  def __prepare_interactive_model(self, g,
              features,#input_fn,
              #esti,
              model_dir,
              predict_keys=None,
              hooks=None,
              checkpoint_path=None):
    """Yields predictions for given features.

    Args:
      input_fn: Input function returning features which is a dictionary of
        string feature name to `Tensor` or `SparseTensor`. If it returns a
        tuple, first item is extracted as features. Prediction continues until
        `input_fn` raises an end-of-input exception (`OutOfRangeError` or
        `StopIteration`).
      predict_keys: list of `str`, name of the keys to predict. It is used if
        the `EstimatorSpec.predictions` is a `dict`. If `predict_keys` is used
        then rest of the predictions will be filtered from the dictionary. If
        `None`, returns all.
      hooks: List of `SessionRunHook` subclass instances. Used for callbacks
        inside the prediction call.
      checkpoint_path: Path of a specific checkpoint to predict. If `None`, the
        latest checkpoint in `model_dir` is used.

    Yields:
      Evaluated values of `predictions` tensors.

    Raises:
      ValueError: Could not find a trained model in model_dir.
      ValueError: if batch length of predictions are not same.
      ValueError: If there is a conflict between `predict_keys` and
        `predictions`. For example if `predict_keys` is not `None` but
        `EstimatorSpec.predictions` is not a `dict`.
    """
    hooks = estimator_lib._check_hooks_type(hooks)
    # Check that model has been trained.
    if not checkpoint_path:
      checkpoint_path = estimator_lib.saver.latest_checkpoint(model_dir)
    if not checkpoint_path:
      raise ValueError('Could not find trained model in model_dir: {}.'.format(
          model_dir))

    #with estimator_lib.ops.Graph().as_default() as g:
    #g = estimator_lib.ops.Graph().as_default()
    estimator_lib.random_seed.set_random_seed(self.estimator._config.tf_random_seed)
    self.estimator._create_and_assert_global_step(g)
    Tracer()()
      #features = self.estimator._get_features_from_input_fn(
      #    input_fn, estimator_lib.model_fn_lib.ModeKeys.PREDICT)
    self.estimator_spec = self.estimator._call_model_fn(
        features, None, estimator_lib.model_fn_lib.ModeKeys.PREDICT,
        self.estimator.config)
    self.predict_keys = predict_keys
      #predictions = self.estimator._extract_keys(estimator_spec.predictions, predict_keys)

      #with tf.Session(graph=g) as sess:
      #  preds_evaluated = sess.run(predictions)
      #with estimator_lib.training.MonitoredSession(
      #    session_creator=estimator_lib.training.ChiefSessionCreator(
      #        checkpoint_filename_with_path=checkpoint_path,
      #        scaffold=estimator_spec.scaffold,
      #        config=esti._session_config),
      #    hooks=hooks) as mon_sess:
    mon_sess = estimator_lib.training.MonitoredSession(
        session_creator=estimator_lib.training.ChiefSessionCreator(
            checkpoint_filename_with_path=checkpoint_path,
            scaffold=self.estimator_spec.scaffold,
            config=self.estimator._session_config),
        hooks=hooks)
    return mon_sess#, predictions
        #while not mon_sess.should_stop():
        #  preds_evaluated = mon_sess.run(predictions)
        #  Tracer()()
        #  if not isinstance(predictions, dict):
        #    for pred in preds_evaluated:
        #      yield pred
        #  else:
        #    for i in range(esti._extract_batch_length(preds_evaluated)):
        #      yield {
        #          key: value[i]
        #          for key, value in estimator_lib.six.iteritems(preds_evaluated)
        #      }



  def decode_word(self, mon_sess, predictions, x, problem_id):#input_string):
    """Decode word.

    Args:
      word: a word for decoding.

    Returns:
      pronunciation: a decoded phonemes sequence for input word.
    """
    transmit_word_op = tf.py_func(transmit_word_fn, [self.inputs_placeholder], tf.int32)##Tout=self.outputs_placeholder)#, Tout=)
    ##self.transmit_word_fn(inputs=np.array(x).astype(np.int32))#,
    #      #problem_choice=np.array(problem_id).astype(np.int32))#,
    #      #mon_sess=mon_sess)
    ##res = mon_sess.run(transmit_word_op, feed_dict={self.inputs_placeholder:self.inputs})
    mon_sess.run(transmit_word_op, feed_dict={self.inputs_placeholder:self.inputs})
    preds_evaluated = mon_sess.run(predictions)
    Tracer()()
    result = None
    if not isinstance(predictions, dict):
      for pred in preds_evaluated:
        result = pred
    else:
      for i in range(self.estimator._extract_batch_length(preds_evaluated)):
        result = {
               key: value[i]
               for key, value in estimator_lib.six.iteritems(preds_evaluated)
              }

    if self.decode_hp.return_beams:
      beams = np.split(result["outputs"], self.decode_hp.beam_size, axis=0)
      scores = None
      if "scores" in result:
        scores = np.split(result["scores"], decode_hp.beam_size, axis=0)
      for k, beam in enumerate(beams):
        tf.logging.info("BEAM %d:" % k)
        beam_string = self.problem.target_vocab.decode(
            decoding._save_until_eos(beam, is_image=False))
        if scores is not None:
          tf.logging.info("%s\tScore:%f" % (beam_string, scores[k]))
        else:
          tf.logging.info(beam_string)
    else:
      if self.decode_hp.identity_output:
        tf.logging.info(" ".join(map(str, result["outputs"].flatten())))
      else:
          #tf.logging.info(
          #    self.problem.target_vocab.decode(
          #        decoding._save_until_eos(result["outputs"], is_image=False)))
          #        #decoding._save_until_eos(result, is_image=False)))
        res = result["outputs"]#result["outputs"]
        res = res.flatten()
        index = list(res).index(text_encoder.EOS_ID)
        res = res[0:index]
        pronunciation = self.problem.target_vocab.decode(res)
    #return pronunciation
    yield pronunciation

  #def transmit_word_fn(self, x):#problem_choice):#, mon_sess):
  #  Tracer()()
  #  if self.word_processed:
  #    self.inputs = [x]
  #    #self.outputs = [x]
  #    #self.problem_choice = problem_choice
  #    #mon_sess.run(feed_dict={self.inputs_placeholder:self.inputs})
  #    self.word_processed = False
  #  #return x

  #def get_word_fn(self):
  #  if not self.word_processed:
  #    self.word_processed = True
  #    #return {"inputs":self.inputs, "problem_choice":self.problem_choice}
  #    self.mon_sess.run(feed_dict={"inputs":self.inputs, "problem_choice":self.problem_choice})
  #    return {"inputs":self.inputs, "problem_choice":self.problem_choice}

  def get_word_fn(self, x):
    inp = np.array(x).astype(np.int32)
    #self.mon_sess.run(feed_dict={"inputs":inp, "problem_choice":self.problem_choice})
    return {"inputs":inp}#, "problem_choice":self.problem_choice}

  def interactive(self):
    """Interactive decoding."""

    #while True:
    if True:
      try:
        Tracer()()
        word = input("> ")
        if not issubclass(type(word), text_type):
          word = text_type(word, encoding="utf-8", errors="replace")
      except EOFError:
        pass#break
      if not word:
        pass#break

      num_samples = 1
      decode_length = 100
      input_type = "text"
      problem_id = 0
      p_hparams = self.estimator.params.problems[problem_id]
      has_input = "inputs" in p_hparams.input_modality
      vocabulary = p_hparams.vocabulary["inputs" if has_input else "targets"]
      # This should be longer than the longest input.
      const_array_size = 10000
      #self.inputs_placeholder = tf.placeholder(tf.int32, [None], name="inputs_placeholder")
      #self.outputs_placeholder = tf.placeholder(tf.int32, [None], name="outputs_placeholder")


      input_ids = vocabulary.encode(word)
      if has_input:
        input_ids.append(text_encoder.EOS_ID)
      x = [num_samples, decode_length, len(input_ids)] + input_ids
      assert len(x) < const_array_size
      x += [0] * (const_array_size - len(x))
      ##inp =  {"inputs": np.array(x).astype(np.int32),
      ##        "problem_choice": np.array(problem_id).astype(np.int32)}
      Tracer()()
      transmit_word_op = tf.py_func(transmit_word_fn, [self.inputs_placeholder], tf.int32)#self.outputs_placeholder)
      sess = tf.Session()
      ##self.transmit_word_fn(inputs= np.array(x).astype(np.int32),
      ##    problem_choice=np.array(problem_id).astype(np.int32))#,
      #    #mon_sess=sess)
      Tracer()
      self.inputs = x
      #res = sess.run(transmit_word_op, feed_dict={self.inputs_placeholder:self.inputs})
      x_out = sess.run(transmit_word_op, feed_dict={self.inputs_placeholder:self.inputs})

      def input_fn():
        gen_fn = make_input_fn(self.get_word_fn(x_out))#inp)
        example = gen_fn()
        example = _interactive_input_tensor_to_features_dict(example,
            self.estimator.params)
        return example


    #while True:

      with estimator_lib.ops.Graph().as_default() as g:
        Tracer()()
        features = self.estimator._get_features_from_input_fn(
            input_fn, estimator_lib.model_fn_lib.ModeKeys.PREDICT)
        self.mon_sess = self.__prepare_interactive_model(g, features,
            model_dir=self.params.model_dir)
        predictions = self.estimator._extract_keys(self.estimator_spec.predictions, None)

    while True:

      pronunciation = self.decode_word(self.mon_sess, predictions, x, problem_id).next()
      print("Pronunciation: {}".format(pronunciation))

    #while True:
    #while not mon_sess.should_stop():
      try:
        Tracer()()
        word = input("> ")
        if not issubclass(type(word), text_type):
          word = text_type(word, encoding="utf-8", errors="replace")
      except EOFError:
        break
      if not word:
        break

      input_ids = vocabulary.encode(word)
      if has_input:
        input_ids.append(text_encoder.EOS_ID)
      x = [num_samples, decode_length, len(input_ids)] + input_ids
      assert len(x) < const_array_size
      x += [0] * (const_array_size - len(x))
      ##inp =  {"inputs": np.array(x).astype(np.int32),
      ##        "problem_choice": np.array(problem_id).astype(np.int32)}

      ##self.transmit_word_fn(inputs=np.array(x).astype(np.int32),
      ##      problem_choice=np.array(problem_id).astype(np.int32))

      ##pronunciation = self.decode_word(mon_sess, predictions, inp).next()
      ##print(pronunciation)

  def decode(self, output_file_path):
    """Run decoding mode."""
    #estimator, decode_hp = self.__prepare_decode_model()
    inputs, decodes = decode_from_file(
        self.estimator, self.file_path, self.decode_hp)
    # If path to the output file pointed out, dump decoding results to the file
    if output_file_path:
      tf.logging.info("Writing decodes into %s" % output_file_path)
      outfile = tf.gfile.Open(output_file_path, "w")
      if decode_hp.return_beams:
        for index in range(len(inputs)):
          outfile.write("%s%s" % ("\t".join(decodes[index]),
                                  decode_hp.delimiter))
      else:
        for index in range(len(inputs)):
          outfile.write("%s%s" % (decodes[index], decode_hp.delimiter))

  def evaluate(self):
    """Run evaluation mode."""
    words, pronunciations = [], []
    for case in self.problem.generator(self.file_path,
                                       self.problem.source_vocab,
                                       self.problem.target_vocab):
      word = self.problem.source_vocab.decode(case["inputs"]).replace(
          EOS, "").strip()
      pronunciation = self.problem.target_vocab.decode(case["targets"]).replace(
          EOS, "").strip()
      words.append(word)
      pronunciations.append(pronunciation)

    g2p_gt_map = create_g2p_gt_map(words, pronunciations)

    #estimator, decode_hp = self.__prepare_decode_model()
    correct, errors = calc_errors(g2p_gt_map, self.estimator, self.file_path,
                                  self.decode_hp)

    print("Words: %d" % (correct+errors))
    print("Errors: %d" % errors)
    print("WER: %.3f" % (float(errors)/(correct+errors)))
    print("Accuracy: %.3f" % float(1.-(float(errors)/(correct+errors))))
    return estimator, decode_hp, g2p_gt_map


def transmit_word_fn(x):
  Tracer()()
  #if self.word_processed:
  #  self.inputs = [x]
  #  self.word_processed = False
  return x


def predict(input_fn,
            esti,
            model_dir,
            predict_keys=None,
            hooks=None,
            checkpoint_path=None):
  """Yields predictions for given features.

  Args:
    input_fn: Input function returning features which is a dictionary of
      string feature name to `Tensor` or `SparseTensor`. If it returns a
      tuple, first item is extracted as features. Prediction continues until
      `input_fn` raises an end-of-input exception (`OutOfRangeError` or
      `StopIteration`).
    predict_keys: list of `str`, name of the keys to predict. It is used if
      the `EstimatorSpec.predictions` is a `dict`. If `predict_keys` is used
      then rest of the predictions will be filtered from the dictionary. If
      `None`, returns all.
    hooks: List of `SessionRunHook` subclass instances. Used for callbacks
      inside the prediction call.
    checkpoint_path: Path of a specific checkpoint to predict. If `None`, the
      latest checkpoint in `model_dir` is used.

  Yields:
    Evaluated values of `predictions` tensors.

  Raises:
    ValueError: Could not find a trained model in model_dir.
    ValueError: if batch length of predictions are not same.
    ValueError: If there is a conflict between `predict_keys` and
      `predictions`. For example if `predict_keys` is not `None` but
      `EstimatorSpec.predictions` is not a `dict`.
  """
  hooks = estimator_lib._check_hooks_type(hooks)
  # Check that model has been trained.
  if not checkpoint_path:
    checkpoint_path = estimator_lib.saver.latest_checkpoint(model_dir)
  if not checkpoint_path:
    raise ValueError('Could not find trained model in model_dir: {}.'.format(
        model_dir))

  with estimator_lib.ops.Graph().as_default() as g:
    estimator_lib.random_seed.set_random_seed(esti._config.tf_random_seed)
    esti._create_and_assert_global_step(g)
    features = esti._get_features_from_input_fn(
        input_fn, estimator_lib.model_fn_lib.ModeKeys.PREDICT)
    estimator_spec = esti._call_model_fn(
        features, None, estimator_lib.model_fn_lib.ModeKeys.PREDICT, esti.config)
    predictions = esti._extract_keys(estimator_spec.predictions, predict_keys)

    #with tf.Session(graph=g) as sess:
    #  preds_evaluated = sess.run(predictions)
    with estimator_lib.training.MonitoredSession(
        session_creator=estimator_lib.training.ChiefSessionCreator(
            checkpoint_filename_with_path=checkpoint_path,
            scaffold=estimator_spec.scaffold,
            config=esti._session_config),
        hooks=hooks) as mon_sess:
      while not mon_sess.should_stop():
        preds_evaluated = mon_sess.run(predictions)
        Tracer()()
        if not isinstance(predictions, dict):
          for pred in preds_evaluated:
            yield pred
        else:
          for i in range(esti._extract_batch_length(preds_evaluated)):
            yield {
                key: value[i]
                for key, value in estimator_lib.six.iteritems(preds_evaluated)
            }


def make_input_fn(inp):#get_word_fn):#gen):
  """Use py_func to yield elements from the given generator."""
  first_ex = inp#six.next(gen)
  #first_ex = get_word_fn()
  flattened = tf.contrib.framework.nest.flatten(first_ex)
  Tracer()()
  types = [t.dtype for t in flattened]
  shapes = [[None] * len(t.shape) for t in flattened]
  first_ex_list = [first_ex]

  def py_func():
    if first_ex_list:
      example = first_ex_list.pop()
    else:
      example = inp#six.next(gen)
      #example = get_word_fn()
    return tf.contrib.framework.nest.flatten(example)

  def input_fn():
    Tracer()()
    flat_example = tf.py_func(py_func, [], types)
    _ = [t.set_shape(shape) for t, shape in zip(flat_example, shapes)]
    example = tf.contrib.framework.nest.pack_sequence_as(first_ex, flat_example)
    return example

  return input_fn


def _interactive_input_tensor_to_features_dict(feature_map, hparams):
  """Convert the interactive input format (see above) to a dictionary.

  Args:
    feature_map: a dictionary with keys `problem_choice` and `input` containing
      Tensors.
    hparams: model hyperparameters

  Returns:
    a features dictionary, as expected by the decoder.
  """
  Tracer()()
  inputs = tf.convert_to_tensor(feature_map["inputs"])

  def input_fn(x=inputs):#problem_choice, x=inputs):  # pylint: disable=missing-docstring
    # Remove the batch dimension.
    num_samples = x[0]
    length = x[2]
    x = tf.slice(x, [3], tf.to_int32([length]))
    x = tf.reshape(x, [1, -1, 1, 1])
    # Transform into a batch of size num_samples to get that many random
    # decodes.
    x = tf.tile(x, tf.to_int32([num_samples, 1, 1, 1]))

    p_hparams = hparams.problems[1]#problem_choice]
    return (tf.constant(p_hparams.input_space_id), tf.constant(
        p_hparams.target_space_id), x)

  input_space_id, target_space_id, x = decoding.input_fn_builder.cond_on_index(
      input_fn,# feature_map["problem_choice"], len(hparams.problems) - 1)
      1, len(hparams.problems) - 1)

  features = {}
  features["problem_choice"] = tf.convert_to_tensor(
      [1])#feature_map["problem_choice"])
  features["input_space_id"] = input_space_id
  features["target_space_id"] = target_space_id
  features["decode_length"] = (inputs[1])
  features["inputs"] = x
  return features


def _interactive_input_fn(hparams, word):
  """Generator that reads from the terminal and yields "interactive inputs".

  Due to temporary limitations in tf.learn, if we don't want to reload the
  whole graph, then we are stuck encoding all of the input as one fixed-size
  numpy array.

  We yield int32 arrays with shape [const_array_size].  The format is:
  [num_samples, decode_length, len(input ids), <input ids>, <padding>]

  Args:
    hparams: model hparams
  Yields:
    numpy arrays

  Raises:
    Exception: when `input_type` is invalid.
  """
  Tracer()()
  num_samples = 1
  Tracer()()
  decode_length = 100
  input_type = "text"
  problem_id = 0
  p_hparams = hparams.problems[problem_id]
  has_input = "inputs" in p_hparams.input_modality
  vocabulary = p_hparams.vocabulary["inputs" if has_input else "targets"]
  # This should be longer than the longest input.
  const_array_size = 10000
  # Import readline if available for command line editing and recall.
  try:
    import readline  # pylint: disable=g-import-not-at-top,unused-variable
  except ImportError:
    pass
  while True:
    prompt = ("INTERACTIVE MODE  num_samples=%d  decode_length=%d  \n"
              "  it=<input_type>     ('text' or 'image' or 'label', default: "
              "text)\n"
              "  pr=<problem_num>    (set the problem number, default: 0)\n"
              "  in=<input_problem>  (set the input problem number)\n"
              "  ou=<output_problem> (set the output problem number)\n"
              "  ns=<num_samples>    (changes number of samples, default: 1)\n"
              "  dl=<decode_length>  (changes decode length, default: 100)\n"
              "  <%s>                (decode)\n"
              "  q                   (quit)\n"
              ">" % (num_samples, decode_length, "source_string"
                     if has_input else "target_prefix"))
    input_string = word#input(prompt)
    if input_string == "q":
      return
    elif input_string[:3] == "pr=":
      problem_id = int(input_string[3:])
      p_hparams = hparams.problems[problem_id]
      has_input = "inputs" in p_hparams.input_modality
      vocabulary = p_hparams.vocabulary["inputs" if has_input else "targets"]
    elif input_string[:3] == "in=":
      problem = int(input_string[3:])
      p_hparams.input_modality = hparams.problems[problem].input_modality
      p_hparams.input_space_id = hparams.problems[problem].input_space_id
    elif input_string[:3] == "ou=":
      problem = int(input_string[3:])
      p_hparams.target_modality = hparams.problems[problem].target_modality
      p_hparams.target_space_id = hparams.problems[problem].target_space_id
    elif input_string[:3] == "ns=":
      num_samples = int(input_string[3:])
    elif input_string[:3] == "dl=":
      decode_length = int(input_string[3:])
    elif input_string[:3] == "it=":
      input_type = input_string[3:]
    else:
      if input_type == "text":
        input_ids = vocabulary.encode(input_string)
        if has_input:
          input_ids.append(text_encoder.EOS_ID)
        x = [num_samples, decode_length, len(input_ids)] + input_ids
        assert len(x) < const_array_size
        x += [0] * (const_array_size - len(x))
        yield {
            "inputs": np.array(x).astype(np.int32),
            "problem_choice": np.array(problem_id).astype(np.int32)
        }
      elif input_type == "image":
        input_path = input_string
        img = read_image(input_path)
        yield {
            "inputs": img.astype(np.int32),
            "problem_choice": np.array(problem_id).astype(np.int32)
        }
      elif input_type == "label":
        input_ids = [int(input_string)]
        x = [num_samples, decode_length, len(input_ids)] + input_ids
        yield {
            "inputs": np.array(x).astype(np.int32),
            "problem_choice": np.array(problem_id).astype(np.int32)
        }
      else:
        raise Exception("Unsupported input type.")


def create_g2p_gt_map(words, pronunciations):
  """Create grapheme-to-phoneme ground true mapping."""
  g2p_gt_map = {}
  for word, pronunciation in zip(words, pronunciations):
    if word in g2p_gt_map:
      g2p_gt_map[word].append(pronunciation)
    else:
      g2p_gt_map[word] = [pronunciation]
  return g2p_gt_map


def calc_errors(g2p_gt_map, estimator, decode_file_path, decode_hp):
  """Calculate a number of prediction errors."""
  inputs, decodes = decode_from_file(
      estimator, decode_file_path, decode_hp)

  correct, errors = 0, 0
  for index, word in enumerate(inputs):
    if decode_hp.return_beams:
      beam_correct_found = False
      for beam_decode in decodes[index]:
        if beam_decode in g2p_gt_map[word]:
          beam_correct_found = True
          break
      if beam_correct_found:
        correct += 1
      else:
        errors += 1
    else:
      if decodes[index] in g2p_gt_map[word]:
        correct += 1
      else:
        errors += 1

  return correct, errors


def decode_from_file(estimator, filename, decode_hp):
  """Compute predictions on entries in filename and write them out."""

  if not decode_hp.batch_size:
    decode_hp.batch_size = 32
    tf.logging.info(
        "decode_hp.batch_size not specified; default=%d" % decode_hp.batch_size)

  hparams = estimator.params
  problem_id = decode_hp.problem_idx
  # Inputs vocabulary is set to targets if there are no inputs in the problem,
  # e.g., for language models where the inputs are just a prefix of targets.
  inputs_vocab = hparams.problems[problem_id].vocabulary["inputs"]
  targets_vocab = hparams.problems[problem_id].vocabulary["targets"]
  problem_name = "grapheme_to_phoneme_problem"
  tf.logging.info("Performing decoding from a file.")
  inputs = _get_inputs(filename)
  num_decode_batches = (len(inputs) - 1) // decode_hp.batch_size + 1

  def input_fn():
    """Function for inputs generator."""
    input_gen = _decode_batch_input_fn(
        problem_id, num_decode_batches, inputs, inputs_vocab,
        decode_hp.batch_size, decode_hp.max_input_size)
    gen_fn = decoding.make_input_fn_from_generator(input_gen)
    example = gen_fn()
    return decoding._decode_input_tensor_to_features_dict(example, hparams)

  decodes = []
  result_iter = estimator.predict(input_fn)
  for result in result_iter:
    if decode_hp.return_beams:
      beam_decodes = []
      output_beams = np.split(result["outputs"], decode_hp.beam_size, axis=0)
      for k, beam in enumerate(output_beams):
        tf.logging.info("BEAM %d:" % k)
        decoded_outputs, _ = decoding.log_decode_results(
            result["inputs"],
            beam,
            problem_name,
            None,
            inputs_vocab,
            targets_vocab)
        beam_decodes.append(decoded_outputs)
      decodes.append(beam_decodes)
    else:
      decoded_outputs, _ = decoding.log_decode_results(
          result["inputs"],
          result["outputs"],
          problem_name,
          None,
          inputs_vocab,
          targets_vocab)
      decodes.append(decoded_outputs)

  return inputs, decodes


def decode_interactively(estimator, decode_hp):
  """Interactive decoding."""
  hparams = estimator.params

  def input_fn():
    gen_fn = decoding.make_input_fn_from_generator(decoding._interactive_input_fn(hparams))
    example = gen_fn()
    example = decoding._interactive_input_tensor_to_features_dict(example, hparams)
    return example

  result_iter = estimator.predict(input_fn)
  for result in result_iter:
    ##problem_idx = result["problem_choice"]
    ##Tracer()()
    ##targets_vocab = hparams.problems[problem_idx].vocabulary["targets"]
    targets_vocab = hparams.problems[0].vocabulary["targets"]

    if decode_hp.return_beams:
      beams = np.split(result["outputs"], decode_hp.beam_size, axis=0)
      scores = None
      if "scores" in result:
        scores = np.split(result["scores"], decode_hp.beam_size, axis=0)
      for k, beam in enumerate(beams):
        tf.logging.info("BEAM %d:" % k)
        beam_string = targets_vocab.decode(decoding._save_until_eos(
            beam, is_image=False))
        if scores is not None:
          tf.logging.info("%s\tScore:%f" % (beam_string, scores[k]))
        else:
          tf.logging.info(beam_string)
    else:
      if decode_hp.identity_output:
        tf.logging.info(" ".join(map(str, result["outputs"].flatten())))
      else:
        tf.logging.info(
            targets_vocab.decode(decoding._save_until_eos(result["outputs"],
                                                          is_image=False)))


def _get_inputs(filename, delimiters="\t "):
  """Returning inputs.

  Args:
    filename: path to file with inputs, 1 per line.
    delimiters: str, delimits records in the file.

  Returns:
    a list of inputs

  """
  tf.logging.info("Getting inputs")
  DELIMITERS_REGEX = re.compile("[" + delimiters + "]+")

  inputs = []
  with tf.gfile.Open(filename) as input_file:
    lines = input_file.readlines()
    for line in lines:
      if set("[" + delimiters + "]+$").intersection(line):
        parts = re.split(DELIMITERS_REGEX, line.strip(), maxsplit=1)
        inputs.append(parts[0])
      else:
        inputs.append(line.strip())
  return inputs


def _decode_batch_input_fn(problem_id, num_decode_batches, inputs,
                           vocabulary, batch_size, max_input_size):
  tf.logging.info(" batch %d" % num_decode_batches)
  for b in range(num_decode_batches):
    tf.logging.info("Decoding batch %d" % b)
    batch_length = 0
    batch_inputs = []
    for _inputs in inputs[b * batch_size:(b + 1) * batch_size]:
      input_ids = vocabulary.encode(_inputs)
      if max_input_size > 0:
        # Subtract 1 for the EOS_ID.
        input_ids = input_ids[:max_input_size - 1]
      input_ids.append(text_encoder.EOS_ID)
      batch_inputs.append(input_ids)
      if len(input_ids) > batch_length:
        batch_length = len(input_ids)
    final_batch_inputs = []
    for input_ids in batch_inputs:
      assert len(input_ids) <= batch_length
      x = input_ids + [0] * (batch_length - len(input_ids))
      final_batch_inputs.append(x)

    yield {
        "inputs": np.array(final_batch_inputs).astype(np.int32),
        "problem_choice": np.array(problem_id).astype(np.int32),
    }
