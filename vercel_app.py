import os
import sys
import uuid
import traceback
from flask import Flask, request, render_template, send_from_directory, url_for, flash, redirect

# Ensure modules can be imported properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# En Vercel usamos módulos simplificados
try:
    # Primero intentamos importar de los módulos de Vercel
    from vercel_modules.video_generator import generate_video
    # Desactivamos todas las APIs de IA en Vercel por simplicidad
    MISTRAL_AVAILABLE = False
    GEMINI_AVAILABLE = False
    ANTHROPIC_AVAILABLE = False
    DEEPSEEK_AVAILABLE = False
    print("Utilizando módulos optimizados para Vercel")
except ImportError as e:
    # Si falla, intentamos con los módulos normales
    try:
        from modules.video_generator import generate_video
        from modules.ai_providers import (MISTRAL_AVAILABLE, GEMINI_AVAILABLE, 
                                       ANTHROPIC_AVAILABLE, DEEPSEEK_AVAILABLE)
        print("Utilizando módulos estándar")
    except ImportError as e:
        print(f"Error importando módulos: {e}")
        # Fallbacks para las flags de disponibilidad
        MISTRAL_AVAILABLE = False
        GEMINI_AVAILABLE = False
        ANTHROPIC_AVAILABLE = False
        DEEPSEEK_AVAILABLE = False

# --- Flask App Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', '/tmp/match_cut_output')
app.config['FONT_DIR'] = os.environ.get('FONT_DIR', 'fonts')
app.config['MEDIA_DIR'] = os.environ.get('MEDIA_DIR', 'media')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

# Ensure directories exist
for directory in [app.config['UPLOAD_FOLDER'], app.config['FONT_DIR'], app.config['MEDIA_DIR']]:
    os.makedirs(directory, exist_ok=True)

# --- Flask Routes ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main form page."""
    # Pass AI provider availability to the template
    return render_template('index.html', 
                          mistral_available=MISTRAL_AVAILABLE,
                          gemini_available=GEMINI_AVAILABLE,
                          anthropic_available=ANTHROPIC_AVAILABLE,
                          deepseek_available=DEEPSEEK_AVAILABLE)

@app.route('/generate', methods=['POST'])
def generate():
    """Handles form submission, triggers video generation."""
    try:
        # Process texture file if uploaded
        if 'texture_file' in request.files and request.files['texture_file'].filename:
            uploaded_file = request.files['texture_file']
            if '.' in uploaded_file.filename and uploaded_file.filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png']:
                try:
                    custom_texture_filename = f"custom_texture_{uuid.uuid4().hex[:8]}.jpg"
                    custom_texture_path = os.path.join(app.config['MEDIA_DIR'], custom_texture_filename)
                    uploaded_file.save(custom_texture_path)
                    background_texture = custom_texture_filename if request.form.get('background_texture') == 'custom' else request.form.get('background_texture', 'none')
                except Exception as e:
                    print(f"Error saving uploaded texture: {e}")
                    background_texture = request.form.get('background_texture', 'none')
            else:
                background_texture = request.form.get('background_texture', 'none')
        else:
            background_texture = request.form.get('background_texture', 'none')
            
        params = {
            'width': request.form.get('width', default=1024, type=int),
            'height': request.form.get('height', default=1024, type=int),
            'fps': request.form.get('fps', default=10, type=int),
            'duration': request.form.get('duration', default=5, type=int),
            'highlighted_text': request.form.get('highlighted_text', default="Match Cut"),
            'highlight_color': request.form.get('highlight_color', default='#FFFF00'),
            'text_color': request.form.get('text_color', default='#000000'),
            'background_color': request.form.get('background_color', default='#FFFFFF'),
            'blur_type': request.form.get('blur_type', default='gaussian'),
            'blur_radius': request.form.get('blur_radius', default=4.0, type=float),
            'ai_enabled': request.form.get('ai_enabled') == 'true',
            'ai_provider': request.form.get('ai_provider', default='mistral'),
            'api_key': request.form.get('api_key', ''),
            'background_texture': background_texture,
            'selected_font': request.form.get('selected_font', default='random'),
            'text_density': request.form.get('text_density', default='2', type=int)
        }

        # Input validation
        if not params['highlighted_text']:
            return render_template('index.html', error='El texto destacado no puede estar vacío.')
        if not (1 <= params['fps'] <= 60):
            return render_template('index.html', error='Los FPS deben estar entre 1 y 60.')
        if not (1 <= params['duration'] <= 60):
            return render_template('index.html', error='La duración debe estar entre 1 y 60 segundos.')
        if not (256 <= params['width'] <= 4096) or not (256 <= params['height'] <= 4096):
            return render_template('index.html', error='El ancho y alto deben estar entre 256 y 4096 píxeles.')

        # For Vercel, limit resource usage
        if params['width'] * params['height'] > 1920 * 1080:
            return render_template('index.html', 
                                  error='Para el despliegue en Vercel, la resolución máxima es 1920x1080.')
        
        if params['duration'] > 10:
            return render_template('index.html', 
                                  error='Para el despliegue en Vercel, la duración máxima es de 10 segundos.')

        # Generate the video
        generated_filename, error = generate_video(params, app.config)

        if error:
            return render_template('index.html', error=error)
        else:
            return render_template('index.html', filename=generated_filename)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
        return render_template('index.html', error=f"Ocurrió un error inesperado: {str(e)}")

@app.route('/output/<filename>')
def download_file(filename):
    """Serves the generated video file for download."""
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        return redirect(url_for('index'))
         
@app.route('/fonts/<filename>')
def font_file(filename):
    """Serves font files for preview in the browser."""
    try:
        if not filename.lower().endswith(('.ttf', '.otf')):
            return "Invalid font file format", 400
        return send_from_directory(app.config["FONT_DIR"], filename)
    except Exception:
        return "Font not found", 404
        
@app.route('/media/<filename>')
def media_file(filename):
    """Serves media files like textures for preview in the browser."""
    try:
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # Check if it's one of the default textures without extension
            if filename in ['textura1', 'textura2', 'textura3']:
                return send_from_directory(app.config["MEDIA_DIR"], f"{filename}.jpg")
            return "Invalid media file format", 400
        return send_from_directory(app.config["MEDIA_DIR"], filename)
    except Exception as e:
        print(f"Error serving media file {filename}: {e}")
        return "Media file not found", 404

# Log AI availability
def log_ai_availability():
    print(f"Mistral AI Available: {MISTRAL_AVAILABLE}")
    print(f"Google Gemini Available: {GEMINI_AVAILABLE}")
    print(f"Anthropic Available: {ANTHROPIC_AVAILABLE}")
    print(f"DeepSeek Available: {DEEPSEEK_AVAILABLE}")

# Log AI availability when loaded
log_ai_availability()

# Required for Vercel
app.debug = False

# This is for local development - won't be used on Vercel
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))
