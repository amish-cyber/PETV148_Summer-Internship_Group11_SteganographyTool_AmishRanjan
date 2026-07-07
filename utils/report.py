from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os
from datetime import datetime
from .hash_utils import calculate_sha256
from PIL import Image

def generate_report(image_path: str, analysis_data: dict, output_path: str) -> bool:
    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # 1. Draw Dark Background
        c.setFillColor(colors.HexColor("#050a15"))
        c.rect(0, 0, width, height, fill=1, stroke=0)
        
        # 2. Draw Grid/Cyber Pattern Overlay
        c.setStrokeColor(colors.HexColor("#00f3ff"))
        # Using state saving for alpha/opacity
        c.saveState()
        c.setStrokeAlpha(0.1)
        c.setLineWidth(0.5)
        for i in range(0, int(width), 20):
            c.line(i, 0, i, height)
        for i in range(0, int(height), 20):
            c.line(0, i, width, i)
        c.restoreState()
            
        # 3. Draw Header Title
        c.setFillColor(colors.HexColor("#00f3ff"))
        c.setFont("Helvetica-Bold", 24)
        c.drawString(40, height - 60, "STEGSHIELD // FORENSICS INTELLIGENCE")
        
        # Header separator line
        c.setStrokeColor(colors.HexColor("#39ff14"))
        c.setLineWidth(2)
        c.line(40, height - 70, width - 40, height - 70)
        
        # 4. Meta Info Box (Time, File, Hash)
        c.setFillColor(colors.HexColor("#39ff14"))
        c.setFont("Courier-Bold", 10)
        c.drawString(40, height - 90, f"[SYS_TIME]: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        c.drawString(40, height - 105, f"[TARGET]: {os.path.basename(image_path)}")
        
        file_hash = calculate_sha256(image_path)
        c.drawString(40, height - 120, f"[SHA-256]: {file_hash}")
        
        # 5. Image Frame (Cyber style)
        img_x, img_y = 40, height - 420
        img_w, img_h = 240, 240
        
        # Frame borders
        c.setStrokeColor(colors.HexColor("#00f3ff"))
        c.setLineWidth(1)
        c.rect(img_x - 5, img_y - 5, img_w + 10, img_h + 10, fill=0, stroke=1)
        
        # Corner accents (Thick edges)
        c.setLineWidth(3)
        l = 15 # length of accent
        # Bottom Left
        c.line(img_x - 5, img_y - 5, img_x - 5 + l, img_y - 5)
        c.line(img_x - 5, img_y - 5, img_x - 5, img_y - 5 + l)
        # Bottom Right
        c.line(img_x + img_w + 5, img_y - 5, img_x + img_w + 5 - l, img_y - 5)
        c.line(img_x + img_w + 5, img_y - 5, img_x + img_w + 5, img_y - 5 + l)
        # Top Left
        c.line(img_x - 5, img_y + img_h + 5, img_x - 5 + l, img_y + img_h + 5)
        c.line(img_x - 5, img_y + img_h + 5, img_x - 5, img_y + img_h + 5 - l)
        # Top Right
        c.line(img_x + img_w + 5, img_y + img_h + 5, img_x + img_w + 5 - l, img_y + img_h + 5)
        c.line(img_x + img_w + 5, img_y + img_h + 5, img_x + img_w + 5, img_y + img_h + 5 - l)
        
        # Draw the actual image inside the frame, preserving aspect ratio
        c.drawImage(image_path, img_x, img_y, width=img_w, height=img_h, preserveAspectRatio=True, mask='auto')
        
        # HUD element below image
        c.setFillColor(colors.HexColor("#00f3ff"))
        c.setFont("Courier", 8)
        c.drawString(img_x, img_y - 15, "VISUAL DATA RECONSTRUCTION COMPLETE [100%]")
        
        # 6. Data Analysis Section
        data_x = 320
        c.setFillColor(colors.HexColor("#00f3ff"))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(data_x, height - 160, ">>> DIAGNOSTIC METADATA")
        
        y_pos = height - 190
        for key, value in analysis_data.items():
            if key not in ['capacity_bytes', 'filename']:
                label = str(key).replace('_', ' ').upper()
                
                # Label
                c.setFont("Courier-Bold", 10)
                c.setFillColor(colors.HexColor("#8892b0"))
                c.drawString(data_x, y_pos, f"{label}:")
                
                # Highlight critical findings
                if value == 'Yes' or value == 'Found':
                    c.setFillColor(colors.HexColor("#39ff14")) # Neon Green
                elif value == 'No' or value == 'Not Found':
                    c.setFillColor(colors.HexColor("#ff3333")) # Cyber Red
                else:
                    c.setFillColor(colors.white) # Standard text
                    
                c.setFont("Courier", 11)
                c.drawString(data_x + 140, y_pos, str(value))
                y_pos -= 22
                
        # Decorative visual scanner block
        c.setStrokeColor(colors.HexColor("#39ff14"))
        c.setLineWidth(1)
        for i in range(12):
            c.rect(data_x + (i*15), y_pos - 30, 10, 4, fill=1, stroke=0)

        # 7. Footer
        c.setFillColor(colors.HexColor("#00f3ff"))
        c.setFont("Courier", 8)
        c.drawString(40, 30, "SYSTEM // STEGSHIELD v1.0 // CLASSIFIED INFORMATION // END OF REPORT")
        
        c.save()
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False
