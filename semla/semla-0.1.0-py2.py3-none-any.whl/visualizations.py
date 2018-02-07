import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_features_distributions(df: pd.DataFrame, target_column: str, bins=20, remove_outliers=True):
    """
    Plots the histogram of every feature per the target column
    :param df:
    :param target_column: name of the column to split the plots on. tested on binary not sure if it works with more
    :param bins: number of bins for the histograms #todo support dictionary for each feature a different histogram
    :param remove_outliers:
    :return:
    """
    columns = sorted(col for col in df.columns if col != target_column)
    width = 2  # int(np.sqrt(len(columns)))
    height = np.ceil(len(columns) / width)
    with plt.rc_context(rc={'figure.figsize': (10, 25)}):
        fig = plt.figure()
        for col_i, col in enumerate(columns):
            fig.add_subplot(height, width, col_i + 1)
            if remove_outliers:
                value_range = (df[col].quantile(.01), df[col].quantile(.99))
            else:
                value_range = (df[col].min(), df[col].max())
            # TODO find a way get a good bin numbers check brute force plotter
            df.groupby(target_column)[col].plot.hist(alpha=0.5, normed=True, bins=bins, range=value_range)
            plt.title("Feature '{}'".format(col), fontdict=dict(fontsize=10))
    plt.tight_layout()
    return fig


def plot_correlation_coeffecients(df: pd.DataFrame, target_feature: str, features: list = None):
    """

    :param df:
    :param target_feature:
    :param features:
    :return:
    """
    # graphique: plotting correlations with target_feature
    if features is None:
        features = []
    label = []
    value = []
    for col in features:
        label.append(col)
        value.append(np.corrcoef(df[col].values, df[target_feature].values)[0, 1])
    ind = np.arange(len(label))
    width = 0.
    fig, ax = plt.subplots(figsize=(8, 20))  # create a frame
    rects = ax.barh(ind, np.array(value), color='red')
    ax.set_yticks(ind + ((width) / 2.))
    ax.set_yticklabels(label, rotation='horizontal')
    ax.set_xlabel("Correlation coefficient")
    ax.set_title(f"Correlation Coefficient with {target_feature}")


def correlation_matrix(df, features):
    corr_matrix = df[features].corr()
    plt.figure(figsize=(12, 12))
    sns.heatmap(corr_matrix, vmax=.8, linewidths=0.01, square=True, cmap='viridis', linecolor='white')
    plt.title('Correlation between features')
    # correlations between features among each other

    threshold = 0.5
    important_corrs = (corr_matrix[abs(corr_matrix) > threshold][corr_matrix != 1.]).unstack().dropna().to_dict()
    unique_important_corrs = pd.DataFrame(
        list(set([(tuple(sorted(key)), important_corrs[key]) for key in important_corrs])),
        columns=['Attribute Pair', 'Correlations'])
    unique_important_corrs = unique_important_corrs.ix[abs(unique_important_corrs['Correlations']).argsort()[::-1]]
    print(unique_important_corrs)
