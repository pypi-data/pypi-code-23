import numpy as np
import tensorflow as tf

from rec_rnn_a3c.src.supervised_rnn import SupervisedRNN

tf.logging.set_verbosity(tf.logging.INFO)


class SupervisedRNNModel(object):
    def __init__(self, optimizer, params, scope='supervised_rnn'):
        self.optimizer = optimizer

        self.params = params

        self.unfold_dim = params['unfold_dim']

        self.reward_network = SupervisedRNN(optimizer=optimizer, params=params, scope=scope)
        rnn_state_c, rnn_state_h = self.reward_network.rnn_zero_state
        self.rnn_state_c = rnn_state_c
        self.rnn_state_h = rnn_state_h

        self.files = tf.placeholder(tf.string, shape=[None])

    def predict(self, seq, sess, num_predictions=1):
        seq_len = len(seq)

        diff = self.unfold_dim - seq_len
        if diff < 0:
            seq = seq[-diff:]
        elif diff > 0:
            seq += [0. for _ in range(self.unfold_dim - seq_len)]

        seq = map(int, seq)
        seq = np.expand_dims(seq, axis=0)

        feed_dict = {
            self.reward_network.input: seq,
            self.reward_network.c_input: self.rnn_state_c,
            self.reward_network.h_input: self.rnn_state_h,
        }

        fetches = [self.reward_network.predictions]

        predictions = []
        for i in range(0, num_predictions):
            prediction_ = sess.run(feed_dict=feed_dict, fetches=fetches)
            prediction_ = np.reshape(prediction_, [-1])
            prediction = prediction_[seq_len - 1 + i]
            seq[0, seq_len + i] = prediction
            predictions.append(predictions)

        return np.reshape(predictions, [-1])

    def eval(self, sess, iterator):
        next_element = iterator.get_next()

        total_loss = 0.0
        total_steps = 0
        while True:
            try:
                total_steps += 1
                step_loss = 0.0
                sequence, label_sequence = sess.run(next_element)

                num_sequence_splits = np.max([1, np.shape(sequence)[1] // self.unfold_dim])

                for split in range(num_sequence_splits):
                    seq_split = sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]
                    label_seq_split = label_sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]

                    feed_dict = {
                        self.reward_network.input: seq_split,
                        self.reward_network.c_input: self.rnn_state_c,
                        self.reward_network.h_input: self.rnn_state_h,
                        self.reward_network.labels: label_seq_split
                    }

                    fetches = [
                        self.reward_network.state_output,
                        self.reward_network.logit_dist,
                        self.reward_network.prob_dist,
                        self.reward_network.loss,
                    ]

                    (self.rnn_state_c, self.rnn_state_h), logit_dist, prob_dist, loss = sess.run(
                        feed_dict=feed_dict,
                        fetches=fetches
                    )

                    step_loss += loss

                total_loss += step_loss / num_sequence_splits
            except tf.errors.OutOfRangeError:
                break

        tf.logging.info("Evaluation -- Error: %s " % (total_loss / total_steps))

    def fit(self, sess, iterator, iteration, num_iterations, num_steps, saver=None, save_path=None):
        next_element = iterator.get_next()

        total_loss = 0.0
        for step in range(num_steps):
            try:
                step += 1
                step_loss = 0.0
                # TODO: Possible without feeding? (Improves performance)
                sequence, label_sequence = sess.run(next_element)

                num_sequence_splits = np.max([1, np.shape(sequence)[1] // self.unfold_dim])

                for split in range(num_sequence_splits):
                    seq_split = sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]
                    label_seq_split = label_sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]

                    feed_dict = {
                        self.reward_network.input: seq_split,
                        self.reward_network.c_input: self.rnn_state_c,
                        self.reward_network.h_input: self.rnn_state_h,
                        self.reward_network.labels: label_seq_split
                    }

                    fetches = [
                        self.reward_network.state_output,
                        self.reward_network.logit_dist,
                        self.reward_network.prob_dist,
                        self.reward_network.loss,
                        self.reward_network.train_op,
                    ]

                    (self.rnn_state_c, self.rnn_state_h), logit_dist, prob_dist, loss, _ = sess.run(
                        feed_dict=feed_dict,
                        fetches=fetches
                    )

                    step_loss += loss

                total_loss += step_loss / num_sequence_splits
            except tf.errors.OutOfRangeError:
                break

            tf.logging.info(
                "Episode [%d/%d] -- Step [%d/%d] -- Error: %s "
                % (iteration, num_iterations, step, num_steps, total_loss / step))

            if step % 10 == 0:
                #saver.save(sess, save_path, global_step=iteration * num_steps + step)
                saver.save(sess, save_path)
                tf.logging.info("Saved model to: %s" % save_path)