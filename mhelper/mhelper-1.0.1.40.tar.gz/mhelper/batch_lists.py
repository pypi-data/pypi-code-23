class BatchList:
    def __init__( self, data, batch_size ):
        self.batch = batch_size
        self.data = list( data )
    
    
    def take( self ):
        result = self.data[0:self.batch]
        del self.data[0:self.batch]
        return result
    
    
    def __bool__( self ):
        return bool( self.data )
    
    
    def __len__( self ):
        return len( self.data )
    
    
    def __iter__( self ):
        while self:
            yield self.take()


def divide_workload( index, count, quantity ):
    import warnings
    warnings.warn( "deprecated - array_helper.get_workload", DeprecationWarning )
    from mhelper import array_helper
    return array_helper.get_workload( index, quantity, count )
