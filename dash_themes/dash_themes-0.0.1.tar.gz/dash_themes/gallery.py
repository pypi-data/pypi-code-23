# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
from textwrap import dedent


def Dropdowns():
    options = [
        {'label': 'New York City', 'value': 'NYC'},
        {'label': u'Montréal', 'value': 'MTL'},
        {'label': 'San Francisco', 'value': 'SF'}
    ]
    return [
        [
            html.Label('Dropdown'),
            dcc.Dropdown(
                options=options,
                value='MTL',
                clearable=True
            )
        ],

        [
            html.Label('Multi-Select Dropdown'),
            dcc.Dropdown(
                options=options,
                value=['MTL', 'SF'],
                multi=True,
                clearable=True
            )
        ],

        [
            html.Label('Placeholder'),
            dcc.Dropdown(
                options=options,
                placeholder='Select a city'
            )
        ],

        [
            html.Label('Disabling Search'),
            dcc.Dropdown(
                options=options,
                searchable=False
            )
        ],

        [
            html.Label('Disabled Dropdown'),
            dcc.Dropdown(
                options=options,
                value='MTL',
                disabled=True
            )
        ],

        [
            html.Label('Disabled Multi Dropdown'),
            dcc.Dropdown(
                options=options,
                value=['MTL', 'SF'],
                multi=True
            )
        ]
    ]


def Sliders():
    return [
        [
            html.Label('Default Slider'),
            dcc.Slider(
                min=0,
                max=20,
                step=0.5,
                value=10,
            )
        ],

        [
            html.Label('Marks and Steps'),
            dcc.Slider(
                min=0,
                max=10,
                step=None,
                marks={
                    0: '0 °F',
                    3: '3 °F',
                    5: '5 °F',
                    7.65: '7.65 °F',
                    10: '10 °F'
                },
                value=5
            )
        ],

        [
            html.Label('With Dots'),
            dcc.Slider(
                min=0,
                max=20,
                step=2,
                value=10,
            )
        ],

        [
            html.Label('Disabled'),
            dcc.Slider(
                min=0,
                max=20,
                step=2,
                value=10,
                disabled=True
            )
        ],

        [
            html.Label('Included=False'),
            dcc.Slider(
                min=0,
                max=20,
                step=2,
                value=10,
                included=False
            )
        ]
    ]


def RangeSliders():
    return [
        [
            html.Label('Default Slider'),
            dcc.RangeSlider(
                min=0,
                max=20,
                step=0.5,
                value=[10, 12],
            )
        ],

        [
            html.Label('Marks and Steps'),
            dcc.RangeSlider(
                min=0,
                max=10,
                step=None,
                marks={
                    0: '0 °F',
                    3: '3 °F',
                    5: '5 °F',
                    7.65: '7.65 °F',
                    10: '10 °F'
                },
                value=5
            )
        ],

        [
            html.Label('With Dots'),
            dcc.RangeSlider(
                min=0,
                max=20,
                step=2,
                value=[10, 12],
            )
        ],

        [
            html.Label('Disabled'),
            dcc.RangeSlider(
                min=0,
                max=20,
                step=2,
                value=[10, 12],
                disabled=True
            )
        ],

        [
            html.Label('Included=False'),
            dcc.RangeSlider(
                min=0,
                max=20,
                step=2,
                value=[10, 12],
                disabled=True
            )
        ]
    ]


def DatePickerSingles():
    return [
        [
            html.Label('Default'),
            dcc.DatePickerSingle(
                date=dt.now()
            )
        ],

        [
            html.Label('Max and Min Date Allowed'),
            dcc.DatePickerSingle(
                date=dt(2017, 2, 15),
                min_date_allowed=dt(2017, 2, 10),
                max_date_allowed=dt(2017, 2, 20),
            )
        ],

        [
            html.Label('Vertical'),
            dcc.DatePickerSingle(
                date=dt(2017, 2, 15),
                calendar_orientation='vertical'
            )
        ],

        [
            html.Label('Clearable'),
            dcc.DatePickerSingle(
                date=dt(2017, 2, 15),
                min_date_allowed=dt(2017, 2, 10),
                max_date_allowed=dt(2017, 2, 20),
                calendar_orientation='vertical'
            )
        ],

        [
            html.Label('Number of Months Shown'),
            dcc.DatePickerSingle(
                date=dt(2017, 2, 15),
                number_of_months_shown=3
            )
        ],

        [
            html.Label('Placeholder'),
            dcc.DatePickerSingle(
                placeholder='Select a date...'
            )
        ],

        [
            html.Label('Show Outside Days'),
            dcc.DatePickerSingle(
                date=dt.now(),
                show_outside_days=True
            )
        ],

        [
            html.Label('Full Screen Portal'),
            dcc.DatePickerSingle(
                date=dt.now(),
                with_full_screen_portal=True
            )
        ],

        [
            html.Label('Portal'),
            dcc.DatePickerSingle(
                date=dt.now(),
                with_portal=True
            )
        ],

        [
            html.Label('Day Size'),
            dcc.DatePickerSingle(
                date=dt.now(),
                day_size=50
            )
        ]
    ]


def DatePickerRanges():
    return [
        [
            html.Label('Default'),
            dcc.DatePickerRange(
                start_date=dt.now()
            )
        ],

        [
            html.Label('Max and Min Date Allowed'),
            dcc.DatePickerRange(
                start_date=dt(2017, 2, 15),
                min_date_allowed=dt(2017, 2, 10),
                max_date_allowed=dt(2017, 2, 20),
            )
        ],

        [
            html.Label('Vertical'),
            dcc.DatePickerRange(
                start_date=dt(2017, 2, 15),
                calendar_orientation='vertical'
            )
        ],

        [
            html.Label('Clearable'),
            dcc.DatePickerRange(
                start_date=dt(2017, 2, 15),
                min_date_allowed=dt(2017, 2, 10),
                max_date_allowed=dt(2017, 2, 20),
                calendar_orientation='vertical'
            )
        ],

        [
            html.Label('Number of Months Shown'),
            dcc.DatePickerRange(
                start_date=dt(2017, 2, 15),
                number_of_months_shown=3
            )
        ],

        [
            html.Label('Placeholder'),
            dcc.DatePickerRange(
                start_date_placeholder_text='Select a date...'
            )
        ],

        [
            html.Label('Show Outside Days'),
            dcc.DatePickerRange(
                start_date=dt.now(),
                show_outside_days=True
            )
        ],

        [
            html.Label('Full Screen Portal'),
            dcc.DatePickerRange(
                start_date=dt.now(),
                with_full_screen_portal=True
            )
        ],

        [
            html.Label('Portal'),
            dcc.DatePickerRange(
                start_date=dt.now(),
                with_portal=True
            )
        ],

        [
            html.Label('Day Size'),
            dcc.DatePickerRange(
                start_date=dt.now(),
                day_size=50
            )
        ],

        [
            html.Label('Minimum Nights'),
            dcc.DatePickerRange(
                start_date=dt.now(),
                minimum_nights=5
            )
        ],
    ]


def TextInputs():
    return [
        [
            html.Label('Input Without Type'),
            dcc.Input()
        ],


        [
            html.Label('Text Input With Value'),
            dcc.Input(
                type='text',
                value='Value'
            )
        ],

        [
            html.Label('Text Input With Placeholder'),
            dcc.Input(
                type='text',
                placeholder='Enter a value...'
            )
        ],

        [
            html.Label('Textarea'),
            dcc.Textarea()
        ],

        [
            html.Label('Textarea With Placeholder'),
            dcc.Textarea(
                placeholder='Enter a value...'
            )
        ],

        [
            html.Label('Textarea With Value'),
            dcc.Textarea(
                value='Value'
            )
        ],
    ]


def Checkboxes():
    options = [
        {'label': 'New York City', 'value': 'NYC'},
        {'label': 'Montréal', 'value': 'MTL'},
        {'label': 'San Francisco', 'value': 'SF'}
    ]
    values = ['MTL', 'SF']
    return [
        [
            html.Label('Checkboxes'),
            dcc.Checklist(options=options, values=values)
        ],
        [
            html.Label('Horizontal Checkboxes'),
            dcc.Checklist(
                options=options,
                values=values,
                labelStyle={'display': 'inline-block'}
            )
        ]
    ]


def RadioItems():
    options = [
        {'label': 'New York City', 'value': 'NYC'},
        {'label': 'Montréal', 'value': 'MTL'},
        {'label': 'San Francisco', 'value': 'SF'}
    ]
    value = 'MTL'
    return [
        [
            html.Label('RadioItems'),
            dcc.RadioItems(options=options, value=value)
        ],
        [
            html.Label('Horizontal RadioItems'),
            dcc.RadioItems(
                options=options,
                value=value,
                labelStyle={'display': 'inline-block'}
            )
        ]
    ]


def Buttons():
    return [
        [
            html.Label('Button'),
            html.Button('Submit')
        ],
        [
            html.Label('Button Disabled'),
            html.Button('Submit', disabled=True)
        ],
        [
            html.Label('Button Primary'),
            html.Button('Submit', className="button-primary")
        ]
    ]


def Text():
    return [
        [
            html.Label('Markdown'),
            dcc.Markdown(dedent('''
                #### Dash and Markdown

                Dash supports [Markdown](http://commonmark.org/help).

                Markdown is a simple way to write and format text.
                It includes a syntax for things like **bold text** and
                *italics*,
                [links](http://commonmark.org/help), inline `code` snippets,
                lists, quotes, and more.

                > Don't forget blockquotes!
                > Blockquotes have a simple left border and an indent,
                > there is nothing too fancy here.
                > These styles are meant to be familiar with GitHub markdown.
            '''))
        ],

        [
            html.H1('Heading 1'),
            html.H2('Heading 2'),
            html.H3('Heading 3'),
            html.H4('Heading 4'),
            html.H5('Heading 5'),
            html.H6('Heading 6'),
        ],

        [
            html.Ul([
                html.Li('Unordered Lists have basic styles'),
                html.Li('They use the circle list style'),
                html.Li([
                    'Also, ',
                    html.Ul([
                        html.Li('nested lists feel right'),
                        html.Li('This could be a Ul or a Ol'),
                    ])
                ])
            ])
        ],

        [
            html.Ol([
                html.Li('Ordered Lists have basic styles too'),
                html.Li('They use the decimal list style'),
                html.Li([
                    'And also',
                    html.Ol([
                        html.Li('ordered lists can be nested too'),
                        html.Li('As could unordered lists'),
                    ])
                ])
            ])
        ]
    ]


def Tables():
    return [
        [
            html.Label('Simple Tables'),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th('Name'),
                        html.Th('Age'),
                        html.Th('Sex'),
                        html.Th('Location'),
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td('Dave Gamache'),
                        html.Td(26),
                        html.Td('Male'),
                        html.Td('San Francisco'),
                    ]),
                    html.Tr([
                        html.Td('Dwayne Johnson'),
                        html.Td(42),
                        html.Td('Male'),
                        html.Td('Hayward'),
                    ])
                ])
            ])
        ]
    ]

def Graphs():
    return [
        [
            html.Label('Bar Chart'),
            dcc.Graph(
                id='graph-1',
                figure={
                    'data': [
                        {
                            'x': [1, 2, 3],
                            'y': [3, 1, 2],
                            'type': 'bar'
                        },
                        {
                            'x': [1, 2, 3],
                            'y': [3, 10, 2],
                            'type': 'bar'
                        },
                    ]
                }
            )
        ],
        [
            html.Label('Scatter Chart'),
            dcc.Graph(
                id='graph-2',
                figure={
                    'data': [
                        {
                            'x': [1, 2, 3],
                            'y': [3, 1, 2],
                            'type': 'scatter',
                            'mode': 'markers',
                            'marker': {'size': 15}
                        },
                        {
                            'x': [1, 2, 3],
                            'y': [3, 10, 2],
                            'type': 'scatter',
                            'mode': 'markers',
                            'marker': {'size': 15}
                        }
                    ]
                }
            )
        ],
        [
            html.Label('Contour'),
            dcc.Graph(
                id='graph-3',
                figure={
                    'data': [
                        {
                            'z': [
                                [1, 2, 3],
                                [4, 2, 1],
                                [3, 1, 2]
                            ],
                            'type': 'contour',
                        },
                    ]
                }
            )
        ],
        [
            html.Label('Heatmap'),
            dcc.Graph(
                id='graph-4',
                figure={
                    'data': [
                        {
                            'z': [
                                [1, 2, 3],
                                [4, 2, 1],
                                [3, 1, 2]
                            ],
                            'type': 'heatmap',
                        },
                    ]
                }
            )
        ]

    ]


layout = html.Div(className='container', children=[
    html.Div([
        html.Hr(),
        html.Div(style={'columnCount': 2}, children=[
            html.Div(example, style={'minHeight': 65})
            for example in suite()
        ])
    ])
    for suite in [
        Dropdowns,
        Sliders,
        Graphs,
        # RangeSliders,
        DatePickerSingles,
        DatePickerRanges,
        TextInputs,
        Checkboxes,
        RadioItems,
        Buttons,
        Text,
        Tables
    ]
])
