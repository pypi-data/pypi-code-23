# author = sbermudel
# package description

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import gzip
import zlib
import bz2

DEFAULT_ENCODING='utf-8'

def DefaultCompressor():
    return NoCompressor()


## Metodo factory que crea un compresor
# @param type Tipo de compresion [Gzip, Zip, Bz2, None]
# @param compressLevel Nivel de compresion, valor comprendido entre 0 y 9
def CreateCompressor(type_compressor, compressLevel=9, encoding=DEFAULT_ENCODING):

    compressor = None

    if type_compressor.lower() == "gzip":
        compressor = GzipCompressor(compressLevel)
    elif type_compressor.lower() == "zip":
        compressor = ZipCompressor(compressLevel)
    elif type_compressor.lower() == "bz2":
        compressor = Bz2Compressor(compressLevel)
    elif type_compressor.lower() == "none":
        compressor = NoCompressor()
    else:
        compressor = DefaultCompressor()
    compressor.set_encoding(encoding)
    return compressor


def CreateCompressorFromConfig(config):
    '''
    Crea un compresor a partir de un diccionario
    '''
    level = 6
    if 'compressLevel' in config:
        level = int(config['compressLevel'])

    encoding = DEFAULT_ENCODING
    if 'encoding' in config:
        encoding = config['encoding']

    return CreateCompressor(config["type"], level, encoding)

## Clase que define los metodos basicos de un compresor en memoria
class Compressor:
    ## Crea una instacia de Compressor
    # @param compressLevel Nivel de compresion
    def __init__(self, compressLevel):
        self.__compressLevel = compressLevel
        self._encoding = DEFAULT_ENCODING

    ## Devuelve el nive de compresion del compressor
    @property
    def compressLevel(self):
        return self.__compressLevel

    def set_encoding(self, encondig):
        '''
        Establece el encoding del compresor
        '''
        self._encoding = encondig

    def get_encoding(self):
        '''
        Devuelve el encoding del compresor
        '''
        return self._encoding


    ## Comprime el buffer especificado
    def compress(self, buffer):
        return buffer

    ## Descomprime el buffer especificado
    def decompress(self, buffer):
        return buffer


## Implementacion de un no compresor
class NoCompressor(Compressor):
    ## Crea una instacia de NoCompressor
    def __init__(self):
        Compressor.__init__(self, None)

    ## Comprime el buffer especificado
    def compress(self, buffer):
        return bytes(buffer, self.get_encoding())

    ## Descomprime el buffer especificado
    def decompress(self, buffer):
        return str(buffer, self.get_encoding())

## Implemtacion de la compresion Gzip
class GzipCompressor(Compressor):
    ## Crea una instacia de GzipCompressor
    # @param compressLevel Nivel de compresion, debe ser un numero entero entre 1 y 9, por defecto 9
    def __init__(self, compressLevel=9):
        Compressor.__init__(self, compressLevel)

    def compress(self, buffer):
        return gzip.compress(bytes(buffer, self.get_encoding()))

    def decompress(self, buffer):
        return str(gzip.decompress(buffer), self.get_encoding())


## Implemtacion de la compresion Gzip
class ZipCompressor(Compressor):
    ## Crea una instacia de ZipCompressor
    # @param compressLevel Nivel de compresion, debe ser un numero entero entre 0 y 9, por defecto 6
    def __init__(self, compressLevel=6):
        Compressor.__init__(self, compressLevel)

    def compress(self, buffer):
        return zlib.compress(bytes(buffer, self.get_encoding()), level=self.compressLevel)

    def decompress(self, buffer):
        return str(zlib.decompress(buffer), self.get_encoding())


## Implementacion de la compresion en BZ2
class Bz2Compressor(Compressor):
    ## Crea una instacia de Bz2Compressor
    # @param compressLevel Nivel de compresion, debe ser un numero entero entre 1 y 9, por defecto 9
    def __init__(self, compressLevel=9):
        Compressor.__init__(self, compressLevel=compressLevel)

    def compress(self, buffer):
        return bz2.compress(bytes(buffer, self.get_encoding()), compresslevel=self.compressLevel)

    def decompress(self, buffer):
        return str(bz2.decompress(buffer), self.get_encoding())
