import numpy as np

# TODO: create policy class, make other inherit its methods


class EpsilonGreedy:
    def __init__(self, thresh):
        self.thresh = thresh

    def select_action(self, Q):
        n_actions = Q.shape[1]
        eps = np.random.random()
        if eps <= self.thresh:  # explore
            a = np.random.randint(0, n_actions, 1)
            return a
        else:
            a = np.argmax(Q)
            return a


class UCB:
    def __init__(self, agent, c):
        self.c = c
        self.agent = agent

    def select_action(self, Q):
        a = np.argmax(Q + self.c * np.sqrt(np.log(self.agent.t) / self.agent.n))
        return a


# needs fixes
class GBA:
    def __init__(self, alpha, agent):
        self.alpha = alpha
        self.agent = agent

        self.n_actions = agent.n_arms
        self.H = np.zeros((1, self.n_actions))
        self.pdf = None

    def select_action(self):
        self.pdf = np.exp(self.H) / np.sum(np.exp(self.H))
        self.pdf = self.pdf[0]
        a = np.random.choice(np.arange(self.n_actions), p=self.pdf)
        return a

    def update_H(self, a):
        self.H[0, a] = self.H[0, a] + self.alpha * (self.agent.R - self.agent.R_bar) * (1 - self.pdf[a])
        mask = np.ones(self.n_actions, dtype=np.int)
        mask[a] = 0
        self.H[0, mask] = self.H[0, mask] - self.alpha * (self.agent.R - self.agent.R_bar) * self.pdf[mask]
