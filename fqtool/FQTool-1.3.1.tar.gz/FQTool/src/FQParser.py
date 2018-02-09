#!/usr/bin/env python3

## @file FQParser.py
## @brief Library to select parts of reads from FASTQ files based from the user's requests 
# The library consists in some functions to select a substring from a read taken from a FASTQ file.

from operator import itemgetter
import math

## @brief Main function
# This function returns a substring of the read if it respects the constraints passed as flags when calling FQTool.
# Otherwise, it returns None
# @param read Input read sequence
# @param phread Input phread values related to the read
# @param encoding_format represents the convention used to convert the phred value into char representation
# @param accuracy If the average probability of correctness of the read is below this value, the read is not analyzed
# @param quality_threshold Minimum probability (or phread value) of each base in the final substring
# @param length_threshold Minimum length of the substring to be returned.
#		If the actual length of the substring found after the trimming process is less than this value, the subsequence is rejected
# @return The function returns the substring found if it satisfies all the constrains, otherwise it returns None
def process_read(read, phread, encoding_format, accuracy, quality_threshold, length_threshold):
	if (quality_threshold <= 1 ):
		quality_threshold = covert_p_to_q(quality_threshold)
	if (sequence_accuracy(phread, encoding_format, quality_threshold) < accuracy):
		return None
	else:
		trimmed_indexes = trim_sequence(phread, encoding_format, quality_threshold)
		if (trimmed_indexes == None):
			return None
		if(trimmed_indexes[2] < length_threshold):
			return None
		else:
			return (read[trimmed_indexes[0] : trimmed_indexes[1]])


# @brief Compute the accuracy of the read
## This function calculates the accuracy index of the read
# @param phread_sequence Input phread values related to the read
# @param encoding_format Convention used to convert the phred value into char representation
# @param quality_threshold Minimum probability (or phread value) of each base in the final substring
# @return The function returns the accuracy index of the read
def sequence_accuracy(phread_sequence, encoding_format, quality_threshold):
	counter = 0
	if(encoding_format == "S" or encoding_format == "L"):
		for phread_element in phread_sequence:
			if(convert_S_L(phread_element) > quality_threshold):
				counter += 1
	else:
		for phread_element in phread_sequence:
			if(convert_X_I_J(phread_element) > quality_threshold):
				counter += 1
	return counter / len(phread_sequence)

## @brief Converts ASCII code of a phread character to the corresponding int value
## This function converts the ASCII code of a phread char to the corresponding int value.
# It can be used to convert phread values encoded with Sanger or Illumina 1.8+  standards
# @param ASCII_code The ASCII rappresentation of the phread value
# @return The function returns the int value of the char phread passed
def convert_S_L(ASCII_code):
	ASCII_value = ord(ASCII_code) - 33
	return ASCII_value

## @brief Converts the ASCII code of a phread char to the corresponding int value
## This function converts the ASCII code of a phread char to the corresponding int value
# It can be used to convert phread values encoded with Solexa or Illumina 1.3-1.8 standards
# @param ASCII_code The ASCII rappresentation of the phread value
# @return The function returns the int value of the char phread passed
def convert_X_I_J(ASCII_code):
	ASCII_value = ord(ASCII_code) - 64
	return ASCII_value

## @brief Trims the phread sequence
## This function trims the phread sequence.
# @param phread_sequence Input phread values related to the read
# @param encoding_format represent the convention used to convert the phred value into char representation
# @param quality_threshold Minimum probability(or phread value) of each base in the final substring
# @return The function returns a list of 3 ints if substring has been found: the start substring index, the end substring index and the length of the substring. Otherwise, it returns None
def trim_sequence(phread_sequence, encoding_format, quality_threshold):
    beginning = 0
    end = 0
    intervals = []
    if(encoding_format == "S" or encoding_format == "L"):
    	for i in range(0, len(phread_sequence)):
        	if convert_S_L(phread_sequence[i]) < quality_threshold:
        		if abs(end - beginning) == 0:
        			end = i + 1
        			beginning = i + 1
        		else:
        			intervals.append([beginning, end, abs(beginning - end)])
        			end = i + 1
        			beginning = i + 1
        	else:
        		end += 1
    else:
    	for i in range(0, len(phread_sequence)):
    		if convert_X_I_J(phread_sequence[i]) < quality_threshold:
    			if abs(end - beginning) == 0:
    				end = i + 1
    				beginning = i + 1
    			else:
    				intervals.append([beginning, end, abs(beginning - end)])
    				end = i + 1
    				beginning = i + 1
    		else:
    			end += 1
    if (intervals == []):
    	return [0, len(phread_sequence) - 1, len(phread_sequence)]
    return(list(sorted(intervals, key = itemgetter(2)))[-1])

## @brief Convert probability of correctness to quality
## This function converts a probability p (0 <= p <= 1) to an integer, the phread quality score
# @param probability Probability of correctness required
# @return quality The function returns the corresponding phread quality score 
def covert_p_to_q(probability):
	probability = 1 - probability
	return (int)(-10*math.log10(probability))
