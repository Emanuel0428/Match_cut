# Text Match Cut Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un generador de videos con efectos de texto dinámicos, enfocado en crear transiciones suaves y efectos visuales atractivos. Este proyecto es una versión mejorada y personalizada, basada en la idea original de [lrdcxdes](https://github.com/lrdcxdes/text-match-cut).

## 🚀 Características Principales

* **Interfaz Web Intuitiva** - Diseño moderno y fácil de usar
* **Efectos Visuales Avanzados:**
  * Desenfoque radial y gaussiano personalizables
  * Texturas de fondo predefinidas y personalizadas
  * Resaltado dinámico de texto
  * Previsualización de texturas
* **Múltiples Proveedores de IA:**
  * Mistral AI
  * Google Gemini
  * Anthropic Claude
  * DeepSeek
* **Personalización Completa:**
  * Colores de texto y fondo
  * Dimensiones del video
  * Duración y FPS ajustables
  * Selección de fuentes tipográficas
  * Subida de texturas personalizadas

## 🛠️ Requisitos

* Python 3.8+
* FFmpeg
* Paquetes de Python listados en `requirements.txt`
* API Key (opcional, para generación de texto con IA)

## 📦 Instalación

1. **Clonar el Repositorio:**
   ```bash
   git clone https://github.com/Emanuel0428/Match_cut.git
   cd Match_cut
   ```

2. **Configurar Entorno Virtual:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Instalar Dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Recursos Adicionales:**
   * Coloca fuentes `.ttf` o `.otf` en la carpeta `fonts/`
   * Agrega imágenes de textura en la carpeta `media/`

## 🎮 Uso

1. **Iniciar la Aplicación:**
   
   **Desarrollo (con recarga automática):**
   ```bash
   # Usando el script de inicio
   start_dev.bat
   
   # O manualmente
   python app.py
   ```
   
   **Producción (con múltiples workers):**
   ```bash
   # Usando el script de inicio
   start_prod.bat
   
   # O manualmente
   gunicorn -c gunicorn_config.py app:app
   ```

2. **Acceder a la Interfaz:**
   * Abre `http://127.0.0.1:5000` en tu navegador

3. **Crear tu Video:**
   * Escribe el texto a resaltar
   * Selecciona una fuente tipográfica
   * Escoge una textura de fondo existente o sube la tuya
   * Configura los efectos visuales y colores
   * ¡Genera y descarga tu video!

## 📁 Estructura del Proyecto

```
Match_cut/
├── app.py                  # Aplicación principal (Flask)
├── gunicorn_config.py      # Configuración para despliegue con Gunicorn
├── start_dev.bat           # Script de inicio para desarrollo (Windows)
├── start_prod.bat          # Script de inicio para producción (Windows)
├── requirements.txt        # Dependencias
├── modules/                # Módulos organizados por funcionalidad
│   ├── __init__.py        
│   ├── ai_providers.py     # Integración con APIs de IA
│   ├── image_processing.py # Procesamiento de imágenes y texto
│   ├── textures.py         # Manejo de texturas y efectos visuales
│   ├── text_generation.py  # Generación de texto (aleatoria)
│   └── video_generator.py  # Generador del video final
├── templates/         
│   └── index.html          # Interfaz web
├── static/
│   └── style.css           # Estilos
├── fonts/                  # Fuentes tipográficas
├── media/                  # Texturas de fondo
└── output/                 # Videos generados
```

## ✨ Mejoras Implementadas

* Estructura de código modular y organizada
* Soporte para texturas de fondo y subida de texturas personalizadas
* Sistema mejorado de desenfoque radial
* Mejor manejo de texto y posicionamiento
* Interfaz de usuario modernizada con previsualización de elementos
* Selección de fuentes tipográficas
* Soporte para múltiples proveedores de IA
* Sistema robusto de manejo de errores
* Configuración para despliegue en producción con Gunicorn
* Scripts de inicio automatizados para Windows

## 🤝 Créditos

Este proyecto es una versión mejorada basada en el trabajo original de [lrdcxdes](https://github.com/lrdcxdes/text-match-cut). Las mejoras y modificaciones fueron realizadas por [Emanuel0428](https://github.com/Emanuel0428).

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si encuentras un bug o tienes una sugerencia:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request
