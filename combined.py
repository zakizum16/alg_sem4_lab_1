import struct
import time
from base import Compressor
from bwt import BlockBWT
from rle import RLECompressor
from mtf import MTFTransform
from huffman import HuffmanCompressor
from lz import LZSSCompressor, LZWCompressor


class BWTRLECompressor(Compressor):
    
    def __init__(self, block_size: int = 900000):
        super().__init__("BWT+RLE")
        self.bwt = BlockBWT(block_size)
        self.rle = RLECompressor(1, 1)

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        
        blocks, indices = self.bwt.forward(data)
        
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
        self.mtf = MTFTransform()
        self.rle = RLECompressor(1, 1)

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        
        blocks, indices = self.bwt.forward(data)
        
        result = bytearray(struct.pack('>I', len(blocks)))
        for block, idx in zip(blocks, indices):
            result.extend(struct.pack('>I', idx))
            
            mtf_block = self.mtf.encode(block)
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
            
            rle_decoded = self.rle.decode(compressed_block)
            decompressed = MTFTransform.decode(rle_decoded)
            
            blocks.append(decompressed)
            indices.append(idx)
        
        result = self.bwt.inverse(blocks, indices)
        self.decode_time = time.time() - start
        return result


class BWTMTFHACompressor(Compressor):
    
    def __init__(self, block_size: int = 900000):
        super().__init__("BWT+MTF+HA")
        self.bwt = BlockBWT(block_size)
        self.mtf = MTFTransform()
        self.huffman = HuffmanCompressor()

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        
        blocks, indices = self.bwt.forward(data)
        
        result = bytearray(struct.pack('>I', len(blocks)))
        for block, idx in zip(blocks, indices):
            result.extend(struct.pack('>I', idx))
            
            mtf_block = self.mtf.encode(block)
            huffman_block = self.huffman.compress(mtf_block)
            
            result.extend(struct.pack('>I', len(huffman_block)))
            result.extend(huffman_block)
        
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
            huffman_block = data[pos:pos+comp_size]
            pos += comp_size
            
            mtf_decoded = self.huffman.decompress(huffman_block)
            decompressed = self.mtf.decode(mtf_decoded)
            
            blocks.append(decompressed)
            indices.append(idx)
        
        result = self.bwt.inverse(blocks, indices)
        self.decode_time = time.time() - start
        return result


class LZSSHACompressor(Compressor):
    
    def __init__(self, window_size: int = 4096):
        super().__init__("LZSS+HA")
        self.lzss = LZSSCompressor(window_size=window_size)
        self.huffman = HuffmanCompressor()

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        
        lzss_compressed = self.lzss.compress(data)
        huffman_compressed = self.huffman.compress(lzss_compressed)
        
        self.encode_time = time.time() - start
        self.compressed_size = len(huffman_compressed)
        return huffman_compressed

    def decompress(self, data: bytes) -> bytes:
        start = time.time()
        
        lzss_compressed = self.huffman.decompress(data)
        decompressed = self.lzss.decompress(lzss_compressed)
        
        self.decode_time = time.time() - start
        return decompressed


class LZWHACompressor(Compressor):
    
    def __init__(self, max_code_bits: int = 11):
        super().__init__("LZW+HA")
        self.lzw = LZWCompressor(max_code_bits=max_code_bits)
        self.huffman = HuffmanCompressor()

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        
        lzw_compressed = self.lzw.compress(data)
        huffman_compressed = self.huffman.compress(lzw_compressed)
        
        self.encode_time = time.time() - start
        self.compressed_size = len(huffman_compressed)
        return huffman_compressed

    def decompress(self, data: bytes) -> bytes:
        start = time.time()
        
        lzw_compressed = self.huffman.decompress(data)
        decompressed = self.lzw.decompress(lzw_compressed)
        
        self.decode_time = time.time() - start
        return decompressed


def chain_compress(data: bytes, *compressors) -> bytes:
    result = data
    for comp in compressors:
        result = comp.compress(result)
    return result


def chain_decompress(data: bytes, *compressors_reversed) -> bytes:
    result = data
    for comp in reversed(compressors_reversed):
        result = comp.decompress(result)
    return result
