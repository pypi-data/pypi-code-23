
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import time
import os
import math
import numpy as np
import tensorflow as tf
from six.moves import xrange



class rmi_simple(object):
    """ Implements the simple "Recursive-index model" described in the paper
        'The Case for Learned Index Structures', which can be found at
        [Kraska et al., 2017](http://arxiv.org/abs/1712.01208)
        ([pdf](http://arxiv.org/pdf/1712.01208.pdf)).

        The first stage is a fully connected neural network with two
        hidden layers. Each second stage model is a single-variable
        linear regression.

        At model creation, the user can choose the widths of the two
        hidden layers and the number of models ("experts") used in
        stage 2.
    """

    def __init__(self,
                 data_set,
                 hidden_layer_widths=[16,16],
                 num_experts=10):
        """Initializes the Recursive-index model

        Args:
            data_set: object of type DataSet, which the model will train on
            hidden layer_widths: length 2 list of hidden layer widths
            num_experts: number of models ("experts") used in stage 2
            
        """
            
        self._data_set = data_set    
        self.hidden_layer_widths = hidden_layer_widths
        self.num_experts = num_experts
        #self._batch_size = batch_size
        #self._key_size = key_size
        #self._key_dtype = key_dtype
        #self._pos_dtype = pos_dtype

        self.max_error_left = None
        self.max_error_right = None
        
        self.min_predict = None
        self.max_predict = None

        self.min_pos = None
        self.max_pos = None


        # Define variables to stored trained tensor variables
        # (e.g. weights and biases).
        # These are used to run inference faster with numpy
        # rather than with TensorFlow.

        num_hidden_layers = len(self.hidden_layer_widths)

        self.hidden_w = [None] * num_hidden_layers
        self.hidden_b = [None] * num_hidden_layers
        self.linear_w = None
        self.linear_b = None
        self.stage_2_w = None
        self.stage_2_b = None
        self._expert_factor = None

        # Pre-calculate some normalization and computation constants,
        # so that they are not repeatedly calculated later.

        # Normalize using mean and dividing by the standard deviation
        self._keys_mean = self._data_set.keys_mean
        self._keys_std_inverse = 1.0 / self._data_set.keys_std
        # Normalize further by dividing by 2*sqrt(3), so that
        # a uniform distribution in the range [a,b] would transform
        # to a uniform distribution in the range [-0.5,0.5]
        self._keys_norm_factor = 0.5 / np.sqrt(3)
        # Precalculation for expert = floor(stage_1_pos * expert_factor)
        self._expert_factor = self.num_experts/self._data_set.num_keys
        
    def new_data(self, data_set):
        """Changes the data set used for training. For example, this function should
           be called after a large number of inserts are performed.

        Args:
            data_set: type DataSet, replaces current data_set with new data_set
        """
        
        self._data_set = data_set

    def _setup_placeholder_inputs(self,batch_size):
        """Create placeholder tensors for inputing keys and positions.

        Args:
            batch_size: Batch size.

        Returns:
            keys_placeholder: Keys placeholder tensor.
            labels_placeholder: Labels placeholder tensor.
        """
        """Generate placeholder variables to represent the input tensors.
        These placeholders are used as inputs by the rest of the model building.
        Args:
        batch_size: The batch size will be baked into both placeholders.
        Returns:
        keys_placeholder: Keys placeholder.
        labels_placeholder: Labels placeholder.
        """
        # Note that the shapes of the placeholders match the shapes of the full
        # image and label tensors, except the first dimension is now batch_size
        # rather than the full size of the train or test data sets.
        with tf.name_scope("placeholders"):
            keys_placeholder = tf.placeholder(tf.float32, shape=(None,self._data_set.key_size), name="keys")
            labels_placeholder = tf.placeholder(tf.int32, shape=(None), name="labels")
        return keys_placeholder, labels_placeholder


    def _fill_feed_dict(self, keys_pl, labels_pl, batch_size=100, shuffle=True):
        """Description

        Args:
            arg1: object type, what it means

        Returns:
            Description of output
        """
        """Fills the feed_dict for training the given step.
        A feed_dict takes the form of:
        feed_dict = {
        <placeholder>: <tensor of values to be passed for placeholder>,
        ....
        }
        Args:
        keys_pl: The keys placeholder, from placeholder_inputs().
        labels_pl: The labels placeholder, from placeholder_inputs().
        Returns:
        feed_dict: The feed dictionary mapping from placeholders to values.
        """
        # Create the feed_dict for the placeholders filled with the next
        # `batch size` examples.
        
        keys_feed, labels_feed = self._data_set.next_batch(batch_size,shuffle)
        feed_dict = {
            keys_pl: keys_feed,
            labels_pl: labels_feed,
        }
        return feed_dict

    
    def _setup_inference_stage_1(self, keys):
        """Description

        Args:
            arg1: object type, what it means

        Returns:
            Description of output
        """
        """TODO: update description 
        Args:
        keys: Images placeholder, from inputs().
        Returns:
        pos_stage_1: Output tensor that predicts key position
        """

        with tf.name_scope('stage_1'):

            keys_std = self._data_set.keys_std
            keys_mean = self._data_set.keys_mean
            key_size = self._data_set.key_size

            hidden_widths = self.hidden_layer_widths
            
            # Normalize
            with tf.name_scope('normalize'):

                keys = tf.cast(keys,dtype=tf.float64)
                
                # Normalize using mean and standard deviation
                keys_normed = tf.scalar_mul(tf.constant(1.0/keys_std),
                                            tf.subtract(keys,tf.constant(keys_mean)))

                # Normalize further by dividing by 2*sqrt(3), so that
                # a uniform distribution in the range [a,b] would transform
                # to a uniform distribution in the range [-0.5,0.5]

                keys_normed = tf.scalar_mul(tf.constant(0.5/np.sqrt(3)),
                                            keys_normed)
            
            # All hidden layers
            output = keys_normed # previous output
            output_size = key_size # previous output size
            for layer_idx in range(0,len(hidden_widths)):
                input = output # get current inputs from previous outputs
                input_size = output_size
                output_size = hidden_widths[layer_idx]
                name_scope = "hidden_" + str(layer_idx+1) # Layer num starts at 1
                with tf.name_scope(name_scope):
                    weights = tf.Variable(
                        tf.truncated_normal([input_size, output_size],
                                            stddev=1.0 / math.sqrt(float(input_size)),
                                            dtype=tf.float64),
                        name='weights',
                        dtype=tf.float64)
                    biases = tf.Variable(tf.zeros([output_size],dtype=tf.float64),
                                         name='biases',
                                         dtype=tf.float64)
                    output = tf.nn.relu(tf.matmul(input, weights) + biases)

                
            # Linear
            with tf.name_scope('linear'):
                weights = tf.Variable(
                    tf.truncated_normal([output_size, 1],
                                        stddev=1.0 / math.sqrt(float(output_size)),
                    dtype=tf.float64),
                    name='weights')
                biases = tf.Variable(tf.zeros([1],dtype=tf.float64),
                                     name='biases')
                    
                pos_stage_1 = tf.matmul(output, weights) + biases
    
                if (key_size == 1):
                    pos_stage_1 = tf.reshape(pos_stage_1,[-1])


                # At this point we want the model to have produced
                # output in the range [-0.5, 0.5], but we want the
                # final output to be in the range [0,N), so we need
                # to add 0.5 and multiply by N.
                # Actually, doint the above process was a mistake,
                # since it results in needing to set the learning_rate
                # very low (N times smaller).
                #pos_stage_1 = tf.scalar_mul(tf.constant(self._data_set.num_keys,
                #                                        dtype=tf.float64),
                #                            tf.add(pos_stage_1,
                #                                   tf.constant(0.5,dtype=tf.float64)))
                    
                pos_stage_1 = tf.identity(pos_stage_1,name="pos")
    
        return pos_stage_1


    def _setup_loss_stage_1(self, pos_stage_1, labels):
        
        """Calculates the loss from the logits and the labels.
        Args:
        pos_stage_1: pos_stage_1 tensor, float - [batch_size, 1].
        labels: Labels tensor, int32 - [batch_size].
        Returns:
        loss: Loss tensor of type float.
        """
        labels = tf.to_int32(labels)
        loss = tf.losses.mean_squared_error(
            labels=labels,
            predictions=pos_stage_1)
        
        return loss


    def _setup_training_stage_1(self, loss, learning_rate):
        """Description

        Args:
            arg1: object type, what it means

        Returns:
            Description of output
        """
        """Sets up the training Ops.
        Creates a summarizer to track the loss over time in TensorBoard.
        Creates an optimizer and applies the gradients to all trainable variables.
        The Op returned by this function is what must be passed to the
        `sess.run()` call to cause the model to train.
        Args:
        loss: Loss tensor, from loss().
        learning_rate: The learning rate to use for gradient descent.
        Returns:
        train_op: The Op for training.
        """
        # Add a scalar summary for the snapshot loss.
        tf.summary.scalar('loss', loss)
        # Create the gradient descent optimizer with the given learning rate.
        optimizer = tf.train.AdamOptimizer(learning_rate)
        #optimizer = tf.train.AdadeltaOptimizer(learning_rate)
        #optimizer = tf.train.GradientDescentOptimizer(learning_rate)
        # Create a variable to track the global step.
        global_step = tf.Variable(0, name='global_step', trainable=False)
        # Use the optimizer to apply the gradients that minimize the loss
        # (and also increment the global step counter) as a single training step.
        train_op = optimizer.minimize(loss, global_step=global_step)
        
        return train_op


    def _setup_inference_stage_2(self, keys, pos_stage_1):
        """Description

        Args:
            arg1: object type, what it means

        Returns:
            Description of output
        """
        """
        Args:
             key should be the same tf.placeholder that inputs keys to stage 1
             pos_stage_1 should be the prediction from stage 1
        Returns:
             
        """

        max_index = self._data_set.num_keys
        # Stage 2 
        with tf.name_scope('stage_2'):

            keys_std = self._data_set.keys_std
            keys_mean = self._data_set.keys_mean

            keys = tf.squeeze(keys,1)
            keys = tf.identity(keys,name='key')
            keys = tf.cast(keys,dtype=tf.float64)
                
            # Normalize using mean and standard deviation
            keys_normed = tf.scalar_mul(tf.constant(1.0/keys_std),
                                        tf.subtract(keys,tf.constant(keys_mean)))
            
            # Normalize further by dividing by 2*sqrt(3), so that
            # a uniform distribution in the range [a,b] would transform
            # to a uniform distribution in the range [-0.5,0.5]
            
            keys_normed = tf.scalar_mul(tf.constant(0.5/np.sqrt(3)),
                                        keys_normed)

            
            expert_index = tf.to_int32(
                tf.floor(
                    tf.scalar_mul(tf.constant(self._expert_factor,dtype=tf.float64),
                                  pos_stage_1)))
    
            # Ensure that expert_index is within range [0,self.num_experts)
            expert_index = tf.maximum(tf.constant(0),expert_index)
            expert_index = tf.minimum(tf.constant(self.num_experts-1),expert_index)
            expert_index = tf.identity(expert_index, name="expert_index")
    
                
            # Explicitly handles batches
            
            num_batches  = tf.shape(pos_stage_1)[0]
            num_batches = tf.identity(num_batches, name="num_batches")
            expert_index_flat = (tf.reshape(expert_index, [-1])
                                 + tf.range(num_batches) * self.num_experts)
            expert_index_flat = tf.identity(expert_index_flat, name="expert_index_flat")

            # This version uses tf.unsroted_segment_sum
            gates_flat = tf.unsorted_segment_sum(
                tf.ones_like(expert_index_flat), 
                expert_index_flat, 
                num_batches * self.num_experts)
            gates = tf.reshape(gates_flat, [num_batches, self.num_experts],
                               name="gates")

            # This version uses SparseTensor
            #expert_index_flat = tf.reshape(expert_index_flat,[-1,1])
            #gates_flat = tf.SparseTensor(tf.cast(expert_index_flat,dtype=tf.int64),
            #                             tf.ones([self.num_experts]),
            #                             dense_shape=[self.num_experts*num_batches,1])
            #gates = tf.sparse_reshape(gates_flat, [num_batches, tf.constant(self.num_experts)],
            #                          name="gates")
            #gates = tf.sparse_tensor_to_dense(gates)
            
            gates = tf.cast(gates,dtype=tf.float64)
            gates = tf.identity(gates, name="gates")

         
            #weights = tf.Variable(
            #    tf.truncated_normal([self.num_experts],
            #                        mean=1.0,
            #                        stddev=0.5,
            #                        dtype=tf.float64),
            #    name='weights')
            weights = tf.Variable(
                tf.truncated_normal([self.num_experts],
                                    mean=1.0*max_index,
                                    stddev=0.5*max_index,
                                    dtype=tf.float64),
                name='weights')

            biases = tf.Variable(tf.zeros([self.num_experts],dtype=tf.float64),
                                 name='biases')

            gated_weights = tf.multiply(gates,weights)
            gated_biases = tf.multiply(gates,biases)
            gated_weights_summed = tf.reduce_sum(gated_weights,axis=1)
            gated_biases_summed = tf.reduce_sum(gated_biases,axis=1)

            #gated_weights = tf.multiply(gates,weights)
            #gated_biases = tf.multiply(gates,biases)
            #gated_weights_summed = tf.reduce_sum(gated_weights,axis=1)
            #gated_biases_summed = tf.reduce_sum(gated_biases,axis=1)
            
            
            gated_weights = tf.identity(gated_weights, name="gated_weights")
            gated_biases = tf.identity(gated_biases, name="gated_biases")
            gated_weights_summed = tf.identity(gated_weights_summed, name="gated_weights_summed")
            gated_biases_summed = tf.identity(gated_biases_summed, name="gated_biases_summed")
            
            #gated_weights = tf.tensordot(gates, weights, axes=[[1],[1]])
            #gated_biases = tf.tensordot(gates, biases, axes=[[1],[1]])
            #stage_2_output = tf.add(tf.multiply(key, gated_weights), gated_biases)
            
            #stage_2_output = tf.matmul(key, gated_weights) + gated_biases
            #stage_2_output = tf.multiply(key, gated_weights) + gated_biases
            #stage_2_output = tf.reduce_sum(tf.multiply(key, gated_weights) + gated_biases)
            #stage_2_output = tf.reduce_sum(summand,axis=1)
            
            pos_stage_2 = tf.add( tf.multiply(keys_normed, gated_weights_summed), gated_biases_summed)
            #stage_2_output = tf.add( tf.matmul(key, gated_weights_summed), gated_biases_summed)

            # At this point we want the model to have produced
            # output in the range [-0.5, 0.5], but we want the
            # final output to be in the range [0,N), so we need
            # to add 0.5 and multiply by N.
            # Actually, doint the above process was a mistake,
            # since it results in needing to set the learning_rate
            # very low (N times smaller).
            #pos_stage_2 = tf.scalar_mul(tf.constant(self._data_set.num_keys,
            #                                        dtype=tf.float64),
            #                            tf.add(pos_stage_2,
            #                                   tf.constant(0.5,dtype=tf.float64)))
            
            
            pos_stage_2 = tf.identity(pos_stage_2, name="pos")
            
        return pos_stage_2

    
    def _setup_loss_stage_2(self, pos_stage_2, labels):
        """Description

        Args:
            arg1: object type, what it means

        Returns:
            Description of output
        """
        """Calculates the loss from the logits and the labels.
        Args:
        pos_stage_2: Stage 2 output tensor, float - [batch_size, 1].
        labels: Labels tensor, int32 - [batch_size].
        Returns:
        loss: Loss tensor of type float.
        """
        # Stage 2 
        with tf.name_scope('stage_2'):
            labels = tf.to_int32(labels)
            loss = tf.losses.mean_squared_error(
                labels=labels,
                predictions=pos_stage_2)
            
        return loss


    def _setup_training_stage_2(self, loss, learning_rate):
        """Description

        Args:
            arg1: object type, what it means

        Returns:
            Description of output
        """
        """Sets up the training Ops.
        Creates a summarizer to track the loss over time in TensorBoard.
        Creates an optimizer and applies the gradients to all trainable variables.
        The Op returned by this function is what must be passed to the
        `sess.run()` call to cause the model to train.
        Args:
        loss: Loss tensor, from loss().
        learning_rate: The learning rate to use for gradient descent.
        Returns:
        train_op: The Op for training.
        """
        # Stage 2 
        with tf.name_scope('stage_2'):
            # Add a scalar summary for the snapshot loss.
            tf.summary.scalar('loss', loss)
            # Create the gradient descent optimizer with the given learning rate.
            optimizer = tf.train.AdamOptimizer(learning_rate)
            #optimizer = tf.train.AdadeltaOptimizer(learning_rate)
            #optimizer = tf.train.GradientDescentOptimizer(learning_rate)
            # Create a variable to track the global step.
            global_step = tf.Variable(0, name='global_step', trainable=False)
            # Get list of variables needed to train stage 2
            variables_stage_2 = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='stage_2')
            #variables_stage_2 = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope='stage_2')
            
            # Use the optimizer to apply the gradients that minimize the loss
            # (and also increment the global step counter) as a single training step.
            #train_op = optimizer.minimize(loss, global_step=global_step)
            train_op = optimizer.minimize(loss, global_step=global_step, var_list=variables_stage_2)
        return train_op

    
    def run_training(self,
                     batch_sizes=[100,100],
                     max_steps=[3000,4000],
                     learning_rates=[0.01,0.01],
                     model_save_dir="tf_checkpoints"):
        """Description

        Args:
            arg1: object type, what it means

        Returns:
            Description of output
        """
        """Train the model for a number of steps."""

        # Reset the default graph  
        tf.reset_default_graph()
    
        # Tell TensorFlow that the model will be built into the default Graph.
        with tf.Graph().as_default():

            ## Stage 1
            
            # Generate placeholders for the images and labels.
            keys_placeholder, labels_placeholder = self._setup_placeholder_inputs(batch_sizes[0])
    
            # Build a Graph that computes predictions from the inference model.
            pos_stage_1 = self._setup_inference_stage_1(keys_placeholder)

            # Add to the Graph the Ops for loss calculation.
            loss_s1 = self._setup_loss_stage_1(pos_stage_1, labels_placeholder)
            
            # Add to the Graph the Ops that calculate and apply gradients.
            train_op_s1 = self._setup_training_stage_1(loss_s1, learning_rates[0])
            
            # Add the Op to compare precitions to the labels during evaluation.
            #eval_correct = evaluation(pos_stage_1, labels_placeholder_s1)
            
            # Build the summary Tensor based on the TF collection of Summaries.
            #summary = tf.summary.merge_all()
            
            
            
            ## Stage 2

            
            pos_stage_2 = self._setup_inference_stage_2(keys_placeholder, pos_stage_1) 
            
            # Add to the Graph the Ops for loss calculation.
            loss_s2 = self._setup_loss_stage_2(pos_stage_2, labels_placeholder)
            
            # Add to the Graph the Ops that calculate and apply gradients.
            train_op_s2 = self._setup_training_stage_2(loss_s2, learning_rates[1])
            
            
            ## Done with Stage definitions
            
            # Add the variable initializer Op.
            init = tf.global_variables_initializer()
            
            # Create a saver for writing training checkpoints.
            saver = tf.train.Saver()
            
            # Create a session for running Ops on the Graph.
            sess = tf.Session()
            
            # Instantiate a SummaryWriter to output summaries and the Graph.
            #summary_writer = tf.summary.FileWriter(model_save_dir, sess.graph)
            
            # And then after everything is built:
            
            # Run the Op to initialize the variables.
            sess.run(init)
            
            
            ## Train Stage 1 

            training_start_time = time.time()
            
            # Start the training loop.
            for step in xrange(max_steps[0]):
                start_time = time.time()
                
                # Fill a feed dictionary with the actual set of keys and labels
                # for this particular training step.
                feed_dict = self._fill_feed_dict(keys_placeholder,
                                                 labels_placeholder,
                                                 batch_size=batch_sizes[0])
                
                # Run one step of the model.  The return values are the activations
                # from the `train_op` (which is discarded) and the `loss` Op.  To
                # inspect the values of your Ops or variables, you may include them
                # in the list passed to sess.run() and the value tensors will be
                # returned in the tuple from the call.
                _, loss_value = sess.run([train_op_s1, loss_s1],
                                         feed_dict=feed_dict)
                
                duration = time.time() - start_time
                
                # Write the summaries and print an overview fairly often.
                if step % 100 == 0:
                    # Print status to stdout.
                    print('Step %d: loss = %.2f (%.3f sec, total %.3f secs)' % (step, np.sqrt(loss_value), duration, time.time() - training_start_time))
                    # Update the events file.
                    #summary_str = sess.run(summary, feed_dict=feed_dict)
                    #summary_writer.add_summary(summary_str, step)
                    #summary_writer.flush()
                    
                # Save a checkpoint and evaluate the model periodically.
                if (step + 1) % 10000 == 0 and (step + 1) != max_steps[0]:
                    checkpoint_file = os.path.join(model_save_dir, 'stage_1.ckpt')
                    saver.save(sess, checkpoint_file, global_step=step)
                if (step + 1) == max_steps[0]:
                    checkpoint_file = os.path.join(model_save_dir, 'stage_1.ckpt')
                    saver.save(sess, checkpoint_file)

            ## Train Stage 2
            
            # Start the training loop.
            for step in xrange(max_steps[1]):
                start_time = time.time()
                
                # Fill a feed dictionary with the actual set of keys and labels
                # for this particular training step.
                feed_dict = self._fill_feed_dict(keys_placeholder,
                                                 labels_placeholder,
                                                 batch_size=batch_sizes[1])
                
                # Run one step of the model.  The return values are the activations
                # from the `train_op` (which is discarded) and the `loss` Op.  To
                # inspect the values of your Ops or variables, you may include them
                # in the list passed to sess.run() and the value tensors will be
                # returned in the tuple from the call.
                _, loss_value = sess.run([train_op_s2, loss_s2],
                                         feed_dict=feed_dict)
                
                duration = time.time() - start_time
                
                # Write the summaries and print an overview fairly often.
                if step % 100 == 0:
                    # Print status to stdout.
                    print('Step %d: loss = %.2f (%.3f sec, total %.3f secs)' % (step, np.sqrt(loss_value), duration, time.time() - training_start_time))
                    # Update the events file.
                    #summary_str = sess.run(summary, feed_dict=feed_dict)
                    #summary_writer.add_summary(summary_str, step)
                    #summary_writer.flush()
                    
                # Save a checkpoint and evaluate the model periodically.
                if (step + 1) % 10000 == 0 and (step + 1) != max_steps[1]:
                    checkpoint_file = os.path.join(model_save_dir, 'stage_2.ckpt')
                    saver.save(sess, checkpoint_file, global_step=step)
                if (step + 1) == max_steps[1]:
                    checkpoint_file = os.path.join(model_save_dir, 'stage_2.ckpt')
                    saver.save(sess, checkpoint_file)



    def run_inference(self,keys,model_save_dir="tf_checkpoints"):
        """Description

        Args:
            arg1: object type, what it means

        Returns:
            Description of output
        """

        """Train the model for a number of steps."""

        batch_size = keys.shape[0]
        
        # Reset the default graph  
        tf.reset_default_graph()
    
        # Tell TensorFlow that the model will be built into the default Graph.
        with tf.Graph().as_default():

            ## Stage 1
            
            # Generate placeholders for the keys and labels.
            keys_placeholder, labels_placeholder = self._setup_placeholder_inputs(batch_size)
    
            # Build a Graph that computes predictions from the inference model.
            pos_stage_1 = self._setup_inference_stage_1(keys_placeholder)

            # Add to the Graph the Ops for loss calculation.
            #loss_s1 = self._setup_loss_stage_1(pos_stage_1, labels_placeholder)
            
            # Add to the Graph the Ops that calculate and apply gradients.
            #train_op_s1 = self._setup_training_stage_1(loss_s1, learning_rates[0])
            
            # Add the Op to compare precitions to the labels during evaluation.
            #eval_correct = evaluation(pos_stage_1, labels_placeholder_s1)
            
            # Build the summary Tensor based on the TF collection of Summaries.
            #summary = tf.summary.merge_all()
            
            
            
            ## Stage 2

            
            pos_stage_2 = self._setup_inference_stage_2(keys_placeholder, pos_stage_1) 
            
            # Add to the Graph the Ops for loss calculation.
            #loss_s2 = self._setup_loss_stage_2(pos_stage_2, labels_placeholder)
            
            # Add to the Graph the Ops that calculate and apply gradients.
            #train_op_s2 = self._setup_training_stage_2(loss_s2, learning_rates[1])
            
            
            ## Done with Stage definitions
            
            # Add the variable initializer Op.
            init = tf.global_variables_initializer()
            
            # Create a saver for writing training checkpoints.
            saver = tf.train.Saver()
            
            # Create a session for running Ops on the Graph.
            sess = tf.Session()
            
            # Instantiate a SummaryWriter to output summaries and the Graph.
            #summary_writer = tf.summary.FileWriter(model_save_dir, sess.graph)
            
            # And then after everything is built:
            
            # Run the Op to initialize the variables.
            sess.run(init)

            checkpoint_file = os.path.join(model_save_dir, "stage_2.ckpt")
            meta_file = os.path.join(model_save_dir,"stage_2.ckpt.meta")
            saver = tf.train.import_meta_graph(meta_file)    
            saver.restore(sess, checkpoint_file)

            # Fill a feed dictionary with the actual set of keys and labels
            # for this particular training step.
            #feed_dict = self._fill_feed_dict(keys_placeholder,
            #                                     labels_placeholder,
            #                                     batch_size)
            feed_dict = {keys_placeholder: keys}

               

            # TODO: the follow code prints out internal tensorflow
            # variable values during inference (for testing model)
            # This code should be put somewhere else

            
            print("Stage 1 position predictions (one per batch):")
            print(sess.run(pos_stage_1,feed_dict=feed_dict))
            
            #print("Actual positions (one per batch):")
            #print(self._data_set.labels[0:batch_size]) 

            print("Expert Index (one per batch):")
            expert_index = sess.graph.get_tensor_by_name("stage_2/expert_index:0")
            print(sess.run(expert_index,feed_dict=feed_dict))
            
            print("Expert Index Flat (all batches):")
            expert_index_flat = sess.graph.get_tensor_by_name("stage_2/expert_index_flat:0")
            print(sess.run(expert_index_flat,feed_dict=feed_dict))

            print("Gate vector (one per batch):")
            gates = sess.graph.get_tensor_by_name("stage_2/gates:0")
            print(sess.run(gates,feed_dict=feed_dict))
            
            print("Gate vector times weights (one per batch):")
            gated_weights = sess.graph.get_tensor_by_name("stage_2/gated_weights:0")
            print(sess.run(gated_weights,feed_dict=feed_dict))
            
            print("Gate vector times weights summed (one per batch):")
            gated_weights_summed = sess.graph.get_tensor_by_name("stage_2/gated_weights_summed:0")
            print(sess.run(gated_weights_summed,feed_dict=feed_dict))
            
            print("Gate vector times biases (one per batch):")
            gated_biases = sess.graph.get_tensor_by_name("stage_2/gated_biases:0")
            print(sess.run(gated_biases,feed_dict=feed_dict))
            
            print("Gate vector times biases summed (one per batch):")
            gated_biases_summed = sess.graph.get_tensor_by_name("stage_2/gated_biases_summed:0")
            print(sess.run(gated_biases_summed,feed_dict=feed_dict))
            
            print("Key (one per batch):")
            key = sess.graph.get_tensor_by_name("stage_2/key:0")
            print(sess.run(key,feed_dict=feed_dict))
        
            print("Stage 2 position prediction = w*key + b (one per batch):")
            stage_2_out = sess.graph.get_tensor_by_name("stage_2/pos:0")
            print(sess.run(stage_2_out,feed_dict=feed_dict))



            expert_index = sess.graph.get_tensor_by_name("stage_2/expert_index:0")
            experts = sess.run(expert_index,feed_dict=feed_dict)
            
            stage_2_out = sess.graph.get_tensor_by_name("stage_2/pos:0")
            pos = sess.run(stage_2_out,feed_dict=feed_dict)
        
        return (pos, experts)

    def get_weights_from_trained_model(self,model_save_dir="tf_checkpoints"):

        
        # Reset the default graph  
        tf.reset_default_graph()
    
        # Tell TensorFlow that the model will be built into the default Graph.
        with tf.Graph().as_default():

             # Generate placeholders for the keys and labels.
            batch_size = 1
            keys_placeholder, labels_placeholder = self._setup_placeholder_inputs(1)
            ## Stage 1
            
            # Build a Graph that computes predictions from the inference model.
            pos_stage_1 = self._setup_inference_stage_1(keys_placeholder)

            ## Stage 2
            
            pos_stage_2 = self._setup_inference_stage_2(keys_placeholder, pos_stage_1) 
            
            # Add the variable initializer Op.
            init = tf.global_variables_initializer()
            
            # Create a saver for writing training checkpoints.
            saver = tf.train.Saver()
            
            # Create a session for running Ops on the Graph.
            sess = tf.Session()
            
            # Run the Op to initialize the variables.
            sess.run(init)

            checkpoint_file = os.path.join(model_save_dir, "stage_2.ckpt")
            meta_file = os.path.join(model_save_dir,"stage_2.ckpt.meta")
            saver = tf.train.import_meta_graph(meta_file)    
            saver.restore(sess, checkpoint_file)


            #for op in tf.get_default_graph().get_operations():
            #    print(op.name)
    
            #tvars = tf.trainable_variables()
            #print(tvars)
            
            #myvars = sess.run([tvars])
            #print(myvars)

            for layer_idx in range(0,len(self.hidden_layer_widths)):

                name_scope = "stage_1/hidden_" + str(layer_idx+1) 

                weights = sess.graph.get_tensor_by_name(name_scope + "/weights:0") 
                self.hidden_w[layer_idx] = sess.run(weights)

                biases = sess.graph.get_tensor_by_name(name_scope + "/biases:0") 
                self.hidden_b[layer_idx] = sess.run(biases)

            linear_w = sess.graph.get_tensor_by_name("stage_1/linear/weights:0")
            self.linear_w = sess.run(linear_w)

            linear_b = sess.graph.get_tensor_by_name("stage_1/linear/biases:0")
            self.linear_b = sess.run(linear_b)

            stage_2_w = sess.graph.get_tensor_by_name("stage_2/weights:0")
            self.stage_2_w = sess.run(stage_2_w)

            stage_2_b = sess.graph.get_tensor_by_name("stage_2/biases:0")
            self.stage_2_b = sess.run(stage_2_b)

            
    def _run_inference_numpy(self,keys):

        #TODO: Check if any variables are None. If so, get the variables.

        #First normalize the key as done in setup_inference()
        #TODO

        keys = (keys - self._keys_mean) * self._keys_std_inverse
        keys = keys * self._keys_norm_factor

        out = np.matmul(keys,self.hidden_1_w)
        out = np.add(out,self.hidden_1_b)
        out = np.maximum(0.0,out)

        out = np.matmul(out,self.hidden_2_w)
        out = np.add(out,self.hidden_2_b)
        out = np.maximum(0.0,out)

        out = np.matmul(out,self.linear_w)
        out = np.add(out,self.linear_b)

        expert = np.multiply(out,self._expert_factor) 
        expert = expert.astype(np.int32) # astype() equivalent to floor() + casting
        expert = np.maximum(0,expert)
        expert = np.minimum(self.num_experts,expert)

        out = np.multiply(keys,self.stage_2_w[expert])
        out = np.add(out,self.stage_2_b[expert])

        
        return (out, expert)

    

    def time_inference_tensorflow(self,keys,N=100,model_save_dir="tf_checkpoints"):

        batch_size = keys.shape[0]
        
        # Reset the default graph  
        tf.reset_default_graph()
    
        # Tell TensorFlow that the model will be built into the default Graph.
        with tf.Graph().as_default():

            ## Stage 1
            
            # Generate placeholders for the images and labels.
            keys_placeholder, labels_placeholder = self._setup_placeholder_inputs(batch_size)    
            # Build a Graph that computes predictions from the inference model.
            pos_stage_1 = self._setup_inference_stage_1(keys_placeholder)

            ## Stage 2
            
            pos_stage_2 = self._setup_inference_stage_2(keys_placeholder, pos_stage_1) 
            
            ## Done with Stage definitions
            
            # Add the variable initializer Op.
            init = tf.global_variables_initializer()
            
            # Create a saver for writing training checkpoints.
            saver = tf.train.Saver()
            
            # Create a session for running Ops on the Graph.
            sess = tf.Session()
            
            # Run the Op to initialize the variables.
            sess.run(init)

            checkpoint_file = os.path.join(model_save_dir, "stage_2.ckpt")
            meta_file = os.path.join(model_save_dir,"stage_2.ckpt.meta")
            saver = tf.train.import_meta_graph(meta_file)    
            saver.restore(sess, checkpoint_file)


            import time
            
            start_time = time.time()
            for n in range(N):

                key = self._data_set.keys[n]
                
                # Fill a feed dictionary with the actual set of keys and labels
                # for this particular training step.
                #feed_dict = self._fill_feed_dict(keys_placeholder,
                #                                     labels_placeholder,
                #                                     batch_size)
                feed_dict = {keys_placeholder: [key]}
                
                expert_index = sess.graph.get_tensor_by_name("stage_2/expert_index:0")
                experts = sess.run(expert_index,feed_dict=feed_dict)
                
                stage_2_out = sess.graph.get_tensor_by_name("stage_2/pos:0")
                pos = sess.run(stage_2_out,feed_dict=feed_dict)

                
        return (time.time() - start_time)/N

        
    
    def calc_min_max_errors(self,
                            batch_size=10000,
                            model_save_dir="tf_checkpoints"):
        """Description

        Args:
            arg1: object type, what it means

        Returns:
            Description of output
        """

        self.max_error_left = np.zeros([self.num_experts])
        self.max_error_right = np.zeros([self.num_experts])
        
        self.min_predict = (np.ones([self.num_experts]) * self._data_set.num_keys) - 1
        self.max_predict = np.zeros([self.num_experts])

        self.min_pos = (np.ones([self.num_experts]) * self._data_set.num_keys) - 1
        self.max_pos = np.zeros([self.num_experts])

        
        for step in range(0, self._data_set.num_keys, batch_size):
        
            positions, experts = self.run_inference(self._data_set.keys[step:(step+batch_size)],model_save_dir=model_save_dir)
            true_positions = self._data_set.labels[step:(step+batch_size)]

            for idx in range(len(true_positions)):

                pos = np.round(positions[idx])
                expert = experts[idx]
                true_pos = true_positions[idx]

                                         
                self.min_predict[expert] = np.minimum(self.min_predict[expert],
                                                  pos)
                self.max_predict[expert] = np.maximum(self.max_predict[expert],
                                                  pos)

                self.min_pos[expert] = np.minimum(self.min_pos[expert],
                                                  true_pos)
                self.max_pos[expert] = np.maximum(self.max_pos[expert],
                                                  true_pos)
                
                error = pos - true_pos
                if error > 0:
                    self.max_error_left[expert] = np.maximum(self.max_error_left[expert],
                                                             error)
                elif error < 0:
                    self.max_error_right[expert] = np.maximum(self.max_error_right[expert],
                                                              np.abs(error))
                    


        for expert in range(self.num_experts):

            print("Expert {}: pos: ({},{}),".format(expert,
                                                    self.min_pos[expert],
                                                    self.max_pos[expert])
                  +" pred ({},{}), error ({},{})".format(self.min_predict[expert],
                                                         self.max_predict[expert],
                                                         self.max_error_left[expert],
                                                         self.max_error_right[expert]))


    def _run_inference_numpy_0_hidden(self,keys):

        #TODO: Check if any variables are None. If so, get the variables.

        #First normalize the key as done in setup_inference()
        #TODO

        keys = (keys - self._keys_mean) * self._keys_std_inverse
        keys = keys * self._keys_norm_factor
                
        out = np.matmul(keys,self.linear_w)
        out = np.add(out,self.linear_b)

        expert = np.multiply(out,self._expert_factor) 
        expert = expert.astype(np.int32) # astype() equivalent to floor() + casting
        expert = np.maximum(0,expert)
        expert = np.minimum(self.num_experts,expert)

        out = np.multiply(keys,self.stage_2_w[expert])
        out = np.add(out,self.stage_2_b[expert])
        
        return (out, expert)

    
    def _run_inference_numpy_1_hidden(self,keys):

        #TODO: Check if any variables are None. If so, get the variables.

        #First normalize the key as done in setup_inference()
        #TODO

        keys = (keys - self._keys_mean) * self._keys_std_inverse
        keys = keys * self._keys_norm_factor
                
        out = np.matmul(keys,self.hidden_w[0])
        out = np.add(out,self.hidden_b[0])
        out = np.maximum(0.0,out)

        out = np.matmul(out,self.linear_w)
        out = np.add(out,self.linear_b)

        expert = np.multiply(out,self._expert_factor) 
        expert = expert.astype(np.int32) # astype() equivalent to floor() + casting
        expert = np.maximum(0,expert)
        expert = np.minimum(self.num_experts,expert)

        out = np.multiply(keys,self.stage_2_w[expert])
        out = np.add(out,self.stage_2_b[expert])
        
        return (out, expert)

    def _run_inference_numpy_1_hidden_debug(self,keys):

        #TODO: Check if any variables are None. If so, get the variables.

        #First normalize the key as done in setup_inference()
        #TODO

        keys = (keys - self._keys_mean) * self._keys_std_inverse
        keys = keys * self._keys_norm_factor
        print(keys)
        
        out = np.matmul(keys,self.hidden_w[0])
        print(out)
        out = np.add(out,self.hidden_b[0])
        print(out)
        out = np.maximum(0.0,out)
        print(out)
        
        out = np.matmul(out,self.linear_w)
        print(out)
        out = np.add(out,self.linear_b)
        print(out)
        
        expert = np.multiply(out,self._expert_factor) 
        expert = expert.astype(np.int32) # astype() equivalent to floor() + casting
        expert = np.maximum(0,expert)
        expert = np.minimum(self.num_experts,expert)

        out = np.multiply(keys,self.stage_2_w[expert])
        print(out)
        out = np.add(out,self.stage_2_b[expert])
        print(out)
        
        return (out, expert)

    
    def _run_inference_numpy_2_hidden(self,keys):

        #TODO: Check if any variables are None. If so, get the variables.

        #First normalize the key as done in setup_inference()
        #TODO

        keys = (keys - self._keys_mean) * self._keys_std_inverse
        keys = keys * self._keys_norm_factor
                
        out = np.matmul(keys,self.hidden_w[0])
        out = np.add(out,self.hidden_b[0])
        out = np.maximum(0.0,out)

        out = np.matmul(out,self.hidden_w[1])
        out = np.add(out,self.hidden_b[1])
        out = np.maximum(0.0,out)

        out = np.matmul(out,self.linear_w)
        out = np.add(out,self.linear_b)

        expert = np.multiply(out,self._expert_factor) 
        expert = expert.astype(np.int32) # astype() equivalent to floor() + casting
        expert = np.maximum(0,expert)
        expert = np.minimum(self.num_experts,expert)

        out = np.multiply(keys,self.stage_2_w[expert])
        out = np.add(out,self.stage_2_b[expert])
        
        return (out, expert)

    ## The following functions are somewhat optimized versions
    # of run_inference using Numpy with different numbers of
    # hidden layers (0, 1, 2, or n)
    
    def _run_inference_numpy_n_hidden(self,keys):

        #TODO: Check if any variables are None. If so, get the variables.

        #First normalize the key as done in setup_inference()
        #TODO

        keys = (keys - self._keys_mean) * self._keys_std_inverse
        keys = keys * self._keys_norm_factor

        out = keys
        for layer_idx in range(0,len(self.hidden_layer_widths)):
                
                out = np.matmul(out,self.hidden_w[layer_idx])
                out = np.add(out,self.hidden_b[layer_idx])
                out = np.maximum(0.0,out)

        out = np.matmul(out,self.linear_w)
        out = np.add(out,self.linear_b)

        expert = np.multiply(out,self._expert_factor) 
        expert = expert.astype(np.int32) # astype() equivalent to floor() + casting
        expert = np.maximum(0,expert)
        expert = np.minimum(self.num_experts,expert)

        out = np.multiply(keys,self.stage_2_w[expert])
        out = np.add(out,self.stage_2_b[expert])
        
        return (out, expert)

