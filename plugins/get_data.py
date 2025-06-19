import requests
import os

def get_data():
    url_snap_id = "https://api.brightdata.com/datasets/v3/snapshot/" + 's_mc3rkp3w20n56uo056'
    token = os.getenv("BRIGHTDATA_TOKEN")
    headers_snap_id = {
        "Authorization": f"Bearer {token}",
    }
    params_snap_id = {
        "format": "json",
    }

    response = requests.get(url_snap_id, headers=headers_snap_id, params=params_snap_id)
    img_url = response.json()[0]['posts'][0]['image_url']
    image_bytes = requests.get(img_url).content  # This will trigger the image download
    return image_bytes