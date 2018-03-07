# Builtins
import os
import json
from collections import defaultdict
from collections import Counter


class CrowdflowerResults(object):
	"""
	Reads in and represents crowdflower results stored in json files located at 
	``paths``.  ``paths`` can be a single json filename or multiple filenames.
	This class is list-like (it wraps a list of rows found in the original
	results sets, and exposes the methods of that list).

	When multiple filenames are given, the results from these files are merged.
	Rows in these results that yield the same value when passed into
	``merge_key`` are considered to hold data about the same question, and will
	be merged into a single row in the final representation.  

	By default gold rows are excluded.  use ``exclude_gold=False`` to include
	gold rows.
	
	Access rows by indexing into the CrowdflowerResults object as if it were a
	list.  Each item is a row, similar to what appears in the original results
	file, but augmented with a few additional keys:

		``count``: contains a counter that indicates how many times each
			response was given for every field in the question.

		``fraction``: contains a dictionary that indicates what proportion of
			times each response was given for every field in the question.

		``mode``: contains a dictionary that indicates the most common response
			for each field in the question.  If multiple responses are tied,
			then they are all listed.  For consistency, when one response is
			most common, it is still presented as a length-1 list.

	You can also access rows based on a dictionary structure, using the id they 
	return when passed into ``merge_key``, by using the CrowdflowerResult.dict
	attribute.
	"""

	def __init__(
		self,
		paths,
		merge_key=None,
		exclude_gold=True
	):
		results = read_results(paths, merge_key)
		self.augmented_results = augment_results(results, exclude_gold)

		if merge_key is not None:
			self.dict = { merge_key(row):row for row in self.augmented_results}

	def __getattr__(self, attr):
		return getattr(self.augmented_results, attr)

	def __getitem__(self, key):
		return self.augmented_results.__getitem__(key)

	def __iter__(self):
		return iter(self.augmented_results)

	def __len__(self):
		return len(self.augmented_results)



def read_augmented_results(
	paths, exclude_gold=True, question_id_key='question_id'
):
	"""
	Read in crowdflower results stored in json files at locations specified by
	paths.  paths may either be a single path or iterable of paths, in which
	case results for multiple tasks will be merged.  

	Merging results is accomplished by considering two rows from different
	results files as corresponding to the same question if they have the same
	id, which is a value located in the data row defining the question in the
	column designated by "question_id_key".

	After merging results, augment them, by computing the number of votes for
	each answer in each question, computing the fraction of votes for each
	answer, and computing the most common response.
	"""
	if isinstance(paths, basestring):
		paths = [paths]

	return augment_results(read_results(paths), exclude_gold)


def merge_results(result_sets, merge_key):
	"""
	Merges the result_sets listed in ``result_sets``.  Two rows are considered
	to correspond to the same question if they return the same value when
	passed into ``merge_key``.
	"""

	# If there are no results, return an empty list
	if len(result_sets)<1:
		return []

	# If there are less than two results, then there's no merging to do, just
	# return the single result set
	if len(result_sets) < 2:
		return result_sets[0]

	# We'll use a dictionary structure to merge results having the same
	# question id.  After merging, we'll convert back to a list.  To merge
	# results, all we do is append judgments.  Note that this invalidates the
	# aggregate statistics that the crowdflower platform inserts into results,
	# which are therefore removed, and aren't very useful anyway.
	merged = {}
	invalid_fields = [
		'agreement', 'created_at', 'updated_at', 'state', 
		'gold_pool', 
	]

	for result_set in result_sets:
		for result in result_set:
			question_id = merge_key(result)

			# If this question id is already in the merged results, all we want
			# to do is add the judgments from this result for that question
			if question_id in merged:

				merged_q = merged[question_id]

				# Add this result's judgments to the merged judgments for this
				# question
				merged_judgments = merged_q['results']['judgments']
				add_judgments = result['results']['judgments']
				merged_judgments.extend(add_judgments)

				# Increment counters associated to this question accordingly
				merged_q['judgments_count'] += result['judgments_count']
				merged_q['missed_count'] += result['missed_count']

				# Normally each row has a crowd-flower assigned id, and it also
				# records the job id it's from.  We'll aggregate the
				# CF-assigned ids and the ids of the jobs in which this
				# question appeared
				merged_q['id'].append(result['id'])
				merged_q['job_id'].append(result['job_id'])


			# If this question is not already in the merged results, then we'll
			# add it.  We need to remove certain fields that won't be valid
			# after merging has taken place.
			else:

				# Delete the invalid fields
				for invalid_field in invalid_fields:
					del result[invalid_field]

				# Delete aggregated responses, keep only individual judgments
				for aggregate_result_field in result['results'].keys():
					if aggregate_result_field != 'judgments':
						del result['results'][aggregate_result_field]

				# Convert certain fields to lists, so the values from different
				# result-sets can be accumulated
				result['id'] = [result['id']]
				result['job_id'] = [result['job_id']]

				# Add to the merged results
				merged[question_id] = result

	# Now that we've merged the results, we don't need them in dictionary form.
	# Restore to list form for consistency with non-merged result sets.
	return merged.values()



def read_results(paths, merge_key=None):
	"""
	Read crowdflower results json file(s) located at paths.

	paths can be a single path or iterable of paths.  If an iterable of paths
	is supplied, then the results from multiple files will be merged.  
	
	Rows from different files are considered to be about the same question
	if the same value is returned when ``merge_key`` is called on those rows.

	If only a single path is given, then no merging is actually done, and
	``merge_key`` will never be called.
	"""

	# Handle the fact that a single path may be provided, rather than an
	# iterable of paths.
	if isinstance(paths, basestring):
		paths = [paths]

	# Read results form each file and merge them
	result_sets = []
	for path in paths:
		result_sets.append([json.loads(l) for l in open(path)])

	# If a method for assigning id's to rows is provided, then rows having the
	# same id will be merged, accumulating judgments for both
	if merge_key is not None:
		return merge_results(result_sets, merge_key)

	# Otherwise, all the rows from all results sets are returned without any
	# attempt to merge rows that pertain to the same question.
	return sum(result_sets, [])



def augment_results(results, exclude_gold = True):
	"""
	Augments CrowdFlower results by adding a few more keys to each row 
	(i.e. results to each question), which
	help summarize the results obtained.

	Each row corresponds to a single question, normally shown to multiple
	annotators.  Each question has multiple "fields" corresponding to each
	of the different CML inputs that annotators fill out for a given question.

	Because multiple annotators answer a single question, we get multiple
	answers for each field in each question.  This summarises the results, by
	providing counts for the number of times each answer is seen, the fraction
	of times each answer is seen, and the most common answer(s).

	These are directly added to the results object, thus they cause a side
	effect.  The modified results object is also returned.  The following keys
	are added to each row of the results object:

		row['counts']
			A dictionary whose keys are the names of the fields in the
			questions, and whose values are counters indicating how many times
			each response value is seen for the field.

		row['fractions']
			A dictionary whose keys are the names of the fields, and whose
			values are dictionaries that indicate the fraction of times
			different responses were seen for that field.

		row['mode']
			A dictionary whose keys are the names of the fields, and whose
			values are a list of the most common response(s) for that field.
			More than one value appears in the list when more than one response
			is tied as "most common".

	Additionally, when exclude gold is True, the gold rows are deleted from the
	results.
	"""

	# For each question, record how many votes were cast for each quote
	# as being the most / least verifiable.  Also record the attribution
	# ids for the quotes.
	augmented_results = []
	for result in results:

		# Ignore test questions
		if '_golden' in result['data'] and exclude_gold:
			continue

		# Accumulate information in this reportable result entry
		counts = defaultdict(Counter)
		mode = {}
		fraction = defaultdict(dict)

		# Count each type of response for each field
		for judgment in result['results']['judgments']:
			for field, val in judgment['data'].items():
				counts[field][val] += 1

		# Having accumulated the counts for each value for each field, use that
		# to calculate the mode value and the fraction of times each value is
		# given for each field
		for field in counts:

			# Figure out the mode value for this field.  Actually we
			# return a list of mode values, because more than one
			# value can tie as the most common value
			pointer = 0
			mode[field] = []
			sorted_counts = counts[field].most_common()
			while (
				pointer < len(sorted_counts) 
				and sorted_counts[pointer][1] == sorted_counts[0][1]
			):
				mode[field].append(sorted_counts[pointer][0])
				pointer += 1

			# Store the fraction of times a given answer is given for a field.
			# I.e. this is the same as counts, but is normalized to
			# sum to 1.
			total = float(sum(counts[field].values()))
			for val in counts[field]:
				fraction[field][val] = counts[field][val]/total

		# Put the counts, mode, and fraction onto the autmented result, and store
		# add that augmented result to the autmented results set.
		augmented_result = dict(result)
		augmented_result.update({
			'counts':counts, 'mode':mode, 'fraction':fraction})
		augmented_results.append(augmented_result)

	return augmented_results

