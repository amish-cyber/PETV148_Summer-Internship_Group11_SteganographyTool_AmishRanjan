from PIL import Image
import numpy as np
import os

MAGIC = b'STEG'

def encode_image(image_path: str, data: bytes, output_path: str) -> bool:
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    
    # Payload format: MAGIC (4 bytes) + Length (4 bytes) + Data
    length = len(data)
    payload = MAGIC + length.to_bytes(4, 'big') + data
    
    # Convert payload to bits
    payload_bits = ''.join(f'{byte:08b}' for byte in payload)
    
    max_bytes = (width * height * 3) // 8
    if len(payload) > max_bytes:
        raise ValueError(f"Data too large. Max capacity is {max_bytes} bytes.")
        
    pixels = np.array(img)
    flat_pixels = pixels.flatten()
    
    # Modify LSB
    for i in range(len(payload_bits)):
        flat_pixels[i] = (flat_pixels[i] & ~1) | int(payload_bits[i])
        
    modified_pixels = flat_pixels.reshape((height, width, 3))
    out_img = Image.fromarray(modified_pixels.astype('uint8'), 'RGB')
    out_img.save(output_path, format='PNG')
    return True

def decode_image(image_path: str) -> bytes:
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img).flatten()
    
    # Read first 8 bytes (64 bits) for MAGIC + Length
    if len(pixels) < 64:
        return None
        
    header_bits = ''.join(str(pixels[i] & 1) for i in range(64))
    header_bytes = bytes(int(header_bits[i:i+8], 2) for i in range(0, 64, 8))
    
    if header_bytes[:4] != MAGIC:
        return None
        
    data_length = int.from_bytes(header_bytes[4:8], 'big')
    total_bits_needed = 64 + (data_length * 8)
    
    if len(pixels) < total_bits_needed:
        return None
        
    data_bits = ''.join(str(pixels[i] & 1) for i in range(64, total_bits_needed))
    data_bytes = bytes(int(data_bits[i:i+8], 2) for i in range(0, len(data_bits), 8))
    
    return data_bytes

def get_lsb_viewer_data(original_path: str, encoded_path: str, count: int = 10):
    try:
        orig = Image.open(original_path).convert('RGB')
        enc = Image.open(encoded_path).convert('RGB')
        
        orig_px = np.array(orig).flatten()[:count]
        enc_px = np.array(enc).flatten()[:count]
        
        result = []
        for i in range(count):
            result.append({
                'original': f"{orig_px[i]:08b}",
                'modified': f"{enc_px[i]:08b}",
                'changed': orig_px[i] != enc_px[i]
            })
        return result
    except Exception as e:
        return []
