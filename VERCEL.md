# Despliegue en Vercel

Este proyecto está configurado para ser desplegado en la plataforma serverless de Vercel.

## Estructura del proyecto para Vercel

- `vercel_app.py`: Aplicación principal Flask adaptada para Vercel
- `index.py`: Punto de entrada para Vercel
- `vercel.json`: Configuración específica para Vercel
- `vercel_modules/`: Módulos simplificados para el entorno serverless
  - `video_generator.py`: Versión adaptada del generador de videos
  - `__init__.py`: Archivo que hace que vercel_modules sea un paquete Python

## Limitaciones del despliegue en Vercel

Debido a las restricciones del entorno serverless de Vercel, se han implementado las siguientes limitaciones:

1. **Resolución máxima**: 1920x1080 píxeles
2. **Duración máxima**: 10 segundos
3. **APIs de IA**: Desactivadas temporalmente para evitar problemas con las credenciales y los tokens

## Pasos para desplegar

1. Asegúrate de tener una cuenta en Vercel (vercel.com)
2. Instala el CLI de Vercel: `npm i -g vercel`
3. Ejecuta `vercel login` para iniciar sesión
4. Desde la raíz del proyecto, ejecuta `vercel` para desplegar

## Variables de entorno

Las siguientes variables de entorno están configuradas en `vercel.json`:

- `PYTHONPATH`: Directorio raíz del proyecto
- `UPLOAD_FOLDER`: Directorio temporal para los videos generados
- `FONT_DIR`: Directorio de fuentes
- `MEDIA_DIR`: Directorio de archivos multimedia

## Estructura de archivos

```
.
├── app.py                   # Aplicación principal (local)
├── vercel_app.py            # Aplicación adaptada para Vercel
├── index.py                 # Punto de entrada para Vercel
├── vercel.json              # Configuración de Vercel
├── requirements.txt         # Dependencias para desarrollo local
├── requirements-vercel.txt  # Dependencias optimizadas para Vercel
├── modules/                 # Módulos para desarrollo local
└── vercel_modules/          # Módulos adaptados para Vercel
```
