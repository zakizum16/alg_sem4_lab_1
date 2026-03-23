#!/usr/bin/env python3
"""Простой тест LZ78"""

from suffix_array_lz import LZ78

# Простой тест
test_data = b'abcabcabc'

print(f"Исходные: {test_data}")

encoded = LZ78.encode(test_data, max_dict_size=1024)
print(f"Закодировано: {len(encoded)} байт")
print(f"Hex: {encoded.hex()}")

decoded = LZ78.decode(encoded, max_dict_size=1024)
print(f"Декодировано: {decoded}")
print(f"Размер: {len(decoded)}")
print(f"Совпадение: {test_data == decoded}")

if test_data != decoded:
    print("\nРазница:")
    for i, (a, b) in enumerate(zip(test_data, decoded)):
        if a != b:
            print(f"  Position {i}: {a} vs {b}")
    if len(test_data) != len(decoded):
        print(f"  Размер: {len(test_data)} vs {len(decoded)}")
