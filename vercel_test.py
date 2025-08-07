"""
Script para probar el despliegue de Vercel localmente
"""
import http.server
import socketserver
import os
import sys

PORT = 8000

class VercelHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Para simular el comportamiento de Vercel, redirigimos todas las peticiones
        # al archivo index.py si no son archivos estáticos
        
        # Archivos estáticos que deben ser servidos directamente
        static_exts = ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico', '.ttf', '.otf']
        
        if any(self.path.endswith(ext) for ext in static_exts):
            # Servir archivos estáticos directamente
            return super().do_GET()
        else:
            # Cualquier otra ruta se redirige a la aplicación Flask
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # En un entorno real, aquí invocaríamos a la aplicación Flask
            # Por simplicidad, solo mostramos un mensaje informativo
            message = """
            <html>
            <head>
                <title>Simulación de Vercel</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 40px auto;
                        padding: 20px;
                        line-height: 1.6;
                    }}
                    pre {{
                        background: #f4f4f4;
                        border-left: 3px solid #f36d33;
                        padding: 15px;
                        overflow: auto;
                    }}
                    .info {{
                        background: #e8f5ff;
                        border-left: 4px solid #2196F3;
                        padding: 10px 20px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <h1>Simulación de Vercel</h1>
                <div class="info">
                    <p>Esta es una simulación local del entorno de Vercel. En un despliegue real, 
                    esta ruta sería procesada por la aplicación Flask.</p>
                </div>
                <h2>Información de la solicitud:</h2>
                <pre>
                Ruta: {path}
                </pre>
                <p>Para probar la aplicación real:</p>
                <ol>
                    <li>Ejecuta <code>flask run</code> en una terminal</li>
                    <li>Accede a <a href="http://localhost:5000">http://localhost:5000</a></li>
                </ol>
                <p>Para desplegar en Vercel:</p>
                <ol>
                    <li>Instala Vercel CLI: <code>npm i -g vercel</code></li>
                    <li>Ejecuta <code>vercel login</code> para iniciar sesión</li>
                    <li>Ejecuta <code>vercel</code> desde la raíz del proyecto</li>
                </ol>
            </body>
            </html>
            """.format(path=self.path)
            
            self.wfile.write(message.encode())
            return

def run_server():
    with socketserver.TCPServer(("", PORT), VercelHandler) as httpd:
        print(f"Simulando servidor Vercel en http://localhost:{PORT}")
        print("Ctrl+C para detener")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
