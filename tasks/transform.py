from prefect import task, get_run_logger
from PIL import Image, ImageFilter
import pytesseract
import re
from datetime import datetime
import json

def image_to_text(response):
    # Abrir imagen
    img = Image.open(response.body).convert("RGB")  # Asegurate que esté en modo RGB

    # Crear una nueva imagen blanca del mismo tamaño
    new_img = Image.new("RGB", img.size, "white")

    # Obtener píxeles
    pixels = img.load()
    pixels_nueva = new_img.load()

    # Reemplazar colores "amarillos" por blanco
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            # Umbral para detectar "amarillo claro"
            if r > 230 and g > 130 and b < 40:
                pixels_nueva[x, y] = (255, 255, 255)  # Blanco
            else:
                pixels_nueva[x, y] = (r, g, b)  # Conservar original

    # Convertir la nueva imagen a escala de grises
    imagen = new_img.convert("L")

    # Filtros para mejorar detección de texto
    imagen = imagen.filter(ImageFilter.MedianFilter())  # Suaviza ruido de fondo

    # OCR
    custom_config = r'--oem 3 --psm 6'  # o --psm 4/11 también puede probarse
    text = pytesseract.image_to_string(imagen, lang="spa", config=custom_config)
    return text

@task
def text_to_json(response) -> json:
    text = image_to_text(response)
    lineas = [l.strip() for l in text.replace("?", "°").splitlines() if l.strip()]
    data = []

    i = 0
    while i < len(lineas) - 1:
        linea_farmacia = lineas[i]
        linea_detalle = lineas[i + 1]

        # Buscar nombre farmacia
        nombre_match = re.search(r"(FAR\.\s?.+)", linea_farmacia, re.IGNORECASE)
        nombre = nombre_match.group(1).strip() if nombre_match else None

        # Buscar fecha
        fecha_match = re.search(r"(\d{2}/\d{2})", linea_detalle)
        if fecha_match:
            fecha_str = fecha_match.group(1) + "/2025"
            fecha = datetime.strptime(fecha_str, "%d/%m/%Y").date().isoformat()
        else:
            fecha = None

        # Buscar dirección
        direccion_match = re.search(r"(DIRECCIÓN|DIRECION|DIR):\s*(.+?)\s*TELEFONO", linea_detalle, re.IGNORECASE)
        direccion = direccion_match.group(2).strip() if direccion_match else None

        # Buscar teléfono
        telefono_match = re.search(r"TELEFONO[:\s]*([0-9\-]+)", linea_detalle)
        telefono = telefono_match.group(1).strip() if telefono_match else None

        if nombre and fecha and direccion and telefono:
            data.append({
                "fecha": fecha,
                "nombre_farmacia": nombre.upper(),
                "direccion_farmacia": direccion,
                "numero_farmacia": telefono
            })

        i += 2  # avanzar al siguiente par línea

    # Mostrar JSON resultante
    return json.dumps(data, indent=2, ensure_ascii=False)