from pandas import DataFrame

raw_data = {
    'Outlook': ['overcast', 'overcast', 'overcast', 'overcast', 'rainy', 'rainy', 'rainy',
                'rainy', 'rainy', 'sunny', 'sunny', 'sunny', 'sunny', 'sunny'],
    'Temperature Numeric': [83, 64, 72, 81, 70, 68, 65, 75, 71, 85, 80, 72, 69, 75],
    'Temperature Nominal': ['hot', 'cool', 'mild', 'hot', 'mild', 'cool', 'cool', 'mild',
                            'mild', 'hot', 'hot', 'mild', 'cool', 'mild'],
    'Humidity Numeric': [86, 65, 90, 75, 96, 80, 70, 80, 91, 85, 90, 95, 70, 70],
    'Humidity Nominal': ['high', 'normal', 'high', 'normal', 'high', 'normal', 'normal',
                         'normal', 'high', 'high', 'high', 'high', 'normal', 'normal'],
    'Windy': [False, True, True, False, False, False, True, False, True, False, True,
              False, False, True],
    'Play': ['yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'no', 'yes', 'no', 'no', 'no',
             'no', 'yes', 'yes'],
}


def education():
    my_history = {'primary school': 'some primary school in shanghai',
                  'middle school': 'some middle school in shanghai',
                  'highschool': 'some high school in shanghai',
                  'university': 'SJTU',
                  'exchangeProgram': 'NCSU'}
    return my_history


def dataset():
    df = DataFrame(raw_data,
                   columns=['Outlook', 'Temperature Numeric', 'Temperature Nominal',
                            'Humidity Numeric', 'Humidity Nominal', 'Windy', 'Play']
                   )
    return df
