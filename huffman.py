import struct
import time
import heapq
from typing import Dict, List, Tuple
from collections import Counter
from base import Compressor


class HuffmanNode:
    _counter = 0
    
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right
        self.seq = HuffmanNode._counter
        HuffmanNode._counter += 1
    
    def __lt__(self, other):
        if self.freq != other.freq:
            return self.freq < other.freq
        return self.seq < other.seq


class HuffmanCoding:
    
    @staticmethod
    def build_tree(frequencies: Dict[int, int]) -> HuffmanNode:
        if not frequencies:
            return None
        HuffmanNode._counter = 0
        heap = []
        for symbol in frequencies.keys():
            freq = frequencies[symbol]
            node = HuffmanNode(symbol=symbol, freq=freq)
            heapq.heappush(heap, node)
        
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            parent = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, parent)
        
        return heap[0]

    @staticmethod
    def build_codes(node: HuffmanNode, code: str = '', codes: Dict[int, str] = None) -> Dict[int, str]:
        if codes is None:
            codes = {}
        if node is None:
            return codes
        if node.symbol is not None:
        
            codes[node.symbol] = code if code else '0'
            return codes
        HuffmanCoding.build_codes(node.left, code + '0', codes)
        HuffmanCoding.build_codes(node.right, code + '1', codes)
        return codes

    @staticmethod
    def encode(data: bytes) -> Tuple[str, Dict[int, str], Dict[int, int]]:
        if not data:
            return '', {}, {}
        frequencies = Counter(data)
        tree = HuffmanCoding.build_tree(dict(frequencies))
        codes = HuffmanCoding.build_codes(tree)
        encoded_bits = ''
        for byte in data:
            encoded_bits += codes[byte]
        return encoded_bits, codes, dict(frequencies)


class HuffmanCompressor(Compressor):
    """Компрессор на основе Huffman кодирования"""
    
    def __init__(self):
        super().__init__("Huffman")

    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        
        if not data:
            self.encode_time = time.time() - start
            self.compressed_size = 0
            return b''
        
        bits, codes, freqs = HuffmanCoding.encode(data)
        
        payload = bytearray()
        
        payload.extend(struct.pack('>I', len(data)))
        
        payload.extend(struct.pack('>H', len(codes)))  
       
        for symbol in sorted(codes.keys()):
            code = codes[symbol]
            code_len = len(code)
            code_int = int(code, 2)
            
            code_bytes = code_int.to_bytes((code_len + 7) // 8, 'big')
            
            payload.extend(struct.pack('>I', symbol)) 
            payload.extend(struct.pack('>B', code_len))
            payload.append(code_bytes[0] if len(code_bytes) == 1 else code_bytes[0])
            if len(code_bytes) > 1:
                payload.extend(code_bytes[1:])
        
        bits_len = len(bits)
        bits_bytes = int(bits, 2).to_bytes((bits_len + 7) // 8, 'big')
        payload.extend(struct.pack('>I', bits_len))
        payload.extend(bits_bytes)
        
        self.encode_time = time.time() - start
        self.compressed_size = len(payload)
        return bytes(payload)

    def decompress(self, data: bytes) -> bytes:
        start = time.time()
        
        if not data:
            self.decode_time = time.time() - start
            return b''
        
        pos = 0
        
        orig_size = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        
        
        code_count = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        
        codes = {}
        for _ in range(code_count):
           
            symbol = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4
            
            code_len = struct.unpack('>B', data[pos:pos+1])[0]
            pos += 1
            
            code_bytes_len = (code_len + 7) // 8
            code_bytes = data[pos:pos+code_bytes_len]
            pos += code_bytes_len
            
            code_int = int.from_bytes(code_bytes, 'big')
            code_str = format(code_int, f'0{code_len}b')
            codes[symbol] = code_str
        
        bits_len = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        
        bits_bytes_len = (bits_len + 7) // 8
        if pos + bits_bytes_len > len(data):
            bits_bytes_len = len(data) - pos
        
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
                if len(result) >= orig_size:
                    break
        
     
        result = result[:orig_size]
        
        self.decode_time = time.time() - start
        return bytes(result)