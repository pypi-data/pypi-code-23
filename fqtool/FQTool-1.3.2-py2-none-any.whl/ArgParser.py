## @file ArgParser.py
## @brief Small tool to parse the command line arguments for FQTool 

import argparse

## @brief This function creates a parser for command line arguments
# Sets up a parser that accepts the following flags: -i, -l, -q, -f, -a, -v, -h
# @return An already configured instance of the ArgumentParser class
def create_parser():
    parser = argparse.ArgumentParser(prog = 'FQTool', 
                                    description = 'FASTQ parser. Quickly get the reads you need.',
                                    epilog = 'That\'s all! Reach us at github.com/mistrello96/FQTool',
                                    add_help = False)
    parser.add_argument('-i', '--input-filenames', type = str, metavar = 'filename', dest = 'filenames', 
                        nargs = '+', help = 'Input file name(s). Usually in the form *.fastq, *.q', required = True)
    parser.add_argument('-l', '--length', type = int, metavar = 'length', dest = 'length', 
                        help = 'Minimum length of the reads to be extracted.', required = True)
    parser.add_argument('-q', '--probability-of-correctness', type = float, metavar = 'quality', 
                        dest = 'quality', required = True,
                        help = 'Minimum probabilty of correctness of the reads to be extracted. Ranges between 0 and 1. You can also write the Phread Quality Value directly (e.g. 35)')
    parser.add_argument('-f', '--ascii-conversion-function', type = str, metavar = 'function', 
                        dest = 'function', help = 'Function to be used to switch bewteen ASCII and Phred Value.' + 
                        'Choose between: S = Sanger, X = Solexa, I = Illumina 1.3+, J = Illumina 1.5+, L = Illumina 1.8+. Default = L', 
                        choices = ['S', 'X', 'I', 'J', 'L'], default = 'L')
    parser.add_argument('-a', '--accuracy', type = float, metavar = 'accuracy', dest = 'accuracy', 
                        help = 'The average probability of correctness of the reads must be *at least* this value. If it is not, the read will be ignored. Default = 0',
                        default = 0)
    parser.add_argument('-v', '--version', action = 'version', help = 'Shows the program version and exits', version = '%(prog)s 1.3')
    parser.add_argument('-h', '--help', action = 'help', help = 'List of the flags you can use with FQTool')
    
    return parser