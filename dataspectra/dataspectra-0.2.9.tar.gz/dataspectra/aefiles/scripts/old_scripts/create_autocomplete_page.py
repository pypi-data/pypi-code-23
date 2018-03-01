#!/usr/bin/env python2.7

# [START] create_autocomplete_page()
def create_autocomplete_page():
    '''

    FUNCTION: Create autocomplete page. 

    #INPUT:
    - ../data/manipulated_data/temporary_gene_key_data.txt - Stores all the information for each possible input and the associated figures for that output.

    #OUTPUT:
    - ../www/js/gene_name_auto.js  - a file that outputs all of the javascript for autocomplete file.
    '''

    pass
    #Step 1: Read in input file.
    fileIN = open("tmp/search_lookup_file.txt")
    searchTerms = list()
    for i in fileIN:
        i =i.rstrip().split("\t")
        searchTerms.append(i[0])
    fileIN.close()

    searchTermUnique = list(set(searchTerms))


    fileOUT = open("web/js/gene_name_auto.js", "w")

    fileOUT.write("var allTerms = [")
    outTerms = ["{ value: \"" + x + "\"}" for x in searchTermUnique]
    fileOUT.write(", ".join(outTerms) + "]\n")
    fileOUT.close()
# [END] create_autocomplete_page()


