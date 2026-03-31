import struct
import time
from base import Compressor
from bwt import BlockBWT
from rle import RLECompressor
from mtf import MTFTransform


class BWTRLECompressor(Compressor):
    
    def __init__(self, block_size: int = 900000):
        super().__init__("BWT+RLE")
        self.bwt = BlockBWT(block_size)
        self.rle = RLECompressor(1, 1)

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        
        # Применяем BWT
        blocks, indices = self.bwt.forward(data)
        
        # Сериализуем с RLE компрессией каждого блока
        result = bytearray(struct.pack('>I', len(blocks)))
        for block, idx in zip(blocks, indices):
            result.extend(struct.pack('>I', idx))
            compressed_block = self.rle.encode(block)
            result.extend(struct.pack('>I', len(compressed_block)))
            result.extend(compressed_block)
        
        self.encode_time = time.time() - start
        self.compressed_size = len(result)
        return bytes(result)

    def decompress(self, data: bytes) -> bytes:
        start = time.time()
        pos = 0
        
        block_count = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        blocks = []
        indices = []
        
        for _ in range(block_count):
            idx = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4
            comp_size = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4
            compressed_block = data[pos:pos+comp_size]
            pos += comp_size
            decompressed = self.rle.decode(compressed_block)
            blocks.append(decompressed)
            indices.append(idx)
        
        result = self.bwt.inverse(blocks, indices)
        self.decode_time = time.time() - start
        return result


class BWTMTFRLECompressor(Compressor):
    
    def __init__(self, block_size: int = 900000):
        super().__init__("BWT+MTF+RLE")
        self.bwt = BlockBWT(block_size)
        self.rle = RLECompressor(1, 1)

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        
        # Применяем BWT
        blocks, indices = self.bwt.forward(data)
        
        # Сериализуем с MTF+RLE компрессией каждого блока
        result = bytearray(struct.pack('>I', len(blocks)))
        for block, idx in zip(blocks, indices):
            result.extend(struct.pack('>I', idx))
            
            # MTF трансформация
            mtf_block = MTFTransform.encode(block)
            # RLE компрессия
            compressed_block = self.rle.encode(mtf_block)
            
            result.extend(struct.pack('>I', len(compressed_block)))
            result.extend(compressed_block)
        
        self.encode_time = time.time() - start
        self.compressed_size = len(result)
        return bytes(result)

    def decompress(self, data: bytes) -> bytes:
        start = time.time()
        pos = 0
        
        block_count = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        blocks = []
        indices = []
        
        for _ in range(block_count):
            idx = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4
            comp_size = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4
            compressed_block = data[pos:pos+comp_size]
            pos += comp_size
            
            # RLE декомпрессия
            rle_decoded = self.rle.decode(compressed_block)
            # MTF обратное преобразование
            decompressed = MTFTransform.decode(rle_decoded)
            
            blocks.append(decompressed)
            indices.append(idx)
        
        result = self.bwt.inverse(blocks, indices)
        self.decode_time = time.time() - start
        return result


def chain_compress(data: bytes, *compressors) -> bytes:
    """
    Цепная компрессия - применяет несколько компрессоров по очереди.
    
    Пример:
        result = chain_compress(data, rle_comp, huffman_comp)
    """
    result = data
    for comp in compressors:
        result = comp.compress(result)
    return result


def chain_decompress(data: bytes, *compressors_reversed) -> bytes:
    """
    Цепная декомпрессия - применяет компрессоры в обратном порядке.
    
    Пример:
        result = chain_decompress(data, huffman_comp, rle_comp)
    """
    result = data
    for comp in reversed(compressors_reversed):
        result = comp.decompress(result)
    return result
