from collections import OrderedDict
from os import path
from typing import Optional

from intermake.engine.environment import MENV


class RecentFilesList:
    """
    Quick management for a list of recent files.
    This is a trivial class and doesn't incur a memory overhead (the actual data is kept in the AutoStore) can be discarded after use.
    """
    
    def __init__( self ):
        """
        Constructor  
        """ 
        self.__store = MENV.local_data.store
        self.__key = "recent-files"
        self.recent = self.__store.retrieve( self.__key, OrderedDict ) #type: OrderedDict
        
    def __save(self):
        self.__store.commit( self.__key )
        
    def append(self, accession : str, file_name : str):
        if not isinstance(file_name, str):
            # Avoid disasters where the programmer passes in the file itself rather than the file-name.
            # We don't want to dump a whole file into the AutoStore.
            raise TypeError("RecentFilesList expected a string, but received a '{}': '{}'.".format(type(file_name).__name__, file_name))
        
        accession=  accession.lower()
            
        while accession in self.recent:
            del self.recent[ accession ]
            
        while file_name in self.recent.values():
            self.recent = { k:v for k, v in self.recent.items() if v != file_name }
            
        self.recent[accession] = file_name
        self.__save()
        
    def search(self, accession : str) -> Optional[str]:
        if not path.sep in accession:
            accession = accession.lower()
            
            file_name = self.recent.get(accession)
                
            if file_name is None:
                return accession
            else:
                return file_name
        else:        
            return accession
    
    def accessions(self):
        return self.recent.keys()
        
    def file_names(self):
        return self.recent.values()
    
    def items(self):
        return self.recent.items()
