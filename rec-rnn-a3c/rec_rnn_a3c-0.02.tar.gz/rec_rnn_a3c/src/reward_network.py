import numpy as np
import tensorflow as tf
from tensorflow.contrib import slim

from tensorflow.python.ops import variable_scope as vs

from rec_rnn_a3c.src.util import normalized_columns_initializer


class RewardNetwork(object):
    def __init__(self, optimizer, params, scope):
        # TODO: Make parameter
        self.scope = scope

        with tf.variable_scope(self.scope):
            self.optimizer = optimizer

            self.item_dim = params['item_dim']
            self.output_dim = params['output_dim']
            self.hidden_dim = params['hidden_dim']
            self.batch_dim = params['batch_dim']

            self.input = tf.placeholder(tf.int32, shape=[None, None], name='input')
            E = tf.get_variable(name="E", shape=[self.item_dim, self.hidden_dim])
            input = tf.nn.embedding_lookup(params=E, ids=self.input)

            rnn_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_dim, state_is_tuple=True)
            rnn_cell = tf.nn.rnn_cell.DropoutWrapper(rnn_cell, output_keep_prob=0.5)

            c_init = np.zeros((self.batch_dim, rnn_cell.state_size.c), np.float32)
            h_init = np.zeros((self.batch_dim, rnn_cell.state_size.h), np.float32)
            self.rnn_zero_state = [c_init, h_init]

            self.c_input = tf.placeholder(tf.float32, [self.batch_dim, rnn_cell.state_size.c], name='c_input')
            self.h_input = tf.placeholder(tf.float32, [self.batch_dim, rnn_cell.state_size.h], name='h_input')
            state_input = tf.nn.rnn_cell.LSTMStateTuple(self.c_input, self.h_input)

            rnn_output, (rnn_c, rnn_h) = tf.nn.dynamic_rnn(
                inputs=input,
                cell=rnn_cell,
                dtype=tf.float32,
                initial_state=state_input,
            )

            self.state_output = (rnn_c, rnn_h)

            self.action_logit_dist = slim.fully_connected(
                inputs=rnn_output,
                num_outputs=self.output_dim,
                activation_fn=None,
                weights_initializer=normalized_columns_initializer(0.01),
                biases_initializer=None
            )
            self.action_logit_dist = tf.reshape(self.action_logit_dist, [self.batch_dim, -1, self.output_dim])
            self.action_prob_dist = tf.nn.softmax(self.action_logit_dist)

            self.target = tf.placeholder(tf.int32, [self.batch_dim, None], name='target')
            shape = tf.shape(self.target)

            self.loss = tf.contrib.seq2seq.sequence_loss(
                logits=self.action_logit_dist,
                targets=self.target,
                weights=tf.ones(shape=shape),
                average_across_timesteps=False,
                average_across_batch=True,
            )
            self.loss = tf.reduce_sum(self.loss)

            trainable_vars = tf.trainable_variables()
            grads, _ = tf.clip_by_global_norm(tf.gradients(self.loss, trainable_vars), 40.0)
            self.optimizer = tf.train.AdamOptimizer(0.1)
            self.train_op = self.optimizer.apply_gradients(zip(grads, trainable_vars))