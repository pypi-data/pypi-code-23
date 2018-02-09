##Start Here to Copy for your import module
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def bars(x, y):
    sns.set_style("darkgrid")
    colors = ['pink' if _y >=0 else 'red' for _y in y]
    fig, ax = plt.subplots()
    fig.set_size_inches(14,8)
    ax = sns.barplot(x, y, palette=colors)

    for n, (label, _y) in enumerate(zip(x, y)):
        ax.annotate(
            s='{:.1f}'.format(abs(_y)),
            xy=(n, _y),
            ha='center',va='center',
            xytext=(0,10),
            textcoords='offset points',
            weight='bold'
        )

        ax.annotate(
            s=label,
            xy=(n, 0),
            ha='center',va='center',
            xytext=(0,10),
            textcoords='offset points',
        )  
    # axes formatting
    #ax.set_yticks([])
    ax.set_xticks([])
    sns.despine(ax=ax, bottom=True, left=True)
##Stop Here to Copy for your import module
