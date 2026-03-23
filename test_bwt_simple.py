#!/usr/bin/env python3
"""Quick BWT test"""

from bwt import BlockBWT

test_data = b'banana' * 100

print('Test data size:', len(test_data))
print()

try:
    block_bwt = BlockBWT(block_size=100)
    print('Created BlockBWT with block_size=100')
    
    bwt_blocks, indices = block_bwt.forward(test_data)
    print('Forward BWT OK')
    print(f'Number of blocks: {len(bwt_blocks)}')
    print(f'Block sizes: {[len(b) for b in bwt_blocks]}')
    print(f'Indices: {indices}')
    
    # Try to recover
    recovered = block_bwt.inverse(bwt_blocks, indices)
    print('Inverse BWT OK')
    print(f'Recovered size: {len(recovered)}')
    print(f'Match: {recovered == test_data}')
    
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
