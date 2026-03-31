import os
import struct

def show_raw(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    
    if len(data) >= 5:
        img_type = data[0]
        width = struct.unpack('>H', data[1:3])[0]
        height = struct.unpack('>H', data[3:5])[0]
        pixels = data[5:]
        
        return {
            'type': img_type,
            'width': width,
            'height': height,
            'pixel_data': pixels,
            'total_size': len(data)
        }
    return None
