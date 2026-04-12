import os
import time
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Permitir CORS para que el cliente acceda a la API
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'gif'}
API_TOKEN = os.environ.get('API_TOKEN', 'admin123')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Middleware para validar Token
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # El token puede venir en encabezado o en un query param
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]
        else:
            token = request.args.get('token')
            
        if not token or token != API_TOKEN:
            return jsonify({'error': 'No autorizado'}), 401
            
        return f(*args, **kwargs)
    return decorated

@app.route('/upload', methods=['POST'])
@require_auth
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No se encontró la imagen'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Ningún archivo seleccionado'}), 400
        
    if file and allowed_file(file.filename):
        try:
            base_filename = secure_filename(file.filename)
            name, ext = os.path.splitext(base_filename)
            filename = f"{name}_{int(time.time())}{ext}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            img = Image.open(file.stream)
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            border_size = int(request.form.get('size', 20))
            border_color = request.form.get('color', 'black')
            
            bordered_img = ImageOps.expand(img, border=border_size, fill=border_color)
            bordered_img.save(filepath)
            
            return jsonify({
                'message': 'Imagen subida y procesada con éxito',
                'filename': filename
            }), 201
            
        except Exception as e:
            return jsonify({'error': f'Error procesando la imagen: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Formato no permitido. Solo JPG, JPEG, GIF.'}), 400

@app.route('/images', methods=['GET'])
@require_auth
def list_images():
    try:
        files = os.listdir(UPLOAD_FOLDER)
        valid_files = [f for f in files if allowed_file(f)]
        return jsonify(valid_files), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images', methods=['DELETE'])
@require_auth
def delete_all_images():
    try:
        for f in os.listdir(UPLOAD_FOLDER):
            if allowed_file(f):
                os.remove(os.path.join(UPLOAD_FOLDER, f))
        return jsonify({'message': 'Todas las imágenes fueron eliminadas con éxito'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>', methods=['GET'])
@require_auth
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
