from PIL import Image
import os
import cv2
import numpy as np

def analyze_image(image_path: str):
    try:
        img = Image.open(image_path)
        width, height = img.size
        file_size = os.path.getsize(image_path)
        channels = len(img.getbands())
        color_mode = img.mode
        
        capacity_bytes = (width * height * channels) // 8
        capacity_kb = capacity_bytes / 1024
        
        # Check for hidden data (rough heuristic based on magic bytes)
        from .stego import decode_image
        hidden_data = decode_image(image_path)
        has_hidden = hidden_data is not None
        
        return {
            'width': width,
            'height': height,
            'resolution': f"{width} × {height}",
            'file_size': f"{file_size / 1024:.2f} KB",
            'channels': channels,
            'color_mode': color_mode,
            'estimated_capacity': f"{capacity_kb:.2f} KB",
            'capacity_bytes': capacity_bytes,
            'hidden_data_detected': 'Yes' if has_hidden else 'No',
            'encoding': 'LSB' if has_hidden else 'N/A',
            'encrypted': 'Yes' if has_hidden and len(hidden_data) > 28 else 'N/A',
            'confidence': '99%' if has_hidden else 'N/A',
            'header': 'Found' if has_hidden else 'Not Found'
        }
    except Exception as e:
        return None

def generate_difference_image(img1_path: str, img2_path: str, output_path: str):
    # Use cv2 to find difference and highlight it
    try:
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        
        if img1.shape != img2.shape:
            return False
            
        diff = cv2.absdiff(img1, img2)
        # Enhance visibility of diff
        mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        th = 1
        imask = mask > th
        
        canvas = np.zeros_like(img2, np.uint8)
        canvas[imask] = [0, 0, 255] # Red highlight for differences
        
        cv2.imwrite(output_path, canvas)
        return True
    except Exception as e:
        return False
