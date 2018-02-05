import os

import numpy as np
import tensorflow as tf

from rec_rnn_a3c.src.reward_network import RewardNetwork


class SupervisedRNNModel(object):
    def __init__(self, optimizer, params, scope='supervised_rnn'):
        self.optimizer = optimizer

        self.params = params

        self.unfold_dim = params['unfold_dim']

        self.reward_network = RewardNetwork(optimizer=optimizer, params=params, scope=scope)
        rnn_state_c, rnn_state_h = self.reward_network.rnn_zero_state
        self.rnn_state_c = rnn_state_c
        self.rnn_state_h = rnn_state_h

        self.files = tf.placeholder(tf.string, shape=[None])

    def fit(self, dataset, train_files, sess):
        iterator = dataset.make_initializable_iterator()
        next_element = iterator.get_next()
        sess.run(iterator.initializer, feed_dict={self.files: train_files})

        # Compute for 100 epochs.
        for _ in range(2):
            total_loss = 0.0
            step = 0
            while True:
                try:
                    step += 1
                    step_loss = 0.0
                    # TODO: Possible without feeding?
                    sequence, label_sequence = sess.run(next_element)

                    num_sequence_splits = np.max([1, np.shape(sequence)[1] // self.unfold_dim])

                    for split in range(num_sequence_splits):
                        seq_split = sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]
                        label_seq_split = label_sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]

                        feed_dict = {
                            self.reward_network.input: seq_split,
                            self.reward_network.c_input: self.rnn_state_c,
                            self.reward_network.h_input: self.rnn_state_h,
                            self.reward_network.target: label_seq_split
                        }

                        fetches = [
                            self.reward_network.state_output,
                            self.reward_network.action_logit_dist,
                            self.reward_network.action_prob_dist,
                            self.reward_network.loss,
                            self.reward_network.train_op
                        ]

                        (self.rnn_state_c, self.rnn_state_h), action_logit_dist, action_prob_dist, loss, _ = sess.run(
                            feed_dict=feed_dict,
                            fetches=fetches
                        )

                        action_probs = np.max(action_prob_dist, axis=2)
                        est_actions = np.argmax(action_prob_dist, axis=2)

                        correct_action_probs = [action_prob_dist[:, i, label_seq_split[:, i]] for i in
                                                range(np.shape(label_seq_split)[1])]

                        overall_max = np.max(correct_action_probs)
                        overall_mean = np.mean(correct_action_probs)

                        step_loss += loss
                    total_loss += step_loss / num_sequence_splits

                except tf.errors.OutOfRangeError:
                    raise
                    break

                total_loss /= step
                print("Ep: %d[%d] -- "
                      "Error: %s | "
                      "Estimation[Mean: %s | Max: %s] | "
                      "Correct[Mean: %s | Max: %s]" %
                      (0, step,
                       total_loss,
                       np.mean(action_probs), np.max(action_probs),
                       overall_mean, overall_max))