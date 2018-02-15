# author = sbermudel
# package description

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import gzip
import zlib
import bz2


def DefaultCompressor():
    return NoCompressor()


## Metodo factory que crea un compresor
# @param type Tipo de compresion [Gzip, Zip, Bz2, None]
# @param compressLevel Nivel de compresion, valor comprendido entre 0 y 9
def CreateCompressor(type, compressLevel=9):
    if type.lower() == "gzip":
        return GzipCompressor(compressLevel)
    elif type.lower() == "zip":
        return ZipCompressor(compressLevel)
    elif type.lower() == "bz2":
        return Bz2Compressor(compressLevel)
    elif type.lower() == "none":
        return NoCompressor()
    else:
        return DefaultCompressor()


def CreateCompressorFromConfig(config):
    level = config.get("compressLevel")
    if level is None:
        return CreateCompressor(config["type"])
    else:
        return CreateCompressor(config["type"], int(level))


## Clase que define los metodos basicos de un compresor en memoria
class Compressor:
    ## Crea una instacia de Compressor
    # @param compressLevel Nivel de compresion
    def __init__(self, compressLevel):
        self.__compressLevel = compressLevel

    ## Devuelve el nive de compresion del compressor
    @property
    def compressLevel(self):
        return self.__compressLevel

    ## Comprime el buffer especificado
    def compress(self, buffer, econding='utf-8'):
        return buffer

    ## Descomprime el buffer especificado
    def decompress(self, buffer, econding='utf-8'):
        return buffer


## Implementacion de un no compresor
class NoCompressor(Compressor):
    ## Crea una instacia de NoCompressor
    def __init__(self):
        Compressor.__init__(self, None)


## Implemtacion de la compresion Gzip
class GzipCompressor(Compressor):
    ## Crea una instacia de GzipCompressor
    # @param compressLevel Nivel de compresion, debe ser un numero entero entre 1 y 9, por defecto 9
    def __init__(self, compressLevel=9):
        Compressor.__init__(self, compressLevel)

    def compress(self, buffer, econding='utf-8'):
        return gzip.compress(bytes(buffer, econding))

    def decompress(self, buffer, econding='utf-8'):
        return str(gzip.decompress(buffer), econding)


## Implemtacion de la compresion Gzip
class ZipCompressor(Compressor):
    ## Crea una instacia de ZipCompressor
    # @param compressLevel Nivel de compresion, debe ser un numero entero entre 0 y 9, por defecto 6
    def __init__(self, compressLevel=6):
        Compressor.__init__(self, compressLevel)

    def compress(self, buffer, econding='utf-8'):
        return zlib.compress(bytes(buffer, econding), level=self.compressLevel)

    def decompress(self, buffer, econding='utf-8'):
        return str(zlib.decompress(buffer), econding)


## Implementacion de la compresion en BZ2
class Bz2Compressor(Compressor):
    ## Crea una instacia de Bz2Compressor
    # @param compressLevel Nivel de compresion, debe ser un numero entero entre 1 y 9, por defecto 9
    def __init__(self, compressLevel=9):
        Compressor.__init__(self, compressLevel=compressLevel)

    def compress(self, buffer, econding='utf-8'):
        return bz2.compress(bytes(buffer, econding), compresslevel=self.compressLevel)

    def decompress(self, buffer, econding='utf-8'):
        return str(bz2.decompress(buffer), econding)
