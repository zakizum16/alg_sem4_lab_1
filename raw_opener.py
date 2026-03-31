import os
import struct

def show_raw(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    
    print(f"\n{os.path.basename(file_path)} ({len(data)} bytes)")
    print("-"*50)
    
    # HEX
    print("HEX:")
    for i in range(0, min(64, len(data)), 16):
        hex_part = ' '.join(f'{b:02X}' for b in data[i:i+16])
        print(f"  {hex_part}")
    
    # BITS
    print("\nBITS (first 32 bytes):")
    for i in range(min(32, len(data))):
        print(f"  {format(data[i], '08b')}")
    
    # Structure
    if len(data) >= 5:
        t = data[0]
        w = struct.unpack('>H', data[1:3])[0]
        h = struct.unpack('>H', data[3:5])[0]
        print(f"\nType:{t} Width:{w} Height:{h}")

1
folder = r'C:/Users/dream/PycharmProjects/Alg_l1_2sem/raw_images'

files = [f for f in os.listdir(folder) if f.endswith('.raw')]
for i, f in enumerate(files, 1):
    print(f"{i}. {f}")

choice = int(input("\nChoose file: ")) - 1
show_raw(os.path.join(folder, files[choice]))