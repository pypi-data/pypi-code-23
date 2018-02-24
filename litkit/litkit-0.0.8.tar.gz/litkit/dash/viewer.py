import dash
import re

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import plotly


def __get_cv_columns(df):
    cols = list(df.columns)

    mean_fit_time = ['mean_fit_time']
    mean_score_time = ['mean_score_time']
    std_fit_time = ['std_fit_time']
    std_score_time = ['std_score_time']

    rs = [('mean_train_scores', 'mean_train_([a-zA-Z0-9]*)'),
          ('mean_test_scores', 'mean_test_([a-zA-Z0-9]*)'),
          ('rank_test_scores', 'rank_test_([a-zA-Z0-9]*)'),
          ('splits', 'split([0-9]*)_(test|train)_([_a-zA-Z0-]*)'),
          ('std_scores', 'std_(test|train)_([_a-zA-Z0-9]*)'),
          ('params', 'param_([a-zA-Z0-9]*)'), ]

    b = {}
    for k, r in rs:
        b[k] = [y.string for y in list(filter(None, (re.search(r, x) for x in cols)))]

    metrics = mean_fit_time + mean_score_time + std_fit_time + std_score_time + b['mean_train_scores'] + b['mean_test_scores'] + b['rank_test_scores'] + b['std_scores']

    params = b['params']

    return metrics, params


def __is_cv_results_df(df):
    if 'mean_fit_time' in list(df.columns) and 'mean_score_time' in list(df.columns) and 'std_fit_time' in list(df.columns) and 'std_score_time' in list(df.columns):
        return True

    return False


def __view_results_df(df: pd.DataFrame):
    app = dash.Dash()

    df.fillna('None', inplace=True)

    metrics, params = __get_cv_columns(df)

    df.rename(lambda x: x[6:] if x.startswith('param_') else x, axis='columns', inplace=True)
    params = [p[6:] for p in params]

    c_x = dcc.Checklist(
        options=[{'label': c, 'value': c} for c in params],
        values=params[:2],
        id='radio_x'
    )

    tb = dt.DataTable(
        rows=df.to_dict('records'),
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable'
    )

    t = dcc.Textarea(
        placeholder='',
        value='',
        style={'width': '100%'},
        id='query'
    )

    b = html.Button('Submit',
                    id='submit-query'
                    )

    app.layout = html.Div([
        html.Div([
            html.Div([
                html.H4('LitKit'),
            ], className="col-md-12"),
        ], className="row"),
        html.Div([
            html.Div([
                html.Label('X'),
                c_x,
            ], className="col-md-2"),
            html.Div([
                html.Div([
                    html.Div([
                        html.H5('Time'),
                    ], className="col-md-12"),
                ], className="row"),
                html.Div([
                    html.Div([html.Div([dcc.Graph(id=x)], className="col-md-3") for x in ['mean_fit_time', 'std_fit_time', 'mean_score_time', 'std_score_time']], className='row')
                ], className="row"),
                html.Div([
                    html.Div([
                        html.H5('Scores'),
                    ], className="col-md-12"),
                ], className="row"),
                html.Div([
                    html.Div([html.Div([dcc.Graph(id=x)], className="col-md-3") for x in ['mean_test_score', 'std_test_score', 'mean_train_score', 'std_train_score']], className='row')
                ], className="row"),
                html.Div([
                    html.Div([
                        html.H5('Rank'),
                    ], className="col-md-12"),
                ], className="row"),
                html.Div([
                    html.Div([html.Div([dcc.Graph(id=x)], className="col-md-3") for x in ['rank_test_score', ]], className='row')
                ], className="row"),
                html.Div([
                    html.Div([
                        html.H5('Query'),
                        t,
                        b,
                    ], className="col-md-12"),
                ], className="row"),
                html.Div([
                    html.Div([
                        html.Div([
                        ], id="editor"),
                    ], className="col-md-12", id="editor-p"),
                ], className="row"),
            ], className="col-md-10"),
        ], className="row"),
        html.Div([
            html.Div([
                tb,
            ], className="col-md-12"),
        ], className="row")
    ], className="container-fluid")

    @app.callback(
        Output('datatable', 'rows'),
        [
            Input('submit-query', 'n_clicks'),
        ],
        [
            State('query', 'value'),
        ]
    )
    def update_rows(_, query):
        try:
            rows = df.query(query).to_dict('records')
        except Exception as e:
            rows = df.to_dict('records')

        return rows

    for id in ['mean_fit_time', 'std_fit_time', 'mean_score_time', 'std_score_time', 'mean_test_score', 'std_test_score', 'mean_train_score', 'std_train_score', 'rank_test_score']:
        @app.callback(
            Output(id, 'figure'),
            [
                Input(id, 'id'),
                Input('datatable', 'rows'),
                Input('radio_x', 'values'),
            ])
        def update_figure(id, rows, x_cols):
            for i in range(len(rows)):
                for k in rows[i].keys():
                    if isinstance(rows[i][k], int):
                        rows[i][k] = float(rows[i][k])

            dff = pd.DataFrame(rows)

            fig = plotly.tools.make_subplots(rows=1, cols=1, )

            x_cols = sorted(x_cols)

            if len(x_cols) == 1:
                fig.append_trace({
                    'x': dff[x_cols[0]],
                    'y': dff[id],
                    'type': 'box',
                }, 1, 1)

                fig['layout']['xaxis'] = {'title': x_cols[0], }
                fig['layout']['yaxis'] = {'title': id, }

            if len(x_cols) == 2:
                fig.append_trace({
                    'z': dff[id],
                    'x': dff[x_cols[0]],
                    'y': dff[x_cols[1]],
                    'type': 'heatmap',
                }, 1, 1)

                fig['layout']['xaxis'] = {'title': x_cols[0], }
                fig['layout']['yaxis'] = {'title': x_cols[1], }
                fig['layout']['scene']['zaxis'] = {'title': id, }
                fig['layout']['scene']['xaxis'] = {'title': x_cols[0], }
                fig['layout']['scene']['yaxis'] = {'title': x_cols[1], }

            fig['layout']['showlegend'] = False

            fig['layout']['margin'] = {
                'l': 60,
                'r': 30,
                't': 30,
                'b': 100
            }

            return fig

    app.css.append_css({
        'external_url': 'https://codepen.io/21stio/pen/RQxLLg.css'
    })

    app.css.append_css({
        'external_url': 'https://unpkg.com/bootstrap@4.0.0-alpha.2/dist/css/bootstrap.min.css'
    })

    app.run_server(debug=True)


def __view_df(df):
    raise NotImplemented()


def view(df):
    if __is_cv_results_df(df):
        __view_results_df(df)
    else:
        __view_df(df)
