import struct
from typing import Tuple, List, Dict

class LZ77:
    @staticmethod
    def encode(data: bytes, window_size: int = 4096, lookahead_size: int = 18) -> bytes:
        if not data:
            return b''
        result = bytearray()
        pos = 0
        n = len(data)
        while pos < n:
            best_offset = 0
            best_length = 0
            window_start = max(0, pos - window_size)
            for i in range(window_start, pos):
                length = 0
                while (length < lookahead_size and pos + length < n and
                       data[i + length] == data[pos + length]):
                    length += 1
                if length > best_length:
                    best_length = length
                    best_offset = pos - i
            if best_length >= 3:
                next_char = data[pos + best_length] if pos + best_length < n else 0
                result.extend(struct.pack('>HBB', best_offset, best_length, next_char))
                pos += best_length + 1
            else:
                result.extend(struct.pack('>HBB', 0, 0, data[pos]))
                pos += 1
        return bytes(result)

    @staticmethod
    def decode(data: bytes) -> bytes:
        result = bytearray()
        pos = 0
        while pos + 4 <= len(data):
            offset, length, next_char = struct.unpack('>HBB', data[pos:pos+4])
            pos += 4
            if length > 0:
                start = len(result) - offset
                for i in range(length):
                    result.append(result[start + i])
            result.append(next_char)
        return bytes(result)

class LZSS:
    @staticmethod
    def encode(data: bytes, window_size: int = 4096, lookahead_size: int = 18) -> bytes:
        if not data:
            return b''
        result = bytearray()
        pos = 0
        n = len(data)
        bits = bytearray()
        flag_byte = 0
        flag_count = 0
        while pos < n:
            best_offset = 0
            best_length = 0
            window_start = max(0, pos - window_size)
            for i in range(window_start, pos):
                length = 0
                while (length < lookahead_size and pos + length < n and
                       data[i + length] == data[pos + length]):
                    length += 1
                if length > best_length:
                    best_length = length
                    best_offset = pos - i
            if best_length >= 4:
                flag_byte |= (1 << (7 - flag_count))
                bits.extend(struct.pack('>HB', best_offset, best_length))
                pos += best_length
            else:
                bits.append(data[pos])
                pos += 1
            flag_count += 1
            if flag_count == 8:
                result.append(flag_byte)
                result.extend(bits)
                bits = bytearray()
                flag_byte = 0
                flag_count = 0
        if flag_count > 0:
            result.append(flag_byte)
            result.extend(bits)
        return bytes(result)

    @staticmethod
    def decode(data: bytes) -> bytes:
        result = bytearray()
        pos = 0
        while pos < len(data):
            flag_byte = data[pos]
            pos += 1
            for i in range(8):
                if pos >= len(data):
                    break
                if flag_byte & (1 << (7 - i)):
                    if pos + 3 > len(data):
                        break
                    offset, length = struct.unpack('>HB', data[pos:pos+3])
                    pos += 3
                    start = len(result) - offset
                    for j in range(length):
                        result.append(result[start + j])
                else:
                    result.append(data[pos])
                    pos += 1
        return bytes(result)

class LZ78:
    @staticmethod
    def encode(data: bytes, max_dict_size: int = 65536) -> bytes:
        if not data:
            return b''
        result = bytearray()
        dictionary = {b'': 0}
        dict_idx = 1
        pos = 0
        n = len(data)
        while pos < n and dict_idx < max_dict_size:
            best_match = b''
            best_match_idx = 0
            i = 1
            while pos + i <= n and i < 256:
                substr = data[pos:pos+i]
                if substr in dictionary:
                    best_match = substr
                    best_match_idx = dictionary[substr]
                    i += 1
                else:
                    break
            next_char = data[pos + len(best_match)] if pos + len(best_match) < n else 0
            result.extend(struct.pack('>HB', best_match_idx, next_char))
            new_substr = best_match + bytes([next_char])
            if new_substr not in dictionary:
                dictionary[new_substr] = dict_idx
                dict_idx += 1
            pos += len(best_match) + 1
        return bytes(result)

    @staticmethod
    def decode(data: bytes) -> bytes:
        result = bytearray()
        dictionary = {0: b''}
        dict_idx = 1
        pos = 0
        while pos + 3 <= len(data):
            ref, char = struct.unpack('>HB', data[pos:pos+3])
            pos += 3
            if ref in dictionary:
                decoded = dictionary[ref] + bytes([char])
                result.extend(decoded)
                dictionary[dict_idx] = decoded
                dict_idx += 1
            else:
                result.append(char)
        return bytes(result)

class LZW:
    @staticmethod
    def encode(data: bytes, max_code_bits: int = 12) -> bytes:
        if not data:
            return b''
        max_code = 1 << max_code_bits
        dictionary = {bytes([i]): i for i in range(256)}
        dict_size = 256
        result = bytearray()
        w = b''
        for byte in data:
            wc = w + bytes([byte])
            if wc in dictionary:
                w = wc
            else:
                result.extend(struct.pack('>H', dictionary[w]))
                if dict_size < max_code:
                    dictionary[wc] = dict_size
                    dict_size += 1
                w = bytes([byte])
        if w:
            result.extend(struct.pack('>H', dictionary[w]))
        return bytes(result)

    @staticmethod
    def decode(data: bytes) -> bytes:
        dictionary = {i: bytes([i]) for i in range(256)}
        dict_size = 256
        result = bytearray()
        pos = 0
        if pos + 2 > len(data):
            return b''
        prev_code = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        result.extend(dictionary.get(prev_code, b''))
        while pos + 2 <= len(data):
            code = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2
            if code in dictionary:
                entry = dictionary[code]
            else:
                entry = dictionary[prev_code] + dictionary[prev_code][0:1]
            result.extend(entry)
            if dict_size < 4096:
                dictionary[dict_size] = dictionary[prev_code] + entry[0:1]
                dict_size += 1
            prev_code = code
        return bytes(result)
