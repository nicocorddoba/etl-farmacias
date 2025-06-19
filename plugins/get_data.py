import requests
import os
import time

def request_data(token):
    # Solicitar extraccion de datos a Bright Data
    url = "https://api.brightdata.com/datasets/v3/trigger"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    params = {
        "dataset_id": "gd_l1vikfch901nx3by4",
        "include_errors": "true",
    }
    data = {
        "input": [{"url":os.getenv("FB_URL")}],
        "custom_output_fields": ["account","posts"],
    }

    response = requests.post(url, headers=headers, params=params, json=data)
    return response.json()['snapshot_id']

def await_for_ready(token, snapshot_id):
    # Esperar hasta que el snapshot esté listo
    url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    max_reintentos = 3
    retraso_entre_intentos = 30  # segundos

    for intento in range(max_reintentos):
        time.sleep(retraso_entre_intentos)  # Esperar antes de cada intento
        response = requests.get(url, headers=headers)
        data = response.json()

        if data.get("status") == "ready":
            break
        else:
            print(f"Intento {intento+1}: estado = {data.get('status')}, esperando...")
    else:
        raise Exception(f"El snapshot {snapshot_id} no está listo después de {max_reintentos} intentos.")


def get_data():
    token = os.getenv("BRIGHTDATA_TOKEN")
    snapshot_id = request_data(token)
    await_for_ready(token, snapshot_id)
    # Si snapshot listo:
    ## Get data:
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    params = {
        "format": "json",
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        img_url = response.json()[0]['posts'][0]['image_url']
        image_bytes = requests.get(img_url).content  # Descarga la imagen en bytes
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        raise e
    return image_bytes
