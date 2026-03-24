import struct
import time
from typing import Dict, Tuple
from abc import ABC, abstractmethod
from collections import Counter
from rle import RLECompressor
from entropy_coding import HuffmanCoding, MTFTransform, CanonicalHuffman, calculate_entropy
from bwt import BlockBWT, SuffixArrayBWT
from suffix_array_lz import LZSS, LZW

class Compressor(ABC):
    def __init__(self, name: str):
        self.name = name
        self.original_size = 0
        self.compressed_size = 0
        self.encode_time = 0.0
        self.decode_time = 0.0

    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        pass

    @abstractmethod
    def decompress(self, data: bytes) -> bytes:
        pass

    def get_ratio(self) -> float:
        if self.compressed_size == 0:
            return 0.0
        return self.original_size / self.compressed_size

    def get_stats(self) -> Dict:
        return {
            'name': self.name,
            'original': self.original_size,
            'compressed': self.compressed_size,
            'ratio': self.get_ratio(),
            'encode_time': self.encode_time,
            'decode_time': self.decode_time
        }

class RLECompressor_Standalone(Compressor):
    def __init__(self, Ms: int = 1, Mc: int = 1):
        super().__init__("RLE")
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

class HuffmanCompressor(Compressor):
    def __init__(self):
        super().__init__("Huffman")

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        bits, codes, freqs = HuffmanCoding.encode(data)
        bits_bytes = int(bits, 2).to_bytes((len(bits) + 7) // 8, 'big')
        payload = struct.pack('>I', len(data))
        payload += struct.pack('>B', len(codes))
        for symbol in sorted(codes.keys()):
            code = codes[symbol]
            payload += struct.pack('>BBB', symbol, len(code), int(code, 2))
        payload += struct.pack('>I', len(bits))
        payload += bits_bytes
        self.encode_time = time.time() - start
        self.compressed_size = len(payload)
        return payload

    def decompress(self, data: bytes) -> bytes:
        start = time.time()
        pos = 0
        orig_size = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        code_count = struct.unpack('>B', data[pos:pos+1])[0]
        pos += 1
        codes = {}
        for _ in range(code_count):
            symbol, code_len, code_int = struct.unpack('>BBB', data[pos:pos+3])
            pos += 3
            code_str = format(code_int, f'0{code_len}b')
            codes[symbol] = code_str
        bits_len = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        bits_bytes_len = (bits_len + 7) // 8
        bits_int = int.from_bytes(data[pos:pos+bits_bytes_len], 'big')
        bits_str = format(bits_int, f'0{bits_len}b')
        reverse_codes = {v: k for k, v in codes.items()}
        result = bytearray()
        current = ''
        for bit in bits_str:
            current += bit
            if current in reverse_codes:
                result.append(reverse_codes[current])
                current = ''
        self.decode_time = time.time() - start
        return bytes(result[:orig_size])

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

class LZSSCompressor(Compressor):
    def __init__(self, window_size: int = 4096):
        super().__init__("LZSS")
        self.window_size = window_size

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        compressed = LZSS.encode(data, self.window_size)
        self.encode_time = time.time() - start
        self.compressed_size = len(compressed)
        return compressed

    def decompress(self, data: bytes) -> bytes:
        start = time.time()
        decompressed = LZSS.decode(data)
        self.decode_time = time.time() - start
        return decompressed

class LZWCompressor(Compressor):
    def __init__(self, max_code_bits: int = 12):
        super().__init__("LZW")
        self.max_code_bits = max_code_bits

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        compressed = LZW.encode(data, self.max_code_bits)
        self.encode_time = time.time() - start
        self.compressed_size = len(compressed)
        return compressed

    def decompress(self, data: bytes) -> bytes:
        start = time.time()
        decompressed = LZW.decode(data)
        self.decode_time = time.time() - start
        return decompressed
