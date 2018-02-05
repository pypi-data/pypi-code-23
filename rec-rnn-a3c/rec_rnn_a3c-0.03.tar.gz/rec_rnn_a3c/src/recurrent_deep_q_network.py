import random
from collections import deque

import numpy as np
import tensorflow as tf
from tensorflow.contrib import slim


class RecurrentDeepQNetwork(object):
    def __init__(self, model_params):

        self.num_iterations = model_params['num_iterations']
        self.num_pretrain_iterations = model_params['num_pretrain_iterations']
        self.num_annealing_iterations = model_params['num_annealing_iterations']
        self.learning_rate = model_params['learning_rate']
        self.item_dim = model_params['item_dim']
        self.output_dim = model_params['output_dim']
        self.hidden_dim = model_params['hidden_dim']

        self.gamma = model_params['gamma']
        self.tau = model_params['tau']
        self.epsilon = model_params['epsilon']
        self.epsilon_min = model_params['epsilon_min']
        self.epsilon_decay = model_params['epsilon_decay']

        self.epsilon_tick_reduce = (self.epsilon - self.epsilon_min) / self.num_annealing_iterations

        self.unfold_size = tf.placeholder(tf.int32, shape=[], name='unfold_size')
        self.batch_size = tf.placeholder(tf.int32, shape=[], name='batch_size')

        self.input = tf.placeholder(tf.int32, shape=[None, None], name='input')
        E = tf.get_variable(name="E", shape=[self.item_dim, self.hidden_dim])
        input = tf.nn.embedding_lookup(params=E, ids=self.input)

        rnn_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_dim, state_is_tuple=True)
        self.rnn_zero_state = rnn_cell.zero_state(self.batch_size, tf.float32)

        ### Part 1: Quality Function based on RNN and optimal Action based on Quality Function ###

        rnn, self.rnn_state = tf.nn.dynamic_rnn(
            inputs=input,
            cell=rnn_cell,
            dtype=tf.float32,
            initial_state=self.rnn_zero_state
        )

        advantage_input, value_input = tf.split(rnn, 2, 2)

        xavier_init = tf.contrib.layers.xavier_initializer()

        advantage_W = tf.Variable(xavier_init([self.hidden_dim // 2, self.output_dim]))
        advantage_output = tf.matmul(tf.reshape(advantage_input, shape=[-1, self.hidden_dim // 2]), advantage_W)

        value_W = tf.Variable(xavier_init([self.hidden_dim // 2, 1]))
        value_output = tf.matmul(tf.reshape(value_input, shape=[-1, self.hidden_dim // 2]), value_W)

        # Quality Estimation via Value & Advantage Values
        self.q_output = value_output + tf.subtract(advantage_output, tf.reduce_mean(advantage_output, axis=1, keep_dims=True))

        # Predicted Action
        self.q_prediction = tf.argmax(self.q_output, 1)

        ### Part 3: Calculate loss between Q-Target (Q(s_{t+1}, argmax_a_{t+1}) & Q-Estimation (Q(s_{t}, a_{t}) ###

        # Q-Target
        self.q_target = tf.placeholder(tf.float32, shape=[None, None], name='q_target')
        q_target = tf.reshape(self.q_target, shape=[-1])

        # Q-Estimation
        self.actions = tf.placeholder(tf.int32, shape=[None, None], name='actions')
        actions = tf.one_hot(self.actions, self.output_dim, dtype=tf.float32)
        actions = tf.reshape(actions, shape=[-1, self.output_dim])
        q_estimation = tf.reduce_sum(tf.multiply(self.q_output, actions), axis=1)

        # Temporal Difference Error
        td_error = tf.square(q_target - q_estimation)
        self.loss = tf.reduce_mean(td_error)

        # Optimizer & Train-Operation
        optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate)
        self.train_op = optimizer.minimize(self.loss)


class Memory(object):
    def __init__(self, memory_size=50000, batch_size=1, unfold_size=1):
        self.memory = deque(maxlen=memory_size)
        self.batch_size = batch_size
        self.unfold_size = unfold_size

    def extend(self, external_memory):
        while True:
            try:
                self.memory.append(external_memory.memory.pop())
            except IndexError:
                break

    def remember(self, action, state_old, reward, state_future):
        if not isinstance(action, np.ndarray):
            action = np.reshape(action, newshape=[self.batch_size, self.unfold_size])

        if not isinstance(reward, np.ndarray):
            reward = np.reshape(reward, newshape=[self.batch_size, self.unfold_size])

        self.memory.append((action, state_old, reward, state_future))

    def sample(self):
        minibatch = random.sample(self.memory, self.batch_size)

        actions, current_observations, rewards, future_observations = [], [], [], []
        for action, current_observation, reward, future_observation in minibatch:
            actions.append(action)
            current_observations.append(current_observation)
            rewards.append(reward)
            future_observations.append(future_observation)

        return {
            'actions': np.reshape(actions, newshape=[self.batch_size, self.unfold_size]),
            'current_observations': np.reshape(current_observations, newshape=[self.batch_size, self.unfold_size]),
            'rewards': np.reshape(rewards, newshape=[self.batch_size, self.unfold_size]),
            'future_observations': np.reshape(future_observations, newshape=[self.batch_size, self.unfold_size]),
        }

# Slow increment update that allows us to update target network with parameters of main network
def update_target_graph(vars, tau):
    op_holder = []
    num_vars = len(vars)

    for index, var in enumerate(vars[:num_vars//2]):
        op_holder.append(
            vars[index + num_vars//2].assign(tau*var.value() + (1-tau)*vars[index + num_vars//2].value())
        )
    return op_holder