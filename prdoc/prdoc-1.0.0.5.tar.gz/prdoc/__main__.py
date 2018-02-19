import sys
from mhelper import file_helper, markdown_helper


__version__ = "1.0.0.5"


def main():
    if len( sys.argv ) < 2:
        print( "prdoc " + __version__, file = sys.stderr )
        print( "See readme.md for details.", file = sys.stderr )
        return 1
    
    file_name = sys.argv[1]
    
    text = file_helper.read_all_text( file_name )
    
    if not text:
        print( "File is missing or empty.", file = sys.stderr )
        return 2
    
    ansi = markdown_helper.markdown_to_ansi( text )
    
    print( ansi )
    return 0


if __name__ == "__main__":
    exit( main() )
