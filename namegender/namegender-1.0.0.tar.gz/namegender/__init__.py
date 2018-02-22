""" Predict the gender of a name based on statistical data

@copyright: 2018 samuorous <samuorous@gmail.com>
@licence: GPLv3
"""
from __future__ import division
import pickle
import pkg_resources

MAPPING_PICKLE = pkg_resources.resource_filename('namegender', 'data/mapping.pickle')
MAPPING_TXT = pkg_resources.resource_filename('namegender', 'data/gender_name_mapping.txt')


def reload_mapping():
    """ Load gender name mapping file into dict.

    """
    mapping = dict()
    with open(MAPPING_TXT) as f:
        next(f)  # skip header
        for line in f:
            try:
                name, female_count, male_count = line.split('\t')
                mapping[name] = {'female': int(female_count), 'male': int(male_count)}
            except:
                continue
    with open(MAPPING_PICKLE, mode='wb') as f:
        pickle.dump(mapping, f)


def get_mapping():
    """ Load the name gender mapping.

    :return: Dict with name -> {'male': num of occurrences, 'female': num of occurrences} mapping
    :rtype: dict
    """
    try:
        with open(MAPPING_PICKLE, mode='rb') as f:
            mapping = pickle.load(f)
        return mapping
    except IOError:
        reload_mapping()
        return get_mapping()
    except Exception as e:
        raise e


def predict(name, mapping=None):
    """ Predict the gender of a name. Returns a dict with gender and information on used data to predict the result.
    {
        'name': name,
        'gender': male or female,
        'probability': float (0 to 1),
        'samples': number of data samples the result is based on.
    }
    If name not in dataset gender will be `unknown`.
    :param name: A name
    :type name: str
    :return: {'name': name, 'gender': male or female or unknown, 'probability': float (0 to 1),
              'samples': number of data samples}
    :rtype: dict
    """
    result = {
        'name': name,
        'gender': 'unknown',
        'probability': 0,
        'samples': 0
    }
    name = name.lower().strip()  # normalize name
    try:
        # Load the mapping
        if mapping is None:
            mapping = get_mapping()
        try:
            result['samples'] = mapping[name]['female'] + mapping[name]['male']
            assert result['samples'] > 0

            # Compute the ratio.
            if mapping[name]['female'] >= mapping[name]['male']:
                result['gender'] = 'female'
                result['probability'] = 100 * (mapping[name]['female'] / (result['samples']))
            else:
                result['gender'] = 'male'
                result['probability'] = 100 * (mapping[name]['male'] / (result['samples']))
        except KeyError:
            # Name not in mapping.
            pass
    except Exception as e:
        raise e

    return result


def predict_list(names):
    """ Predict genders of a list of names.

    :param names: List of names ['Jhon', 'Jane']
    :type names: list
    :return: list of dicts {
        'name': name,
        'gender': male or female or unknown,
        'probability': float (0 to 1),
        'samples': number of data samples
    }
    :rtype: dict
    """
    result = list()
    mapping = get_mapping()
    for name in names:
        result.append(predict(name, mapping))
    return result

if __name__ == '__main__':
    print(predict_list(['samusaael', 'Samuel', 'hannah']))
