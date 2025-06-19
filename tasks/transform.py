from prefect import task, get_run_logger
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import re
from datetime import datetime
import json
from io import BytesIO

def image_to_text(image_bytes):
    # 1. Cargar imagen y convertir a RGB
    img = Image.open(BytesIO(image_bytes)).convert("RGB")

    # 2. Eliminar fondo amarillo/naranja
    clean = Image.new("RGB", img.size, "white")
    pixels = img.load()
    pixels_clean = clean.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            if r > 180 and g > 130 and b < 110:  # Más estricto con el amarillo/naranja
                pixels_clean[x, y] = (255, 255, 255)
            else:
                pixels_clean[x, y] = (r, g, b)

    # 3. Convertir a escala de grises
    gray = clean.convert("L")

    # 4. Mejorar contraste y nitidez de bordes
    gray = ImageOps.autocontrast(gray)
    gray = ImageEnhance.Contrast(gray).enhance(1.8)  # Aumenta contraste aún más

    # 5. Redimensionar (clave para Tesseract)
    scale = 2
    resized = gray.resize(
        (gray.width * scale, gray.height * scale),
        resample=Image.LANCZOS
    )

    # 6. Binarización (umbral más fino)
    np_img = np.array(resized)
    threshold = 150  # Ligeramente más bajo para captar grises claros
    binary_np = np.where(np_img > threshold, 255, 0).astype(np.uint8)
    binary = Image.fromarray(binary_np)

    # 7. OCR
    custom_config = r'--oem 3 --psm 11 -l spa'
    raw_text = pytesseract.image_to_string(binary, config=custom_config)

    return raw_text

@task
def text_to_dict(image_bytes) -> json:
    logger = get_run_logger()
    # get text
    text = image_to_text(image_bytes, logger)
    
    # Transforming text to structured data
    farmacias = []
    lines = text.upper().replace("%", "°").splitlines()

    current = {}
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Detectar fecha
        fecha_match = re.match(r"(\d{2})/(\d{2})", line)
        if fecha_match:
            current["fecha"] = f"2025-{fecha_match.group(2)}-{fecha_match.group(1)}"
            continue

        # Nombre farmacia
        if line.startswith("FAR."):
            current["nombre_farmacia"] = line
            continue

        # Dirección
        if "DIR" in line.upper() or "DIRECION" in line.upper():
            direccion = re.sub(r"(?i)^.*?dir\w*[:;]?", "", line).strip()
            current["direccion_farmacia"] = direccion
            continue

        # Teléfono
        if "TELEFONO" in line.upper():
            numero = re.sub(r"(?i)telefono[:;]?", "", line).strip()
            current["numero_farmacia"] = numero
            # Cuando ya tenemos todo, guardamos y reiniciamos
            if "nombre_farmacia" in current and "direccion_farmacia" in current and "fecha" in current:
                farmacias.append(current)
            current = {}

    # Mostrar resultado final
    return farmacias