'''
Description. Class NeEstimationTableFileManagerAsync
is motivated by GUI freezes when using class
NeEstimationTableFileManager.  
'''

from __future__ import print_function
from future import standard_library

standard_library.install_aliases()

__filename__ = "pgneestimationfilerunner.py"
__date__ = "20171203"
__author__ = "Ted Cosart<ted.cosart@umontana.edu>"

from agestrucne.pgguiutilities import PGGUIMessageWaitForResultsAndActionOnCancel
from agestrucne.pgneestimationtablefilemanager import NeEstimationTableFileManager
import multiprocessing

def call_async( dict_args ):
	'''
	This def requires as argument a dictionry with keys:items:
		"queue":a multiprocessing.Queue instance
		"instance":a NeEstimationTableFileManagerAsync instance
		"name":a name of a callable def in an NeEstimationTableFileManager object
		"args":a tuple giving, in signature order, args to the def given by "name"
	'''

	o_q=dict_args["queue"]
	o_instance=dict_args["instance"]
	s_name=dict_args["name"]
	tup_args=dict_args["args" ]

	o_parent=super( NeEstimationTableFileManagerAsync, o_instance )

	v_results= getattr( o_parent, s_name ) ( *tup_args )

	o_q.put( v_results )

	return True
#end call_async

class NeEstimationTableFileManagerAsync( NeEstimationTableFileManager ):

	def __init__( self, o_parent_frame,
					s_file_name, 
					i_header_is_first_n_lines=1,
					i_col_names_line_num=1,
					s_tsv_file_delimiter="\t" ):
		
		NeEstimationTableFileManager.__init__( self, 
				s_file_name=s_file_name,
				i_header_is_first_n_lines=i_header_is_first_n_lines,
				i_col_names_line_num=i_col_names_line_num,
				s_tsv_file_delimiter=s_tsv_file_delimiter )

		self.parentframe=o_parent_frame

		return
	#end __init__

	def __make_async_call_dict_of_args( self, 
									s_parent_def_name, 
									tup_args_for_call_to_parent_def ):
		dv_callargs={}
		dv_callargs[ "queue" ] = multiprocessing.Queue()
		dv_callargs[ "instance" ] = self
		dv_callargs[ "name" ] = s_parent_def_name
		dv_callargs[ "args" ] = tup_args_for_call_to_parent_def
		return dv_callargs
	#end __make_async_call_dict_of_args

	def __call_async_in_new_process( self, dv_callargs ):

		v_results=None

		o_process=multiprocessing.Process( target=call_async,
											args=( dv_callargs, ) )
		o_process.start()

		def cleanup():
			##### temp
			print( "-------------" )
			print( "in cleanup" )
			print( "----------" )
			#####

			dv_callargs[ "queue" ].close()
			o_process.terminate()
		#end cleanup

		PGGUIMessageWaitForResultsAndActionOnCancel( \
							o_parent=self.parentframe,
							s_message="Getting LDNe estimation info...",
							s_title="Loading File info",										
							def_boolean_signaling_finish=\
								lambda : not( dv_callargs["queue"].empty() ),
							def_on_cancel=cleanup )
	
		if o_process.is_alive() or not( dv_callargs[ "queue" ].empty() ):	
			##### temp
			print( "------------" )
			print( "in __call_async_in_new_process, process is alive." )
			print("------------" )
			#####
			v_results=dv_callargs[ "queue" ].get()
		#end if

		##### temp
		print( "---------------" )
		print( "in __call_async_in_new_process, returning value: " + str( v_results ) )
		print( "---------------" )
		#####

		return v_results
	#end __call_async_in_new_process

	def getGroupedDataLines( self, ls_group_by_column_names, 
										ls_data_column_names, 
										b_skip_header=True ):

		dv_callargs=self.__make_async_call_dict_of_args( \
					s_parent_def_name="getGroupedDataLines",
					tup_args_for_call_to_parent_def=\
											( ls_group_by_column_names,
												ls_data_column_names,
												b_skip_header ) )

		dlv_grouped_data=self.__call_async_in_new_process( dv_callargs )

		return dlv_grouped_data
	#end getGroupedDataLines

	def getDictDataLinesKeyedToColnames( self, ls_key_column_names, 
												ls_value_column_names,
												b_skip_header=False ):

		dv_callargs=self.__make_async_call_dict_of_args( \
					s_parent_def_name="getDictDataLinesKeyedToColnames",
					tup_args_for_call_to_parent_def=\
							( ls_key_column_names,
									ls_value_column_names,
									b_skip_header ) )

		df_data_keyed_to_colnames=self.__call_async_in_new_process( dv_callargs )

	
		return df_data_keyed_to_colnames
	#end getDictDataLinesKeyedToColnames
	
	def setFilter( self, s_column_name, def_filter ):
		dv_callargs=self.__make_async_call_dict_of_args( \
							s_parent_def_name="setFilter",
							tup_args_for_call_to_parent_def=\
									( s_column_name, def_filter ) )
		v_result=self.__call_async_in_new_process( dv_callargs )
		return v_result
	#end setFilter

	def unsetAllFilters( self ):
		dv_callargs=self.__make_async_call_dict_of_args( \
							s_parent_def_name="unsetAllFilters",
							tup_args_for_call_to_parent_def= () )
		v_result=self.__call_async_in_new_process( dv_callargs )

		return v_result
	#end unsetAllFilters

	def writeFilteredTable( self, o_fileobject ):
		dv_callargs=self.__make_async_call_dict_of_args( \
							s_parent_def_name="writeFilteredTable",
							tup_args_for_call_to_parent_def= ( o_fileobject, ) )
		v_result=self.__call_async_in_new_process( dv_callargs )

		return v_result
	#end writeFilteredTableToFile

	def getFilteredTableAsList( self, 
									ls_exclusive_inclusion_cols=None, 
									b_skip_header=False ):

		dv_callargs=self.__make_async_call_dict_of_args( \
							s_parent_def_name="getFilteredTableAsList",
							tup_args_for_call_to_parent_def=\
									( ls_exclusive_inclusion_cols, b_skip_header ) )

		ls_filtered_table=self.__call_async_in_new_process( dv_callargs )

		return ls_filtered_table
	#end getFilteredTableAsList


	def getUnfilteredTableAsList( self, 
							ls_exclusive_inclusion_cols=None, 
							b_skip_header=False ):

		dv_callargs=self.__make_async_call_dict_of_args( \
							s_parent_def_name="getUnfilteredTableAsList",
							tup_args_for_call_to_parent_def=\
									( ls_exclusive_inclusion_cols, b_skip_header ) )

		ls_unfiltered_table=self.__call_async_in_new_process( dv_callargs )

		return ls_unfiltered_table
	#end getFilteredTableAsList


	def getUniqueStringValuesForColumn( self, s_colname ):

		dv_callargs=self.__make_async_call_dict_of_args( \
							s_parent_def_name="getUniqueStringValuesForColumn",
							tup_args_for_call_to_parent_def=\
									( s_colname, ) )

		ls_column_values=self.__call_async_in_new_process( dv_callargs )
		return ls_column_values

	#end getUniqueStringValuesForColumn

	def getColumnNumberByName( self, s_column_name ):

		dv_callargs=self.__make_async_call_dict_of_args( \
							s_parent_def_name="getUniqueStringValuesForColumn",
							tup_args_for_call_to_parent_def=\
									( s_column_name, ) )

		i_column_num=self.__call_async_in_new_process( dv_callargs )

		return i_column_num
#end class NeEstimationTableFileManagerAsync

if __name__ == "__main__":
	pass
#end if main

