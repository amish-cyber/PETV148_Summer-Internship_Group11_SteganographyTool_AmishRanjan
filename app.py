from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
from config import Config
from utils.crypto import encrypt_message, decrypt_message
from utils.stego import encode_image, decode_image, get_lsb_viewer_data
from utils.analysis import analyze_image, generate_difference_image
from utils.report import generate_report
from utils.hash_utils import calculate_sha256
import uuid

app = Flask(__name__)
app.config.from_object(Config)

# Ensure dirs exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PNG allowed'}), 400
            
        message = request.form.get('message', '')
        password = request.form.get('password', '')
        
        if not message or not password:
            return jsonify({'error': 'Message and password required'}), 400
            
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
        output_filename = f"encoded_{filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        file.save(upload_path)
        
        try:
            encrypted_data = encrypt_message(message, password)
            encode_image(upload_path, encrypted_data, output_path)
            
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        file = request.files['image']
        password = request.form.get('password', '')
        
        if not password:
            return jsonify({'error': 'Password required'}), 400
            
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
        file.save(upload_path)
        
        try:
            hidden_data = decode_image(upload_path)
            if not hidden_data:
                return jsonify({'error': 'No hidden data found or invalid format'}), 400
                
            message = decrypt_message(hidden_data, password)
            if message is None:
                return jsonify({'error': 'Invalid password or corrupted data'}), 400
                
            return jsonify({'success': True, 'message': message})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return render_template('decode.html')

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        file = request.files['image']
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
        file.save(upload_path)
        
        analysis_data = analyze_image(upload_path)
        if analysis_data:
            analysis_data['filename'] = filename
            return jsonify({'success': True, 'data': analysis_data, 'upload_id': f"{unique_id}_{filename}"})
        else:
            return jsonify({'error': 'Failed to analyze image'}), 500

    return render_template('analysis.html')

@app.route('/report', methods=['POST'])
def get_report():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    file = request.files['image']
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
    file.save(upload_path)
    
    analysis_data = analyze_image(upload_path)
    if not analysis_data:
        return jsonify({'error': 'Failed to analyze image'}), 500
        
    report_filename = f"report_{unique_id}.pdf"
    report_path = os.path.join(app.config['REPORT_FOLDER'], report_filename)
    
    if generate_report(upload_path, analysis_data, report_path):
        return send_file(report_path, as_attachment=True, download_name=report_filename)
    return jsonify({'error': 'Failed to generate report'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
