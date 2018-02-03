import numpy as np
import garlic.policies as pol


class MultiArmedBandit:
    def __init__(self, n_arms, reward, policy):
        self.n_arms = n_arms
        self.reward = reward
        self.policy = policy

        self.Q = np.zeros((1, n_arms))
        # self.Q[0, :] = 10  # optimistic initialization
        self.n = np.ones((1, n_arms))  # number of times an action is selected
        self.t = 1
        self.R = 0
        self.R_bar = 0
        self.a = None

    def make_action(self):
        # a = self.policy.select_action(self.Q)
        a = self.policy.select_action()
        self.R = self.reward(a)
        self.R_bar = self.R_bar + (1 / self.t) * (self.R - self.R_bar)

        self.policy.update_H(a)
        self.a = a
        self._update_q(a)
        self.n[0, a] += 1
        self.t += 1

    def _update_q(self, a):
        # alpha = 1 / self.n[0, a]
        alpha = 0.1
        self.Q[0, a] = self.Q[0, a] + alpha * (self.R - self.Q[0, a])
