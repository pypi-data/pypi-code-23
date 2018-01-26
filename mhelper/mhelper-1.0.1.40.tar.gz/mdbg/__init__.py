def pl( target, find = None ):
    if find is not None:
        find = find.lower()
    
    for index, member in enumerate( dir( target ) ):
        if find is not None and find not in member.lower():
            continue
        
        print( "    [{}] {}".format( index, member ) )


def ps( sequence ):
    for index, item in enumerate( sequence ):
        print( "    [{}] {}".format( index, item ) )
