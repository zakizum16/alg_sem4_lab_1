#!/usr/bin/env python3
"""Test BWT on real files"""

from bwt import BlockBWT
from rle import RLECompressor
import os

filename = 'test_data/russian_text.txt'

if os.path.exists(filename):
    with open(filename, 'rb') as f:
        file_data = f.read(5000)  # First 5KB only
    
    print(f'File size: {len(file_data)} bytes')
    
    try:
        # BWT
        block_bwt = BlockBWT(block_size=1000)
        print('Created BlockBWT...')
        
        bwt_blocks, indices = block_bwt.forward(file_data)
        print(f'Forward BWT OK: {len(bwt_blocks)} blocks')
        
        # Concat blocks
        bwt_data = b''.join(bwt_blocks)
        print(f'BWT data size: {len(bwt_data)}')
        
        # RLE
        rle = RLECompressor(Ms=1, Mc=1)
        rle_data = rle.encode(bwt_data)
        print(f'RLE data size: {len(rle_data)}')
        print(f'Compression ratio: {len(file_data)}/{len(rle_data)} = {len(file_data)/len(rle_data):.2f}x')
        
        # Decode
        rle_decoded = rle.decode(rle_data)
        print(f'RLE decoded size: {len(rle_decoded)}')
        
        # Inverse BWT
        bwt_decoded_blocks = [rle_decoded[i:i+len(bwt_blocks[0])] for i in range(0, len(rle_decoded), len(bwt_blocks[0]))]
        print(f'BWT blocks count: {len(bwt_decoded_blocks)}')
        
        file_recovered = block_bwt.inverse(bwt_decoded_blocks, indices)
        print(f'Inverse BWT OK: {len(file_recovered)} bytes')
        
        if file_recovered == file_data:
            print('[OK] Perfect match!')
        else:
            print(f'[FAIL] Mismatch: {len(file_recovered)} != {len(file_data)}')
        
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()
else:
    print(f'{filename} does not exist')
