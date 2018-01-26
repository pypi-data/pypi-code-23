import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class explore():
	# Show how category distribute (in percentage)
	def plot_percentage_category(df, row):
	    row_percentage = df[row].value_counts() / df.shape[0] * 100
	    row_percentage.plot(kind='bar', color = "#FD5C64", rot = 0)
	    plt.xlabel(row)
	    plt.ylabel("Percentage")
	    sns.despine()
	    plt.show()

	# For ploting categories vs Target variable
	def plot_categories(df , cat , target , **kwargs):
	    row = kwargs.get( 'row' , None )
	    col = kwargs.get( 'col' , None )
	    facet = sns.FacetGrid( df , row = row , col = col, size = 6)
	    facet.map( sns.barplot , cat , target )
	    facet.add_legend()

	# show how target variable vary with data (sorted)
	def plot_target_variable(df, target, figsize = (8,6)):
		plt.figure(figsize=figsize)
		plt.scatter(range(df.shape[0]), np.sort(df.target.values))
		plt.xlabel('index', fontsize=12)
		plt.ylabel('y', fontsize=12)
		plt.show()

	# useful function to plot the first 'k' count
	def plot_countplot(df, col, k):
		df[col].value_counts()[0:k].plot(kind="bar")

	# missing data
	def get_missing_data(data):
	    total = data.isnull().sum().sort_values(ascending=False)
	    percent = (data.isnull().sum()/data.isnull().count()).sort_values(ascending=False)
	    missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
	    return missing_data

	# null data
	def null_count(df):
	    nulls = pd.DataFrame(df.isnull().sum().sort_values(ascending=False)[:25])
	    nulls.columns = ['Null Count']
	    nulls.index.name = 'Feature'
	    return nulls

	# For classification problem
	def plot_distribution( df , var , target , **kwargs ):
	    row = kwargs.get( 'row' , None )
	    col = kwargs.get( 'col' , None )
	    facet = sns.FacetGrid( df , hue=target , aspect=4 , row = row , col = col )
	    facet.map( sns.kdeplot , var , shade= True )
	    facet.set( xlim=( 0 , df[ var ].max() ) )
	    facet.add_legend()

	# pivot table use to show how target value affect by categorical value 
	def plot_pivot_table(df, var, target):
	    condition_pivot = df.pivot_table(index=var,
	                                    values=target, aggfunc=np.median)
	    condition_pivot.plot(kind='bar', color='blue')
	    plt.xlabel(var)
	    plt.ylabel('Median ' + target)
	    plt.xticks(rotation=0)
	    plt.show()

	def plot_heatmap(df, k, col):
	    """
	    Arguments:
	    df -- input dataframe
	    k -- numbers of variables for heatmap
	    col -- target variable
	    Returns:
	    seaborn heatmap
	    """
	    numerical_features = df.select_dtypes(include=[np.number])
	    corr = numerical_features.corr()
	    cols = corr.nlargest(k, col)[col].index
	    _ , ax = plt.subplots( figsize =( 12 , 10 ) )
	    cmap = sns.diverging_palette( 250 , 15 , as_cmap = True )
	    cm = np.corrcoef(df[cols].values.T)
	#     plt.figure(figsize=(15,10))
	    sns.set(font_scale=1.25)
	    hm = sns.heatmap(
	                    cm,
	                    cmap = cmap,
	                    cbar=True, 
	                    annot=True, 
	                    square=True, 
	                    fmt='.2f',
	                    annot_kws={'fontsize': 12},
	                    xticklabels=cols.values,
	                    yticklabels=cols.values,
	                    ax = ax
	                    )
	    plt.show()