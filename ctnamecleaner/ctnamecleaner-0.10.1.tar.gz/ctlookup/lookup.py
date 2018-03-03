""" Main module for CT Name Cleaner """

import pandas as pd
import os
import config

class Lookup:

    """ Lookup class for CT place names, or any other DF for that matter  """

    def __init__(self, raw_name_col="name",
                 clean_name_col="real.town.name",
                 csv_url=None,
                 use_inet_csv=False):

        """Constructor for Lookup 

        No need to use parameters unless you are specifying a different
        source URL.

        Parameters
        -----------
        raw_name_col : string, optional
            The name of the column with input names, like "New Preston"
        
            Only use if you're using a different source spreadsheet.

        clean_name_col : string, optional
            The name of the column with out names, like "Washington"

            Only use if you're using a different source spreadsheet.

        csv_url : string, optional
            A valid local file or remote url to use as an alternative
            source spreadsheet.

        use_inet_csv : boolean, optional
            Force a reload of the spreadsheet from the web to reflect any
            new additions since it was bundled with this python package.

            Defaults to False. The list doesn't change too much anymore.
        """
        
        self.internet_csv = config.SHEET_URL
        self.csv_url = csv_url
        if csv_url is not None:
            self.csv_url = csv_url
        elif use_inet_csv:
            self.csv_url = self.internet_csv
        else:
            self.csv_url = os.path.join(os.path.dirname(__file__), "data/ctnamecleaner.csv")

        self.lookup_table = pd.read_csv(self.csv_url)
        self.raw_name_col=raw_name_col
        self.clean_name_col = clean_name_col
        
    def clean(self, raw_name, error=None):

        """
        Get a clean place name (e.g. input "New Preston" and get
        "Washington")

        Parameters
        ----------
        raw_name : string
            The input name of the place, such as a village or a
            common misspelling of a town name

        error : obj, optional
            The default to return if no match is found

            Defaults to None

        Returns
        -------
        String or the value of None (or anything specified with the error
        parameter) if no match is found
    
        """
        
        results = self.lookup_table[self.lookup_table[self.raw_name_col]\
                                    .str.upper() == raw_name.upper()]
        if len(results.index) < 1:
            return error
            # raise Exception("LookupError: No results found")
        elif len(results.index) > 1:
            return error
            # raise Exception("LookupError: More than one result found")
        else:
            return results[self.clean_name_col].unique()[0]

    def clean_dataframe(self, df, town_col,error=None):

        """Clean an entire column of place names

        Parameters
        ----------

        df : Pandas DataFrame
            Dataframe containing to clean

        town_col : valid column label
            Label of column containing town names to clean

        error : obj, optional
            Default value to use when no match is found.
    
            Defaults to None

        Notes
        -----
        I plan to deprecate this but leave it in place for
        backward-compatibility. Use clean_col instead.

        """
        
        df = df.copy()
        df[town_col + "_CDF_UPPER"] = df.apply(lambda x: str(x[town_col]).upper(), axis=1)
        df = df.set_index(town_col + "_CDF_UPPER")
        lu = self.lookup_table
        lu = lu.set_index(self.raw_name_col)

        df =  df.join(lu,how="left")[self.clean_name_col].to_frame().reset_index()["real.town.name"]
        if error is not None:
            return df.fillna(error)
        return df


    def clean_col(self, series, error=None):
        """
        Clean a Pandas Series of place names

        Parameters
        ----------
        series : Pandas Series
            A series containing place names that need to be cleaned

        error : obj, optional
            Value to use if no match is found for a given place.

            Defaults to None

        Notes
        -----
        Meant as a less opinionated version of clean_dataframe

        """

        return series.apply(lambda x: self.clean(x, error=error))
