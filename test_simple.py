from rle import RLECompressor
from entropy_coding import calculate_entropy, HuffmanCoding, MTFTransform
from bwt import BWT, BlockBWT
from suffix_array_lz import LZ77, LZSS, LZ78, LZW
import os

def test_rle():
    print("Testing RLE...")
    comp = RLECompressor(1, 1)
    data = b'\xcf\xcf\xcf\xcf\xcf\xce\xce\xce'
    encoded = comp.encode(data)
    decoded = comp.decode(encoded)
    assert data == decoded, "RLE test failed"
    print("✓ RLE works")

def test_entropy():
    print("Testing Entropy...")
    data = b"hello world"
    entropy = calculate_entropy(data)
    assert isinstance(entropy, float), "Entropy test failed"
    print(f"✓ Entropy works (H={entropy:.2f})")

def test_huffman():
    print("Testing Huffman...")
    data = b"hello world"
    bits, codes, freqs = HuffmanCoding.encode(data)
    decoded = HuffmanCoding.decode(bits, codes)
    assert data == decoded, "Huffman test failed"
    print("✓ Huffman works")

def test_mtf():
    print("Testing MTF...")
    data = b"hello"
    encoded = MTFTransform.encode(data)
    decoded = MTFTransform.decode(encoded)
    assert data == decoded, "MTF test failed"
    print("✓ MTF works")

def test_bwt():
    print("Testing BWT...")
    data = b"banana"
    bwt, idx = BWT.forward_matrix(data)
    recovered = BWT.inverse_permutation(bwt, idx)
    assert data == recovered, "BWT test failed"
    print("✓ BWT works")

def test_lz77():
    print("Testing LZ77...")
    data = b"hello hello world"
    encoded = LZ77.encode(data)
    decoded = LZ77.decode(encoded)
    assert data == decoded, "LZ77 test failed"
    print("✓ LZ77 works")

def test_lzss():
    print("Testing LZSS...")
    data = b"hello hello world hello"
    encoded = LZSS.encode(data)
    decoded = LZSS.decode(encoded)
    assert data == decoded, "LZSS test failed"
    print("✓ LZSS works")

def test_lz78():
    print("Testing LZ78...")
    data = b"hello world"
    encoded = LZ78.encode(data)
    decoded = LZ78.decode(encoded)
    assert data == decoded, "LZ78 test failed"
    print("✓ LZ78 works")

def test_lzw():
    print("Testing LZW...")
    data = b"hello world"
    encoded = LZW.encode(data)
    decoded = LZW.decode(encoded)
    assert data == decoded, "LZW test failed"
    print("✓ LZW works")

if __name__ == "__main__":
    print("="*50)
    print("Running tests...")
    print("="*50)
    test_rle()
    test_entropy()
    test_huffman()
    test_mtf()
    test_bwt()
    test_lz77()
    test_lzss()
    test_lz78()
    test_lzw()
    print("="*50)
    print("All tests passed!")
    print("="*50)
