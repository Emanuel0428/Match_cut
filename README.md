# Text Match Cut Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un generador de videos con efectos de texto dinámicos, enfocado en crear transiciones suaves y efectos visuales atractivos. Este proyecto es una versión mejorada y personalizada, basada en la idea original de [lrdcxdes](https://github.com/lrdcxdes/text-match-cut).

## 🚀 Características Principales

* **Interfaz Web Intuitiva** - Diseño moderno y fácil de usar
* **Efectos Visuales Avanzados:**
  * Desenfoque radial y gaussiano personalizables
  * Texturas de fondo predefinidas
  * Resaltado dinámico de texto
* **Múltiples Proveedores de IA:**
  * Mistral AI
  * Google Gemini
  * Anthropic Claude
  * DeepSeek
* **Personalización Completa:**
  * Colores de texto y fondo
  * Dimensiones del video
  * Duración y FPS ajustables
  * Fuentes personalizables

## 🛠️ Requisitos

* Python 3.8+
* FFmpeg
* Paquetes de Python listados en `requirements.txt`
* API Key (opcional, para generación de texto con IA)

## 📦 Instalación

1. **Clonar el Repositorio:**
   ```bash
   git clone https://github.com/Emanuel0428/text-match-cut.git
   cd text-match-cut
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
   ```bash
   python app.py
   ```

2. **Acceder a la Interfaz:**
   * Abre `http://127.0.0.1:5000` en tu navegador

3. **Crear tu Video:**
   * Escribe el texto a resaltar
   * Selecciona una textura de fondo o color sólido
   * Configura los efectos visuales
   * ¡Genera y descarga tu video!

## 📁 Estructura del Proyecto

```
text-match-cut/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── templates/         
│   └── index.html     # Interfaz web
├── static/
│   └── style.css      # Estilos
├── fonts/             # Fuentes tipográficas
├── media/             # Texturas
└── output/            # Videos generados
```

## ✨ Mejoras Implementadas

* Soporte para texturas de fondo
* Sistema mejorado de desenfoque radial
* Mejor manejo de texto y posicionamiento
* Interfaz de usuario modernizada
* Soporte para múltiples proveedores de IA
* Sistema robusto de manejo de errores

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
