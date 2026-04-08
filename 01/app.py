import os
from flask import Flask, render_template, request, abort, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB máximo
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'

def validate_image(stream):
    """Valida el tipo de imagen leyendo los primeros bytes (magic numbers)"""
    header = stream.read(64)  # Leemos 64 bytes es suficiente
    stream.seek(0)  # Reiniciamos el puntero
    
    # JPEG: empieza con FF D8 FF
    if header[:3] == b'\xff\xd8\xff':
        return '.jpg'
    # PNG: empieza con PNG signature
    if header[:8] == b'\x89PNG\r\n\x1a\n':
        return '.png'
    # GIF: empieza con GIF87a o GIF89a
    if header[:6] in (b'GIF87a', b'GIF89a'):
        return '.gif'
    
    return None  # No es una imagen válida

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH']) if os.path.exists(app.config['UPLOAD_PATH']) else []
    return render_template('index.html', files=files)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    
    if filename != '':
        file_ext = os.path.splitext(filename)[1].lower()
        detected_ext = validate_image(uploaded_file.stream)
        
        # Validar extensión y contenido
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
           file_ext != detected_ext:
            return "Invalid image", 400
        
        os.makedirs(app.config['UPLOAD_PATH'], exist_ok=True)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        return "", 204
    
    return "No file selected", 400

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

if __name__ == '__main__':
    app.run(debug=True)