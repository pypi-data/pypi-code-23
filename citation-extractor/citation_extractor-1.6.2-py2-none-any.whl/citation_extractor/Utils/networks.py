# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

"""
TODO:

* pass a dictionary to the functions `create_*_graph` instead of a pd.DataFrame (refactoring)
* output logging information

"""

# node types declared as global
type_author = "aauthor"
type_work = "awork"
type_document = "document"
type_passage = "text_passage"
type_orphan_document = "document_nocit"

import json
import networkx as nx
import argparse
import sys
import pandas as pd
import glob
import os
from pyCTS import CTS_URN

def expand_scope(urn):
	"""
	this is applicable only URNs that are ranges
	and explodes only the last level of the scope
	returns a list of exploded URNs
	"""

	def scope_is_digits_only(urn):
		"""
		Check if a scope contains only digits
		"""
		checks = [y.isdigit() for x in split_passage(urn) for y in x]
		if(sum(checks)==len(checks)):
			# all digits
			return True
		else:
			return False
	def split_passage(urn):
		if(urn.is_range()):
			urn_start,urn_end = urn.passage_component.split('-')
			return (urn_start.split('.'),urn_end.split('.'))
		else:
			return (urn.passage_component.split('.'),)
	result = []
	scope = split_passage(urn)
	if(scope_is_digits_only(urn)):
		scope = [[int(level) for level in component] for component in scope]
		# check that only last component is different
		checks = [scope[0][n]==scope[1][n] for n in range(0,len(scope[0])-1)]
		if(sum(checks)==len(checks)):
			start,end=scope
			for value in range(start[len(start)-1],end[len(end)-1]):
			    new_scope = start[:len(start)-1]
			    new_scope.append(value)
			    print new_scope
			    result.append("%s:%s"%(urn.get_urn_without_passage(),".".join([str(x) for x in new_scope])))
		else:
			pass
	else:
		return None
	return result

def compute_shortest_path(graph):
	import networkx as nx
	ungraph = graph.to_undirected()
	shortest_paths = nx.all_pairs_shortest_path(ungraph,2)
	for source in shortest_paths.keys():
	    for target in shortest_paths[source].keys():
	        print >> sys.stderr, "from %s to %s via %i hops"%(source,target,len(shortest_paths[source][target]))
	result = {}
	for source in shortest_paths.keys():
	    result[source]= [target for target in shortest_paths[source].keys()]
	return result

def add_node(node_id,node_label,node_type,graph,node_content=None):
	graph.add_node(node_id,label=node_label,type=node_type)
	#graph.add_node(node_id,label=node_label,type=node_type,content=node_content)
	return graph

def add_edge(from_node_id,to_node_id,graph):
	if(not graph.has_edge(from_node_id,to_node_id)):
		graph.add_edge(from_node_id,to_node_id,value=1)
	else:
		data = graph.get_edge_data(from_node_id,to_node_id)
		graph.add_edge(from_node_id,to_node_id,value=data["value"]+1)
	return graph

def create_macro_graph(dataframe,all_doc_ids,doc_prefix,citations_only=False,output_orphan_nodes=False):
	"""

	What columns is the dataframe expected to have?


	TODO: implement orphan control (!)
	
	"""
	graph = nx.DiGraph()
	print >> sys.stderr, "Processing %i rows in the DataFrame"%len(dataframe)
	for idx,row in dataframe.iterrows():
		author_label = row["author_label"].decode('utf-8')
		author_urn = row["author_urn"]
		work_urn = row["work_urn"]
		citation_urn = row["cts_urn"]
		annotation_type = row["type"]
		doc_id = row["doc_id"]
		ann_id = row["ann_id"]
		doc_label = "%s-%s"%(doc_prefix,doc_id.replace('.txt',''))
		print >> sys.stderr, "[%s @ %s] Processing row %i/%i"%(doc_id,ann_id,idx+1,len(dataframe))
		if(citations_only == True and annotation_type!="scope"):
			print >> sys.stderr,"Type = %s, skipping"%annotation_type
		else:
			# add the citing document
			if(not doc_id in graph):
				graph = add_node(doc_id,doc_label,type_document,graph)
			# add the cited author
			if(author_urn not in graph):
				graph = add_node(author_urn,author_label,type_author,graph)
			# add the edge
			graph = add_edge(doc_id,author_urn,graph)
	# calculate the indegree and add to the graph
	for node in graph.nodes():
	    graph.node[node]["indegree"]=graph.in_degree(node)
	return graph

def create_meso_graph(dataframe,all_doc_ids,doc_prefix,citations_only=False,output_orphan_nodes=False):
	"""

	TODO: 
		* what it does?
		* when outputting label of `awork` node: concat title and author's name
	
	"""
	graph = nx.DiGraph()
	print >> sys.stderr, "Processing %i rows in the DataFrame"%len(dataframe)
	for idx,row in dataframe.iterrows():
		annotation_type = row["type"]
		ann_id = row["ann_id"]
		doc_id = row["doc_id"]
		print >> sys.stderr, "[%s @ %s] Processing row %i/%i"%(doc_id,ann_id,idx+1,len(dataframe))
		if(row["type"]=="awork" or row["type"]=="scope"):
			if(not pd.isnull(row["work_urn"]) and not pd.isnull(row["work_label"])):
				work_label = row["work_label"].decode('utf-8') # TODO: concatenate with author's name
				work_urn = row["work_urn"] 
				citation_urn = row["cts_urn"]
				doc_label = "%s-%s"%(doc_prefix,doc_id.replace('.txt',''))
				if(citations_only == True and annotation_type!="scope"):
					print >> sys.stderr,"Type = %s, skipping"%annotation_type
				else:
					# add the citing document
					if(not doc_id in graph):
						graph = add_node(doc_id,doc_label,type_document,graph)
					# add the cited author
					if(work_urn not in graph):
						graph = add_node(work_urn,work_label,type_work,graph)
					# add the edge
					graph = add_edge(doc_id,work_urn,graph)
			else:
				print >> sys.stderr,"Field `work_urn` or `work_label` are missing, skipping"	
		else:
			print >> sys.stderr,"Type = %s, skipping"%(annotation_type)
	# calculate the indegree and add to the graph
	for node in graph.nodes():
	    graph.node[node]["indegree"]=graph.in_degree(node)
	return graph

def create_micro_graph(dataframe,all_doc_ids,doc_prefix,output_orphan_nodes=False):
	"""

	TODO
	
	"""
	graph = nx.DiGraph()
	print >> sys.stderr, "Processing %i rows in the DataFrame"%len(dataframe)
	for idx,row in dataframe.iterrows():
		annotation_type = row["type"]
		ann_id = row["ann_id"]
		doc_id = row["doc_id"]
		print >> sys.stderr, "[%s @ %s] Processing row %i/%i"%(doc_id,ann_id,idx+1,len(dataframe))
		# at the micro level author- and work-level references are discared
		if(annotation_type=="scope"):
			if(not pd.isnull(row["work_urn"]) and not pd.isnull(row["work_label"])):
				work_label = row["work_label"].decode('utf-8')
				work_urn = row["work_urn"] 
				doc_label = "%s-%s"%(doc_prefix,doc_id.replace('.txt',''))
				citation_urn = row["cts_urn"]
				urn = CTS_URN(citation_urn)
				urns = []
				if(urn.is_range()):
					try:
						expanded_urns = [CTS_URN(x) for x in expand_scope(urn)]
						assert expanded_urns is not None
						urns = expanded_urns
					except Exception, e:
						urns = [urn]
				print >> sys.stderr,urns
				if(len(urns)>0):
					# add the citing document
					if(not doc_id in graph):
						graph = add_node(doc_id,doc_label,type_document,graph)
					# add the cited text passages
					for urn in urns:
						if(str(urn) not in graph):
							graph = add_node(str(urn),"%s: %s"%(work_label,urn.passage_component),type_passage,graph)
						# add the edge
						graph = add_edge(doc_id,str(urn),graph)
			else:
				print >> sys.stderr,"Field `work_urn` or `work_label` are missing, skipping (%s)"%row['cts_urn']
		else:
			print >> sys.stderr,"Type = %s, skipping"%(annotation_type)
	# calculate the indegree and add to the graph
	for node in graph.nodes():
	    graph.node[node]["indegree"]=graph.in_degree(node)
	return graph