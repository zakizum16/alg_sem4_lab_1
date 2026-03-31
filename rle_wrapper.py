"""
RLE компрессор в формате Compressor
"""
import time
from rle import RLECompressor
from base import Compressor


class RLECompressorWrapper(Compressor):
    """Обёртка RLE в формате Compressor"""
    
    def __init__(self, Ms: int = 1, Mc: int = 1):
        super().__init__(f"RLE(Ms={Ms},Mc={Mc})")
        self.compressor = RLECompressor(Ms, Mc)

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        compressed = self.compressor.encode(data)
        self.encode_time = time.time() - start
        self.compressed_size = len(compressed)
        return compressed

    def decompress(self, data: bytes) -> bytes:
        start = time.time()
        decompressed = self.compressor.decode(data)
        self.decode_time = time.time() - start
        return decompressed
