import os
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))
graphs_dir = os.path.dirname(os.path.realpath(__file__)) + '/../../graphs/'

field2empty_obj = {'type': '',
                   'name': '',
                   'flavors': [],
                   'effects': {},
                   'medical': {},
                   'negatives': {},
                   'difficulty': '',
                   'height': '',
                   'yield': '',
                   'flowering': '',
                   'stretch': '',
                   'parents': [],
                   'description': '',
                   'image_urls': ''
                   }


#### ENCODING SUPPORTED
#  * 'binary_on_off'
#  * 'binary-1'
#  * 'set-real-value'

# define encoding for variables
# encoding type -> variable features
enctype2features = {
    'binary-1': [],
    'binary-on-off': [
        'type',
        'flavors',
        'difficulty',
        'yield',
        'flowering',
        'height',
        'stretch',
        'name'
    ],
    'set-real-value': [
        'effects',
        'medical',
        'negatives'
    ],
}

#######################

grow_info = {
    'difficulty': ('Easy', 'Moderate', 'Difficult'),
    'height': ('< .75 m', '.76-2 m', '> 2 m'),
    'yield': ('40-99', '100-250', '251-500'),
    'flowering': ('7-9 wks', '10-12 wks', '> 12 wks'),
    'stretch': ('< 100%', '100-200%', '> 200%')
}
