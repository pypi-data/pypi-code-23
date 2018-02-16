import unittest


class ImitationGroupTestCase(unittest.TestCase):

  number_of_modules = 3

  def setUp(self):
    from hebi.util import create_imitation_group as create_group
    self.group = create_group(
      ImitationGroupTestCase.number_of_modules
    )

  def testThrowOnNegativeSize(self):
    from hebi.util import create_imitation_group as create_group
    with self.assertRaises(ValueError):
      create_group(-1)

  def testThrowOnZeroSize(self):
    from hebi.util import create_imitation_group as create_group
    with self.assertRaises(ValueError):
      create_group(0)

  def testThrowOnNonIntSize(self):
    from hebi.util import create_imitation_group as create_group
    with self.assertRaises(TypeError):
      create_group('foo')

  def testGroupCreated(self):
    self.assertIsNotNone(self.group)

  def testDefaultState(self):
    self.assertEqual(self.group.feedback_frequency, 0.0)
    self.assertEqual(self.group.command_lifetime, 0)
    self.assertIsNone(self.group.get_next_feedback(timeout_ms=0), 'Feedback exists with 0 feedback frequency and no request sent.')
    self.assertEqual(self.group.size, ImitationGroupTestCase.number_of_modules)

  def testNoInfoReceived(self):
    """
    We don't support info request with imitation group. So all calls to
    retrieve info will return ``None``
    """
    self.assertIsNone(self.group.request_info(timeout_ms=0))

  def testCommandLifetime(self):
    prev_lifetime = self.group.command_lifetime
    set_lifetime = 250
    # Set
    self.group.command_lifetime = set_lifetime
    self.assertEqual(self.group.command_lifetime, set_lifetime)
    # Re-Set
    self.group.command_lifetime = prev_lifetime
    self.assertEqual(self.group.command_lifetime, prev_lifetime)

  def testFeedbackFrequency(self):
    prev_freq = self.group.feedback_frequency
    set_freq = 250
    # Set
    self.group.feedback_frequency = set_freq
    self.assertEqual(self.group.feedback_frequency, set_freq)
    # Re-Set
    self.group.feedback_frequency = prev_freq
    self.assertEqual(self.group.feedback_frequency, prev_freq)

  def testRetrieveSyncFeedback(self):
    self.assertEqual(self.group.feedback_frequency, 0.0, 'Feedback frequency in an invalid state. Another test'
                                                         ' which changed frequency probably failed to pass.')
    self.assertTrue(self.group.send_feedback_request())
    self.assertTrue(self.group.get_next_feedback(timeout_ms=0), 'Feedback should always be readily'
                                                                'available without any delay.')
    self.assertIsNone(self.group.get_next_feedback(), 'Subsequent calls to this function should not return feedback.')

  def testRetrieveAsyncFeedback(self):
    self.assertEqual(self.group.feedback_frequency, 0.0, 'Feedback frequency in an invalid state. Another test'
                                                         ' which changed frequency probably failed to pass.')

    frequency = 250.0
    self.group.feedback_frequency = frequency
    self.assertEqual(self.group.feedback_frequency, frequency, 'Could not set feedback frequency')

    from time import sleep
    feedback_count = 0
    def feedback_handler(*args):
      feedback_count = feedback_count + 1

    self.group.add_feedback_handler(feedback_handler)
    sleep(1.0)
    # Sleep for 1 second, which should yield about ``frequency``
    # iterations of the feedback handler

    feedback_count_tolerance = 0.25
    # Huge tolerance (25.0%), but can tweak later
    # This is a heuristic after all..
    infimum_freq = frequency * (1.0 - feedback_count_tolerance)
    supremum_freq = frequency * (1.0 + feedback_count_tolerance)
    count_in_range = (feedback_count >= infimum_freq) and (feedback_count <= supremum_freq)

    self.assertTrue(count_in_range,
                    'Feedback handler called outside of expected range. '
                    'Feedback frequency was {0}, handler called {1} times in a second. '
                    'This was outside the tolerance range of {2}%.'.format(
                      frequency, feedback_count, feedback_count_tolerance * 100.0
                    ))


def __load_hebi():
  # Force add the current directory as a package, which will in return
  # import the `hebi` package from this repository, taking precedence over
  # any user installed variant of the hebi-py API
  if __package__ == None:
    from os.path import abspath, dirname
    from importlib import import_module
    import sys
    sys.path = [dirname(dirname(abspath(__file__)))] + sys.path
    import_module('test')


def main():
  __load_hebi()
  unittest.main()


if __name__ == '__main__':
  main()
