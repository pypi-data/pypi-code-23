"""Main script for generating output.csv."""
import pandas as pd 

def stat_avg(df):
    return (df['H'] / df['AB'])
    
def stat_obp(df):
    return ((df['H'] + df['BB'] + df['HBP']) / (df['AB'] + df['BB'] + df['HBP'] + df['SF']))

def stat_slg(df):
    return (df['TB'] / df['AB'])

def stat_ops(df):
    return (stat_obp(df) + stat_slg(df))

vs_Map = {'vs RHP': lambda df : df[df['PitcherSide'] == 'R'],
		'vs LHP': lambda df : df[df['PitcherSide'] == 'L'],
		'vs RHH': lambda df : df[df['HitterSide'] == 'R'],
		'vs LHH': lambda df : df[df['HitterSide'] == 'L'] }

def query_process(df, query):
	q = query.strip().split(',')  # query format = Stat,Subject,Split [0,1,2]

	#get split data and groupy by subject
	sums = vs_Map[q[2]](df).groupby(q[1]).sum()
	q_df = sums[sums.PA >=25]						# filter by PA

	# compute value for query stat
	if q[0] == 'AVG':
		value = pd.Series(stat_avg(q_df))
	elif q[0] == 'OBP':
		value = pd.Series(stat_obp(q_df))
	elif q[0] == 'SLG':
		value = pd.Series(stat_slg(q_df))
	else:
		value = pd.Series(stat_ops(q_df))

	# create dataframe by adding value and return
	ret = pd.DataFrame({'SubjectId' : q_df.index, 'Stat' : q[0], 'Subject' : q[1], 'Split' : q[2], 'Value' : value.round(3)},columns=['SubjectId', 'Stat', 'Split', 'Subject', 'Value'])
	ret = ret.reset_index(drop = True)
	return ret[['SubjectId', 'Stat', 'Split', 'Subject', 'Value']]




def main():
    # add basic program logic here
    #read data and combinations.
    pitch_data = pd.read_csv('./data/raw/pitchdata.csv')
    queries = open('./data/reference/combinations.txt').readlines()[1:]

    # create output dataframe format and read combinations to process
    output = pd.DataFrame(columns=['SubjectId', 'Stat', 'Split', 'Subject', 'Value'])
    for q in queries:
    	temp = query_process(pitch_data, q)
    	output = output.append(temp)

    
    # sort and write to csv
    output = output.sort_values(by = ['SubjectId', 'Stat', 'Split', 'Subject']) 
    output[['SubjectId', 'Stat', 'Split', 'Subject', 'Value']].to_csv('data/processed/output.csv',index = False)


if __name__ == '__main__':
    main()
