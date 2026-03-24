from typing import Tuple, List

class BWT:
    @staticmethod
    def forward_matrix(data: bytes) -> Tuple[bytes, int]:
        if not data:
            return b'', 0
        n = len(data)
        rotations = []
        for i in range(n):
            rotation = data[i:] + data[:i]
            rotations.append((rotation, i))
        rotations.sort(key=lambda x: x[0])
        bwt_result = b''.join(r[0][-1:] for r in rotations)
        original_index = 0
        for i, (rotation, shift_index) in enumerate(rotations):
            if shift_index == 0:
                original_index = i
                break
        return bwt_result, original_index

    @staticmethod
    def inverse_matrix(bwt_data: bytes, original_index: int) -> bytes:
        if not bwt_data:
            return b''
        n = len(bwt_data)
        counts = {}
        for byte in bwt_data:
            counts[byte] = counts.get(byte, 0) + 1
        positions = {}
        pos = 0
        for byte_val in sorted(counts.keys()):
            positions[byte_val] = pos
            pos += counts[byte_val]
        next_idx = [0] * n
        count = {}
        for i in range(n):
            byte_val = bwt_data[i]
            if byte_val not in count:
                count[byte_val] = 0
            j = positions[byte_val] + count[byte_val]
            next_idx[j] = i
            count[byte_val] += 1
        result = bytearray()
        idx = original_index
        for _ in range(n):
            result.append(bwt_data[next_idx[idx]])
            idx = next_idx[idx]
        return bytes(result)

    @staticmethod
    def inverse_permutation(bwt_data: bytes, original_index: int) -> bytes:
        if not bwt_data:
            return b''
        n = len(bwt_data)
        counts = {}
        for byte in bwt_data:
            counts[byte] = counts.get(byte, 0) + 1
        first_column_positions = {}
        pos = 0
        for byte in sorted(counts.keys()):
            first_column_positions[byte] = pos
            pos += counts[byte]
        next_index = [0] * n
        count = {}
        for i in range(n):
            byte = bwt_data[i]
            if byte not in count:
                count[byte] = 0
            j = first_column_positions[byte] + count[byte]
            next_index[j] = i
            count[byte] += 1
        result = bytearray()
        idx = original_index
        for _ in range(n):
            result.append(bwt_data[next_index[idx]])
            idx = next_index[idx]
        return bytes(result)

class BlockBWT:
    def __init__(self, block_size: int = 900000):
        self.block_size = block_size

    def forward(self, data: bytes) -> Tuple[List[bytes], List[int]]:
        blocks = []
        indices = []
        for i in range(0, len(data), self.block_size):
            block = data[i:i+self.block_size]
            bwt_block, idx = BWT.forward_matrix(block)
            blocks.append(bwt_block)
            indices.append(idx)
        return blocks, indices

    def inverse(self, blocks: List[bytes], indices: List[int]) -> bytes:
        result = bytearray()
        for bwt_block, idx in zip(blocks, indices):
            original_block = BWT.inverse_permutation(bwt_block, idx)
            result.extend(original_block)
        return bytes(result)

class SuffixArrayBWT:
    @staticmethod
    def build_suffix_array(data: bytes) -> List[int]:
        if not data:
            return []
        n = len(data)
        suffixes = [(data[i:], i) for i in range(n)]
        suffixes.sort(key=lambda x: x[0])
        return [idx for _, idx in suffixes]

    @staticmethod
    def suffix_array_to_bwt(suffix_array: List[int], data: bytes) -> Tuple[bytes, int]:
        if not suffix_array:
            return b'', 0
        n = len(data)
        bwt = bytearray()
        original_index = 0
        for i, sa_val in enumerate(suffix_array):
            prev_idx = (sa_val - 1) % n
            bwt.append(data[prev_idx])
            if sa_val == 0:
                original_index = i
        return bytes(bwt), original_index
