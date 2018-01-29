import numpy as np

from rec_rnn_a3c.src.reward_network import RewardNetwork


class RewardModel(object):
    def __init__(self, optimizer, input_fns, params, scope='reward_network'):
        self.optimizer = optimizer
        self.train_input_fn = input_fns['train']
        self.test_input_fn = input_fns['test']
        self.params = params

        self.unfold_dim = params['unfold_dim']

        self.reward_network = RewardNetwork(optimizer=optimizer, params=params, scope=scope)
        rnn_state_c, rnn_state_h = self.reward_network.rnn_zero_state
        self.rnn_state_c = rnn_state_c
        self.rnn_state_h = rnn_state_h

    def eval(self, sess, gamma):
        total_loss = 0.0
        for step, (input, target) in enumerate(self.test_input_fn()):
            current_observation = input['item']
            future_observation = target['item']

            feed_dict = {
                self.reward_network.input: current_observation,
                self.reward_network.c_input: self.rnn_state_c,
                self.reward_network.h_input: self.rnn_state_h,
                self.reward_network.target: future_observation
            }

            fetches = [
                self.reward_network.state_output,
                self.reward_network.action_logit_dist,
                self.reward_network.action_prob_dist,
                self.reward_network.loss,
            ]

            (self.rnn_state_c, self.rnn_state_h), action_logit_dist, action_prob_dist, loss = sess.run(
                feed_dict=feed_dict,
                fetches=fetches
            )

            action_probs = np.max(action_prob_dist, axis=2)
            correct_action_probs = [action_prob_dist[:, i, future_observation[:, i]] for i in range(np.shape(future_observation)[1])]

            overall_max = np.max(correct_action_probs)
            overall_mean = np.mean(correct_action_probs)

            total_loss += loss

        print("Test: -- "
              "Error: %s | "
              "Estimation[Mean: %s | Max: %s] | "
              "Correct[Mean: %s | Max: %s]" %
              (total_loss / step,
               np.mean(action_probs), np.max(action_probs),
               overall_mean, overall_max))

    def fit(self, episode, sess, gamma):
        total_loss = 0.0

        for step, (input, target) in enumerate(self.train_input_fn()):
            step_loss = 0.0
            current_observation = input['item']
            future_observation = target['item']

            num_sequence_splits = np.max([1, np.shape(current_observation)[1] // self.unfold_dim])

            for split in range(num_sequence_splits):
                state_split = current_observation[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]
                target_split = future_observation[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]

                feed_dict = {
                    self.reward_network.input: state_split,
                    self.reward_network.c_input: self.rnn_state_c,
                    self.reward_network.h_input: self.rnn_state_h,
                    self.reward_network.target: target_split
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

                correct_action_probs = [action_prob_dist[:, i, target_split[:, i]] for i in
                                        range(np.shape(target_split)[1])]

                overall_max = np.max(correct_action_probs)
                overall_mean = np.mean(correct_action_probs)

                step_loss += loss
            total_loss += step_loss / num_sequence_splits

        total_loss /= step
        print("Ep: %d[%d] -- "
              "Error: %s | "
              "Estimation[Mean: %s | Max: %s] | "
              "Correct[Mean: %s | Max: %s]" %
              (episode, step,
               total_loss,
               np.mean(action_probs), np.max(action_probs),
               overall_mean, overall_max))



