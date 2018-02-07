from __future__ import print_function, unicode_literals
"""
Basic parsing of records (usually a line from a file).
Records can either be delimited (like common .CSV files),
or fixed width (each field has preset start and end values)

Each record is made up of fields. A record definition lists the fields and types of each that make up the record.

The fields must be given as a list of tuples ( name, field type ) to ensure
the order of the fields is not lost.
"""
import ctxlogger

from . import ParseException


def parse_delimited_record( record, delimiter = ',', quote = '"' ):
    fields = []
    endquote = quote + delimiter # how a quoted field ends

    while True: # keep going until we can't split the record any more

        try: # try and pull the first field off the string
            field, record = record.strip().split( delimiter, 1 )
        except ValueError:
            # couldn't split, so we're done
            # add everything left as the last field
            # and return all the fields we've found
            fields.append(record)
            return fields

        if not field.startswith( quote ):
            fields.append( field )
            continue

        field = field[1:] # skip the starting quote character

        # do we end with the quote character too? If so, nothing to be done
        if field.endswith( quote ):
            fields.append( field[:-1] )
            continue

        # so we've split on a delimiter in a quoted field
        # there should be another quote character followed by the
        # usual delimiter somewhere further along in the line
        # or just the end of line
        try:
            quotedfield, record = record.split( endquote, 1 )
        except ValueError:
            if record.endswith( quote ): # end of line
                fields.append(
                    '{}{}{}'.format( field, delimiter, record[:-1] )
                )
                return fields

            # ERROR: No matching end quote
            ctxlogger.exception(
                ParseException,
                'Quoted field with no matching end'
            )

        fields.append( '{}{}{}'.format( field, delimiter, quotedfield ) )

def unparse_delimited_record( fields, delimiter = ',', quote = '"', always_quote = False ):
    quoted_fields = []
    for field in fields:
        if always_quote or ( delimiter in str(field) ):
            quoted_fields.append(
                '{quote}{field}{quote}'.format( quote = quote, field = field )
            )
        else:
            quoted_fields.append( field )
    return delimiter.join( quoted_fields )

## Given an argument list of field name, field definition tuples,
## this class can parse and unparse a delimited record into or from a dict.
##
## eg.
##
## delimited_record(
##    ( 'order', string_field() ),
##    ( 'amount', decimal_field() ),
##    ( 'quantity', int_field() ) ),
## )

class delimited_record( object ):

    def __init__( self, *args, **kwargs ):
        self.fields = args

        # have to get kwargs this way as they need to be defined
        # after the *args (the list of records)
        # otherwise keyword args not used would steal from the
        # record definitions
        self.delimiter = kwargs.get( 'delimiter', ',' )
        self.quote = kwargs.get( 'quote', '"' )
        self.always_quote = kwargs.get( 'always_quote', False )

    def parse( self, record ):
        raw_values = parse_delimited_record(
            record, self.delimiter, self.quote
        )
        if len(raw_values) < len(self.fields):
            for name, field in self.fields[ len(raw_values): ]:
                with ctxlogger.context( 'field', name ):
                    if field.flags.get( 'required', True ):
                        ctxlogger.exception(
                            ParseException,
                            'Missing field in data'
                        )

        untyped = zip(
            [ f[0] for f in self.fields ],
            [ f[1] for f in self.fields ],
            raw_values
        )

        typed = {}
        for n, p, v in untyped:
            with ctxlogger.context( 'field', n ):
                typed[ n ] = p.parse( v )

        return typed

    def unparse( self, data ):
        values = []
        for n, p in self.fields:
            with ctxlogger.context( 'field', n ):
                try:
                    values.append( p.unparse( data[ n ] ) )
                except KeyError:
                    ctxlogger.exception(
                        ParseException,
                        'Missing field in data'
                    )

        return unparse_delimited_record(
            values,
            self.delimiter,
            self.quote,
            self.always_quote,
        )

    def as_header( self ):
        return unparse_delimited_record(
            [ f[0] for f in self.fields ],
            self.delimiter,
            self.quote
        )

## Given a list of field name, field definition tuples, this class can
## parse and unparse a fixed width record. Each field definition needs
## to specify the start and end positions of the field within the record.
##
## eg.
##
## fixedwidth_record(
##     ( 'order', string_field( 0, 8 ) ),
##     ( 'amount', decimal_field( 8, 14 ) ),
##     ( 'quantity', int_field( 14, 17 ) ),
## )

class fixedwidth_record( object ):

    def __init__( self, *args ):
        self.fields = args

    def parse( self, record ):
        parsed = {}
        for n, p in self.fields:
            with ctxlogger.context( 'field', n ):
                parsed[ n ] =  p.parse( record )

        return parsed

    def unparse( self, data ):
        record = ''
        for n, p in self.fields:
            with ctxlogger.context( 'field', n ):
                try:
                    record += p.unparse( data[n] )
                except KeyError:
                    ctxlogger.exception(
                        ParseException,
                        'Missing field in data'
                    )

        return record

    def as_header( self ):
        # not sure this is possible in any sane fashion
        raise NotImplemented
