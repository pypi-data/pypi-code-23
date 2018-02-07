
from tramway.helper import *

def main():

	# data generation -> pandas.DataFrame data

	cells = tessellate(data, method='window', duration=2, shift=1, frames=True)
	# (optional) cells = tessellate(cells, method='kmeans', avg_location_count=5, knn=20)

	maps = infer(cells, mode='nontracking')

	# ...

