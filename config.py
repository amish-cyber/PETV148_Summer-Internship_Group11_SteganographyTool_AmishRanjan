import os
import tempfile

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-cyber-key-12345'
    
    # Use the system's temporary directory for Vercel/Serverless compatibility
    TEMP_DIR = tempfile.gettempdir()
    UPLOAD_FOLDER = os.path.join(TEMP_DIR, 'stegshield_uploads')
    OUTPUT_FOLDER = os.path.join(TEMP_DIR, 'stegshield_output')
    REPORT_FOLDER = os.path.join(TEMP_DIR, 'stegshield_reports')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB limit
    ALLOWED_EXTENSIONS = {'png'}
