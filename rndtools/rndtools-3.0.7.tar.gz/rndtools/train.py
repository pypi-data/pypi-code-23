from __future__ import print_function

import inspect
import json
import os
import shutil
from datetime import datetime

import click
import numpy as np
from contexttimer import Timer
from keras.callbacks import CSVLogger
from keras.utils.layer_utils import count_params
from keras.utils import plot_model

from rndtools.io import ensure_dirs
from rndtools.keras_callbacks import VisualizeHistory
from rndtools.keras_dataset_generator import DataSerializer, Dataset


def echo_info(s):
    click.echo('-' * 30)
    click.echo(s)
    click.echo('-' * 30)


class MetaInfo(object):
    def __init__(self):
        self.date = datetime.today()
        self.processing_time = None
        self.number_of_epochs = None
        self.best_test_loss = None
        self.best_train_loss = None
        self.weights_file_size = None
        self.dataset_info = None
        self.number_of_model_parameters = None

    def from_history(self, history):
        self.number_of_epochs = len(history.get('loss'))
        self.best_train_loss = np.round(min(history['loss']), 4)

        if 'val_loss' in history:
            self.best_test_loss = np.round(min(history['val_loss']), 4)

    def serialize(self):
        return {
            'creation_date': str(self.date.date()),
            'processing_time_in_minutes': self.processing_time,
            'number_of_epochs': self.number_of_epochs,
            'best_test_loss': self.best_test_loss,
            'best_train_loss': self.best_train_loss,
            'dataset_info': self.dataset_info,
            'weights_file_size': self.weights_file_size,
            'number_of_model_parameters': self.number_of_model_parameters
        }

    def save_to(self, file):
        json.dump(self.serialize(), open(file, 'w+'), indent=2)


class DatasetInfo(object):
    def __init__(self, data):
        self.data = data

    def serialize(self):
        data = filter(lambda d: isinstance(d, Dataset), self.data)

        return [
            {
                'dir_path': d.path
            }
            for d in data
            ]


def save_summary(f, layers, relevant_nodes=None,
                 line_length=100, positions=[.33, .55, .67, 1.]):
    '''Prints a summary of a layer

    # Arguments
        layers: list of layers to print summaries of
        relevant_nodes: list of relevant nodes
        line_length: total length of printed lines
        positions: relative or absolute positions of log elements in each line
    '''
    if positions[-1] <= 1:
        positions = [int(line_length * p) for p in positions]
    # header names for the different log elements
    to_display = ['Layer (type)', 'Output Shape', 'Param #', 'Connected to']

    def print_row(fields, positions):
        line = ''
        for i in range(len(fields)):
            if i > 0:
                line = line[:-1] + ' '
            line += str(fields[i])
            line = line[:positions[i]]
            line += ' ' * (positions[i] - len(line))
        print(line, file=f)

    print('_' * line_length, file=f)
    print_row(to_display, positions)
    print('=' * line_length, file=f)

    def print_layer_summary(layer):
        try:
            output_shape = layer.output_shape
        except:
            output_shape = 'multiple'
        connections = []
        for node_index, node in enumerate(layer.inbound_nodes):
            if relevant_nodes:
                node_key = layer.name + '_ib-' + str(node_index)
                if node_key not in relevant_nodes:
                    # node is node part of the current network
                    continue
            for i in range(len(node.inbound_layers)):
                inbound_layer = node.inbound_layers[i].name
                inbound_node_index = node.node_indices[i]
                inbound_tensor_index = node.tensor_indices[i]
                connections.append(inbound_layer + '[' + str(inbound_node_index) + '][' + str(inbound_tensor_index) + ']')

        name = layer.name
        cls_name = layer.__class__.__name__
        if not connections:
            first_connection = ''
        else:
            first_connection = connections[0]
        fields = [name + ' (' + cls_name + ')', output_shape, layer.count_params(), first_connection]
        print_row(fields, positions)
        if len(connections) > 1:
            for i in range(1, len(connections)):
                fields = ['', '', '', connections[i]]
                print_row(fields, positions)

    for i in range(len(layers)):
        print_layer_summary(layers[i])
        if i == len(layers) - 1:
            print('=' * line_length, file=f)
        else:
            print('_' * line_length, file=f)

    # trainable_count, non_trainable_count = count_params(layers)
    #
    # print('Total params: {:,}'.format(trainable_count + non_trainable_count), file=f)
    # print('Trainable params: {:,}'.format(trainable_count), file=f)
    # print('Non-trainable params: {:,}'.format(non_trainable_count), file=f)
    # print('_' * line_length, file=f)


def train_model(model_dir, get_model_function, training_function, loading_data_function, overwrite=False):
    """

    :type overwrite: bool
    :type model_dir: str
    :type get_model_function: callable
    :type training_function: callable
    :type loading_data_function: callable
    """

    click.secho('\nModel path: {}'.format(click.format_filename(os.path.abspath(model_dir))), fg='blue')

    if os.path.exists(model_dir):
        if not overwrite:
            click.confirm('\nModel dir already exists. Do you want to REMOVE whole dir before training?', abort=True)

        echo_info('Removing dir...')
        shutil.rmtree(model_dir)

    meta_file_path = os.path.join(model_dir, 'meta.json')
    weights_path = os.path.join(model_dir, 'weights.h5')

    with Timer(factor=1. / 60, output=True, fmt='Process took {:.0f} minutes.') as t:
        meta_info = MetaInfo()

        click.echo()

        echo_info('Creating dirs...')
        ensure_dirs(model_dir)

        echo_info('Creating and compiling model...')
        model = get_model_function()

        echo_info('Saving summary...')
        meta_info.number_of_model_parameters = model.count_params()
        meta_info.save_to(meta_file_path)
        with open(os.path.join(model_dir, 'summary.txt'), 'w+') as f:
            save_summary(f, model.layers)

        echo_info('Saving architecture...')
        open(os.path.join(model_dir, 'architecture.json'), 'w').write(model.to_json())

        echo_info('Plotting model...')
        plot_model(model, to_file=os.path.join(model_dir, 'model.png'), show_shapes=True)

        echo_info('Saving model source code...')
        with open(os.path.join(model_dir, 'model.py'), 'w+') as f:
            f.write(inspect.getsource(get_model_function))
            f.write('\n')
            f.write(inspect.getsource(training_function))

        echo_info('Loading data...')
        data = loading_data_function()
        meta_info.dataset_info = DatasetInfo(data).serialize()
        meta_info.save_to(meta_file_path)

        echo_info('Instantiating callbacks...')
        callbacks = [
            VisualizeHistory(dir_path=model_dir),
            CSVLogger(filename=os.path.join(model_dir, 'history.csv'))
        ]

        echo_info('Training model...')
        with Timer(factor=1. / 60, output=True, fmt='Training model took {:.0f} minutes'):
            params = {
                'data': data,
                'model': model,
                'model_dir': model_dir
            }

            if 'callbacks' in inspect.getargspec(training_function).args:
                params['callbacks'] = callbacks
            else:
                click.secho("'callbacks' argument not found in training function. Callbacks will not be added.", fg='red')

            history = training_function(**params)

        echo_info('Saving history...')
        ds_dataset_out = DataSerializer(os.path.join(model_dir, "history.pkl"))
        ds_dataset_out.pickle_out(history.history)

        echo_info('Saving meta info...')
        meta_info.from_history(history.history)
        meta_info.processing_time = t.elapsed
        if os.path.exists(weights_path): meta_info.weights_file_size = os.stat(weights_path).st_size
        meta_info.save_to(meta_file_path)

        click.secho('\nFinished!', fg='green', bold=True)
