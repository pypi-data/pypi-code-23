import json

import defines
import arguments
import tensor_maps

# Keras Imports
import keras.backend as K
from keras.models import load_model

def set_args_and_get_model_from_semantics(args, semantics_json):
    '''Recreate a model from a json file specifying model semantics.

    Update the args namespace from the semantics file values.
    Assert that the serialized tensor map and the recreated one are the same.

    Arguments:
        args.tensor_map: String which indicates tensor map to use or None
        args.window_size: sites included in the tensor map
        args.read_limit: Maximum reads included in the tensor map
        args.annotations: List of annotations or None
        semantics_json: Semantics json file (created with serialize_model_semantics())

    Returns:
        The Keras model
    '''
    with open(semantics_json, 'r') as infile:
        semantics = json.load(infile)

    if 'input_tensor_map' in semantics:
        args.tensor_map = semantics['input_tensor_map_name']
        args.window_size = semantics['window_size']
        args.read_limit = semantics['read_limit']
        tm = tensor_maps.get_tensor_channel_map_from_args(args)
        assert(len(tm) == len(semantics['input_tensor_map']))
        #print('tm len:', len(tm), 'semantics map:', semantics['input_tensor_map'])
        for key in tm:
            assert(tm[key] == semantics['input_tensor_map'][key])

    if 'input_annotations' in semantics:
        args.annotations = semantics['input_annotations']

    args.input_symbols = semantics['input_symbols']
    args.labels = semantics['output_labels']

    if 'data_dir' in semantics:
        args.data_dir = semantics['data_dir']

    weight_path_hd5 = os.path.join(os.path.dirname(semantics_json), semantics['architecture'])
    print('Loading keras weight file from:', weight_path_hd5)
    model = load_model(weight_path_hd5, custom_objects=get_metric_dict(args.labels))
    model.summary()
    return model

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~ Metrics ~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def precision(y_true, y_pred):
    '''Calculates the precision, a metric for multi-label classification of
    how many selected items are relevant.
    '''
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision


def recall(y_true, y_pred):
    '''Calculates the recall, a metric for multi-label classification of
    how many relevant items are selected.
    '''
    true_positives = K.sum(K.round(K.clip(y_true*y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall


def per_class_recall(labels):
    recall_fxns = []

    for label_key in labels:
        label_idx = labels[label_key]
        string_fxn = 'def '+ label_key + '_recall(y_true, y_pred):\n'
        string_fxn += '\ttrue_positives = K.sum(K.round(K.clip(y_true*y_pred, 0, 1)), axis=0)\n'
        string_fxn += '\tpossible_positives = K.sum(K.round(K.clip(y_true, 0, 1)), axis=0)\n'
        string_fxn += '\treturn true_positives['+str(label_idx)+'] / (possible_positives['+str(label_idx)+'] + K.epsilon())\n'

        exec(string_fxn)
        recall_fxn = eval(label_key + '_recall')
        recall_fxns.append(recall_fxn)

    return recall_fxns


def per_class_precision(labels):
    precision_fxns = []

    for label_key in labels:
        label_idx = labels[label_key]
        string_fxn = 'def '+ label_key + '_precision(y_true, y_pred):\n'
        string_fxn += '\ttrue_positives = K.sum(K.round(K.clip(y_true*y_pred, 0, 1)), axis=0)\n'
        string_fxn += '\tpredicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)), axis=0)\n'
        string_fxn += '\treturn true_positives['+str(label_idx)+'] / (predicted_positives['+str(label_idx)+'] + K.epsilon())\n'

        exec(string_fxn)
        precision_fxn = eval(label_key + '_precision')
        precision_fxns.append(precision_fxn)

    return precision_fxns


def get_metric_dict(labels=defines.SNP_INDEL_LABELS):
    metrics = {'precision':precision, 'recall':recall}
    precision_fxns = per_class_precision(labels)
    recall_fxns = per_class_recall(labels)
    for i,label_key in enumerate(labels.keys()):
        metrics[label_key+'_precision'] = precision_fxns[i]
        metrics[label_key+'_recall'] = recall_fxns[i]

    return metrics

def args_and_model_from_semantics(semantics_json):
    args = arguments.parse_args()
    model = set_args_and_get_model_from_semantics(args, semantics_json)
    return args, model

