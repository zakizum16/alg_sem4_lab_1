import math
from collections import Counter
import struct
import heapq
from typing import Dict, List, Tuple

def calculate_entropy(data: bytes, Ms: int = 1) -> float:
    if len(data) < Ms:
        return 0.0
    symbols = []
    for i in range(0, len(data) - Ms + 1, Ms):
        symbol = data[i:i+Ms]
        symbols.append(symbol)
    total = len(symbols)
    freq = Counter(symbols)
    entropy = 0.0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

class MTFTransform:
    @staticmethod
    def encode(data: bytes) -> bytes:
        alphabet = list(range(256))
        result = bytearray()
        for byte in data:
            index = alphabet.index(byte)
            result.append(index)
            alphabet.pop(index)
            alphabet.insert(0, byte)
        return bytes(result)

    @staticmethod
    def decode(data: bytes) -> bytes:
        alphabet = list(range(256))
        result = bytearray()
        for index in data:
            byte = alphabet[index]
            result.append(byte)
            alphabet.pop(index)
            alphabet.insert(0, byte)
        return bytes(result)

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
        for symbol in sorted(frequencies.keys()):
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
        frequencies = Counter(data)
        tree = HuffmanCoding.build_tree(dict(frequencies))
        codes = HuffmanCoding.build_codes(tree)
        encoded_bits = ''
        for byte in data:
            encoded_bits += codes[byte]
        return encoded_bits, codes, dict(frequencies)

    @staticmethod
    def decode(encoded_bits: str, codes: Dict[int, str]) -> bytes:
        reverse_codes = {v: k for k, v in codes.items()}
        result = bytearray()
        current_code = ''
        for bit in encoded_bits:
            current_code += bit
            if current_code in reverse_codes:
                result.append(reverse_codes[current_code])
                current_code = ''
        return bytes(result)

class CanonicalHuffman:
    @staticmethod
    def build_from_lengths(lengths: List[int]) -> Dict[int, str]:
        max_len = max(lengths) if lengths else 0
        code = 0
        codes = {}
        for symbol in range(len(lengths)):
            length = lengths[symbol]
            if length > 0:
                code_str = format(code, f'0{length}b')
                codes[symbol] = code_str
                code = (code + 1) << (max_len - length)
        return codes

class ArithmeticCoding:
    @staticmethod
    def encode(data: bytes, frequencies: Dict[int, int] = None) -> float:
        if frequencies is None:
            frequencies = Counter(data)
        total = sum(frequencies.values())
        cumulative = {}
        pos = 0
        for symbol in sorted(frequencies.keys()):
            cumulative[symbol] = pos / total
            pos += frequencies[symbol] / total
        
        low = 0.0
        high = 1.0
        for byte in data:
            range_size = high - low
            high = low + range_size * (cumulative[byte] + frequencies[byte] / total)
            low = low + range_size * cumulative[byte]
        
        return (low + high) / 2
