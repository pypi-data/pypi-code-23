import plotly.offline as py
import plotly.figure_factory as ff


def scatter_matrix(df):
    fig = ff.create_scatterplotmatrix(df.dropna(), diag='box', height=1000, width=1900, colormap='Portland')
    py.plot(fig, filename='/tmp/scatter_matrix.html')
