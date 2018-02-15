import collections

import numpy as np
import tensorflow as tf

from rec_rnn_a3c.src.a3c_network import A3CNetwork
from rec_rnn_a3c.src.util import update_target_graph

Rollout = collections.namedtuple("Rollout", ["env_state", "action_estimate", "reward", "action_target", "value_estimate"])

class A3CModel(object):
    def __init__(self, name, optimizer, global_a3c_network, input_fn, params, global_episodes, saver=None):
        self.name = "model_" + str(name)
        self.optimizer = optimizer
        self.global_episodes = global_episodes
        self.saver = saver
        self.summary_writer = tf.summary.FileWriter("train")

        self.increment = self.global_episodes.assign_add(1)

        self.input_fn = input_fn[0] if isinstance(input_fn, tuple) else input_fn

        self.global_a3c_network = global_a3c_network
        self.local_a3c_network = A3CNetwork(scope=self.name, optimizer=optimizer, params=params)

        self.update_local_ops = update_target_graph('global', self.name)

        self.use_pretrained_rnn = params['use_pretrained_rnn']
        self.unfold_dim = params['unfold_dim']

    def train(self, rollout, sess, gamma, bootstrap_value):
        env_state = rollout.env_state
        action_estimate = rollout.action_estimate
        reward = rollout.reward
        action_target = rollout.action_target
        value_estimate = np.squeeze(rollout.value_estimate, axis=2)

        # Step 1: Calculate Discounted rewards (Act as an estimator for Q(s,a) #
        # bootstrap_value as an estimate of future reward #
        reward_bootstrapped = reward
        #reward_bootstrapped = np.append(reward, bootstrap_value, axis=1)
        # TODO: Check how this should work
        #reward_bootstrapped = discount(reward_bootstrapped, gamma)

        # Step 2: Calculate Advantage based on "Generalized Advantage Estimation (Schulman et al., 2016)" #
        value_bootstrapped = np.append(value_estimate, bootstrap_value, axis=1)
        advantage = reward + 0.01 * value_bootstrapped[:, 1:] - value_bootstrapped[:, :-1]
        #advantage = reward + gamma * value_bootstrapped[:, 1:] - value_bootstrapped[:, :-1]
        #advantage = discount(advantage, gamma)

        # Step 3: Step into AC-Network to train #
        feed_dict = {
            self.local_a3c_network.env_state_input: env_state,
            self.local_a3c_network.c_input: self.rnn_state_c,
            self.local_a3c_network.h_input: self.rnn_state_h,
            self.local_a3c_network.actions: action_estimate,
            self.local_a3c_network.value_target: reward_bootstrapped,
            self.local_a3c_network.advantages: advantage,

            self.local_a3c_network.sv_target: action_target
        }

        fetches = [
            self.local_a3c_network.value_loss,
            self.local_a3c_network.entropy,
            self.local_a3c_network.policy_loss,
            self.local_a3c_network.advantages_sum,
            self.local_a3c_network.train_op,
        ]

        value_loss, entropy, policy_loss, advantages_sum, train_op = sess.run(
            fetches=fetches,
            feed_dict=feed_dict
        )
        # TODO: Normalize some with batch_size * unfold_size (?)
        return value_loss, entropy, policy_loss, advantages_sum


    def predict(self, input_seq, gamma, reward_worker, sess):
        sess.run(self.update_local_ops)
        feed_dict = {
            self.local_a3c_network.env_state_input: input_seq,
            self.local_a3c_network.c_input: self.rnn_state_c,
            self.local_a3c_network.h_input: self.rnn_state_h,
        }

        fetches = [
            self.local_a3c_network.policy_log_prob_output,
            self.local_a3c_network.policy_prob_output,
            self.local_a3c_network.value_output,
            self.local_a3c_network.rnn_state_output,
        ]

        # Step 1: Calculate Policy Output (Prob. Dist. over Actions) & Value Output (Estimation of "goodness") #
        policy_log_prob_output, policy_prob_output, value_output, (self.rnn_state_c, self.rnn_state_h) = sess.run(
            feed_dict=feed_dict,
            fetches=fetches
        )

        # Step 2: Select Action epsilon-greedily #
        actions = np.argmax(policy_prob_output, axis=2)
        actions_shape = np.shape(actions)
        actions = np.reshape(actions, [-1])
        mask = np.random.choice([False, True], np.shape(actions), p=[0.95, 0.05])
        actions[mask] = np.random.randint(0, self.local_a3c_network.item_dim, size=np.sum(mask))
        actions = np.reshape(actions, actions_shape)

        return actions, value_output


    def online_train(self, gamma, input_seq, target_seq, sess, reward_worker, actions, value):
        # Step 3: Calculate reward #
        reward_feed_dict = {
            reward_worker.reward_network.input: input_seq,
            reward_worker.reward_network.c_input: self.rnn_state_c,
            reward_worker.reward_network.h_input: self.rnn_state_h,
        }

        reward_fetches = [
            reward_worker.reward_network.action_logit_dist,
            reward_worker.reward_network.action_prob_dist,
        ]

        reward_action_log_probs, reward_action_probs = sess.run(
            feed_dict=reward_feed_dict,
            fetches=reward_fetches
        )
        reward = [reward_action_probs[:, i, actions[:, i]] for i in range(np.shape(actions)[1])]
        reward = np.reshape(reward, newshape=[self.local_a3c_network.batch_dim, -1])

        step_rollout = Rollout(
            env_state=input_seq,
            action_estimate=actions,
            reward=reward,
            action_target=target_seq,
            value_estimate=value)


        # Step 4: Since we don't know the true final return, we "bootstrap" from current value estimation
        feed_dict = {
            self.local_a3c_network.env_state_input: target_seq,
            self.local_a3c_network.c_input: self.rnn_state_c,
            self.local_a3c_network.h_input: self.rnn_state_h,
        }

        value_output = sess.run(
            fetches=self.local_a3c_network.value_output,
            feed_dict=feed_dict
        )[:, -1, :]

        # Step 5: Calculate Loss based on Action, Cur. Obs., Reward, Fut. Obs., Value and Bootstrap Value #

        self.train(step_rollout, sess, gamma, value_output)
        sess.run(self.update_local_ops)




    def work(self, gamma, reward_worker, sess, coordinator):
        episode_count = sess.run(self.global_episodes)

        # TODO: Include logging
        print("Starting worker %s" % self.name)
        with sess.as_default(), sess.graph.as_default():
            while not coordinator.should_stop():
                # TODO: Reset states for every episode?
                if self.use_pretrained_rnn:
                    rnn_state_c, rnn_state_h = (reward_worker.rnn_state_c, reward_worker.rnn_state_h)
                else:
                    rnn_state_c, rnn_state_h = self.local_a3c_network.rnn_zero_state

                self.rnn_state_c = rnn_state_c
                self.rnn_state_h = rnn_state_h

                sess.run(self.update_local_ops)

                all_rewards = []

                for step, (input, target) in enumerate(self.input_fn()):
                    env_state = input['item']
                    target_action = target['item']

                    num_sequence_splits = np.max([1, np.shape(target_action)[1] // self.unfold_dim])

                    step_reward = 0.0

                    for split in range(num_sequence_splits):
                        state_split = env_state[:, split*self.unfold_dim:(split+1)*self.unfold_dim]
                        target_split = target_action[:, split*self.unfold_dim:(split+1)*self.unfold_dim]

                        feed_dict = {
                            self.local_a3c_network.env_state_input: state_split,
                            self.local_a3c_network.c_input: self.rnn_state_c,
                            self.local_a3c_network.h_input: self.rnn_state_h,
                        }

                        fetches = [
                            self.local_a3c_network.policy_log_prob_output,
                            self.local_a3c_network.policy_prob_output,
                            self.local_a3c_network.value_output,
                            self.local_a3c_network.rnn_state_output,
                        ]

                        # Step 1: Calculate Policy Output (Prob. Dist. over Actions) & Value Output (Estimation of "goodness") #
                        policy_log_prob_output, policy_prob_output, value_output, (self.rnn_state_c, self.rnn_state_h) = sess.run(
                            feed_dict=feed_dict,
                            fetches=fetches
                        )

                        # Step 2: Select Action epsilon-greedily #
                        actions = np.argmax(policy_prob_output, axis=2)
                        actions_shape = np.shape(actions)
                        actions = np.reshape(actions, [-1])
                        mask = np.random.choice([False, True], np.shape(actions), p=[0.95, 0.05])
                        actions[mask] = np.random.randint(0, self.local_a3c_network.item_dim, size=np.sum(mask))
                        actions = np.reshape(actions, actions_shape)

                        # Step 3: Calculate reward #
                        reward_feed_dict = {
                            reward_worker.reward_network.input: state_split,
                            reward_worker.reward_network.c_input: self.rnn_state_c,
                            reward_worker.reward_network.h_input: self.rnn_state_h,
                        }

                        reward_fetches = [
                            reward_worker.reward_network.action_logit_dist,
                            reward_worker.reward_network.action_prob_dist,
                        ]

                        reward_action_log_probs, reward_action_probs = sess.run(
                            feed_dict=reward_feed_dict,
                            fetches=reward_fetches
                        )
                        reward = [reward_action_probs[:, i, actions[:, i]] for i in range(np.shape(actions)[1])]
                        reward = np.reshape(reward, newshape=[self.local_a3c_network.batch_dim, -1])

                        reward = np.zeros(np.shape(reward))
                        reward[:, 4] = 1

                        reward_actions = np.argmax(reward_action_log_probs, axis=2)

                        step_reward += np.mean(reward)

                        step_rollout = Rollout(
                            env_state=state_split,
                            action_estimate=actions,
                            reward=reward,
                            action_target=target_split,
                            value_estimate=value_output)

                        # Step 4: Since we don't know the true final return, we "bootstrap" from current value estimation
                        feed_dict[self.local_a3c_network.env_state_input] = target_split
                        value_output = sess.run(
                            fetches=self.local_a3c_network.value_output,
                            feed_dict=feed_dict
                        )[:, -1, :]

                        # Step 5: Calculate Loss based on Action, Cur. Obs., Reward, Fut. Obs., Value and Bootstrap Value #

                        value_loss, entropy, policy_loss, advantages_sum = self.train(step_rollout, sess, gamma, value_output)

                        sess.run(self.update_local_ops)

                        action_overlap = np.equal(np.reshape(actions, [-1]), np.reshape(target_split, [-1]))
                        action_overlap = np.reshape(action_overlap, newshape=[self.local_a3c_network.batch_dim, -1])

                        estimated_action_probabilities = np.reshape([policy_prob_output[:, i, actions[:, i]]
                                                                     for i in range(np.shape(actions)[1])], [1, -1])
                        target_action_probabilities = np.reshape([policy_prob_output[:, i, target_split[:, i]]
                                                                  for i in range(np.shape(target_split)[1])], [1, -1])

                all_rewards.append(step_reward)

                print("%s  -- Ep: %d[%d] -- "
                      "Reward: %s | "
                      "Val. Loss: %s | "
                      "Pol. Loss: %s | "
                      "Est. Prob: %s | "
                      "Rew. Prob: %s | "
                      "Action Overlap: %s" %
                      (self.name,
                       episode_count,
                       step,
                       np.mean(all_rewards[-5:]),
                       value_loss,
                       policy_loss,
                       np.mean(estimated_action_probabilities),
                       np.mean(target_action_probabilities),
                       np.mean(action_overlap)))

                    # TODO: Maybe add break condition

                sess.run(self.increment)
                episode_count += 1
                # TODO: Update network at the end of episode. Necessary in my setting?

                if episode_count % 5 == 0 and episode_count != 0:
                    if self.saver and episode_count % 250 == 0 and self.name == 'model_0':
                        #self.saver.save(sess,self.model_path+'/model-'+str(episode_count)+'.cptk')
                        print("Saved Model")

                    """ TODO 
                    summary = tf.Summary()
                    summary.value.add(tag='Perf/Reward', simple_value=float(np.mean(self.episode_rewards[-5:])))
                    summary.value.add(tag='Losses/Value Loss', simple_value=float(value_loss))
                    self.summary_writer.add_summary(summary, episode_count)
                    self.summary_writer.flush()
                    """

