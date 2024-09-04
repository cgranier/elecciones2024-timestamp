
# Extractor de Timestamps de Imágenes

## Descripción

Este proyecto está diseñado para extraer marcas de tiempo (timestamps) de una serie de imágenes utilizando Reconocimiento Óptico de Caracteres (OCR). Procesa un archivo CSV que contiene URLs de imágenes, descarga las imágenes, realiza OCR para extraer las marcas de tiempo y actualiza el CSV con los resultados. El script incluye características como rotación de imágenes para mejorar la detección de timestamps y un manejo eficiente de archivos previamente procesados.

## Características

- Extrae marcas de tiempo de imágenes usando OCR
- Maneja grandes conjuntos de datos de manera eficiente
- Retoma el procesamiento interrumpido
- Rota las imágenes si las marcas de tiempo no son detectadas inicialmente
- Elimina duplicados en la salida del archivo CSV
- Guarda imágenes rotadas para análisis adicional

## Requisitos

- Python 3.6+
- Tesseract OCR
- Librerías de Python: PIL (Pillow), pytesseract, requests

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/yourusername/image-timestamp-extractor.git
   cd image-timestamp-extractor
   ```

2. Instala las librerías de Python requeridas:
   ```bash
   pip install -r requirements.txt
   ```

3. Instala Tesseract OCR:
   - Para Windows: Descarga e instala desde [GitHub Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki)
   - Para macOS: `brew install tesseract`
   - Para Linux: `sudo apt-get install tesseract-ocr`

4. Configura la ruta del ejecutable de Tesseract en el script si no está en la variable PATH del sistema.

## Uso

1. Prepara tu archivo CSV de entrada (por ejemplo, `resultados-macedonia-del-norte.csv`) con al menos una columna 'URL' que contenga las URLs de las imágenes.

2. Actualiza el script con las rutas y configuraciones específicas:
   - `input_csv`: Ruta a tu archivo CSV de entrada
   - `output_csv`: Ruta para el archivo CSV de salida
   - `image_dir`: Directorio donde se almacenarán las imágenes descargadas

3. Ejecuta el script:
   ```bash
   python ocr-time.py
   ```

4. El script procesará las imágenes y actualizará el archivo CSV de salida con las marcas de tiempo extraídas.

## Salida

- Archivo CSV actualizado con una nueva columna 'timestamp'
- Imágenes rotadas (si las hay) guardadas con el sufijo '_rotated' en el directorio de imágenes

## Solución de Problemas

- Si Tesseract no se encuentra, asegúrate de que esté instalado y de que la ruta esté correctamente configurada en el script.
- Para problemas con el procesamiento de imágenes, revisa los permisos del directorio de imágenes y el espacio disponible en disco.

## Contribuciones

Las contribuciones para mejorar el script o ampliar su funcionalidad son bienvenidas. Por favor, envía un pull request o abre un issue para discutir los cambios propuestos.

## Licencia

[Licencia MIT](LICENSE)

## Contacto

Para cualquier consulta o soporte, por favor abre un issue en el repositorio de GitHub.
