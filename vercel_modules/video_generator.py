"""
Módulo para la generación de videos en Vercel
Este archivo es una versión simplificada del módulo video_generator.py
optimizada para funcionar en el entorno serverless de Vercel
"""
import os
import uuid
import traceback
import random
import numpy as np
from PIL import Image
from moviepy.editor import ImageSequenceClip

def generate_video(params, app_config):
    """
    Versión simplificada para Vercel
    Simula la generación del video y devuelve un resultado de prueba
    """
    try:
        # Para Vercel, limitamos la duración y resolución
        width = min(params['width'], 1920)
        height = min(params['height'], 1080)
        fps = params['fps']
        duration_seconds = min(params['duration'], 10)
        highlighted_text = params['highlighted_text']
        
        # Generamos un nombre único para el archivo de salida
        unique_id = uuid.uuid4()
        output_filename = f"text_match_cut_{unique_id}.mp4"
        output_path = os.path.join(app_config['UPLOAD_FOLDER'], output_filename)
        
        # Aseguramos que el directorio de salida exista
        os.makedirs(app_config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Para prueba en Vercel, creamos un video muy simple
        # En un entorno de producción, implementaríamos la lógica completa
        frames = []
        # Crear frames de prueba
        for i in range(fps * duration_seconds):
            # Crear un frame con un color de fondo y el texto destacado
            img = Image.new('RGB', (width, height), params['background_color'])
            frames.append(np.array(img))
        
        # Crear el clip de video y guardarlo
        clip = ImageSequenceClip(frames, fps=fps)
        clip.write_videofile(output_path,
                             codec='libx264',
                             preset='ultrafast',
                             fps=fps,
                             threads=2,
                             logger=None,
                             audio=False)
        
        clip.close()
        
        return output_filename, None
    
    except Exception as e:
        print(f"\nError durante la generación del video: {e}")
        traceback.print_exc()
        return None, f"Error durante la generación del video: {e}"
