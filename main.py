import aigostar
import json
import pandas as pd
import re
import requests
from qreader import QReader
import cv2
import numpy as np
from urllib.parse import urlparse
import time

URL_PRINCIPAL_IMAGE = "https://aigo-oss-mall.oss-accelerate.aliyuncs.com/"
COLUMNAS = [
    "NOMBRE",
    "REF/SKU",
    "EAN",
    "EPREL",
    "EEI",
    "PRECIO",
    "PESO",
    "ALTO",
    "LARGO",
    "ANCHO"
]
data_excel = pd.read_excel("Eprel-Aigostar-29-5.xlsx", sheet_name="Sheet")
aigo = aigostar.Api_aigo()
access_token = aigo.api_auth()
token_expiration = 3590
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
}


def generate_products_excel(data_excel, access_token):
    """
    Generate a new Excel file with the product information from Aigostar.
    """
    data = []
    for index, row in data_excel.iterrows():
        ean = row["ean_proveedor"]
        product_info = aigo.get_info(access_token, ean)
        if (time.time() - aigo.get_time_expiration()) > token_expiration:
            access_token = aigo.api_auth() 
            print("Token refrescado")
        if product_info:
            try:
                for item in product_info:
                    parameters = transform_parameters(json.loads(item["parameter"]))
                    dimensions = get_dimensions(dimension = parameters.get("Dimensión", "") or "")
                    eei = parameters = parameters.get("EEI", "") or ""
                    if item["mainImages"] is not None:
                        images_list = json.loads(item["mainImages"])
                    eprel = get_eprel(images_list = images_list)
                data.append(
                            {
                                "NOMBRE": item["appName"],
                                "REF/SKU": item["goodsCode"],
                                "EAN": ean,
                                "EPREL": eprel,
                                "EEI": eei,
                                "PRECIO": aigo.get_price(access_token, ean),
                                "PESO": item["peso"]*1000,
                                "ALTO": dimensions["alto"],
                                "LARGO": dimensions["largo"],
                                "ANCHO": dimensions["ancho"]
                            }
                        )
                print(f"Procesando {ean}")
            except Exception as e:
                print(e)
        else:
            data.append(
                {
                    "EAN": ean,
                    "EPREL": "", 
                }
            )
        df = pd.DataFrame(data, columns=COLUMNAS)
        df.to_excel("productos_aigostar_datos-29-5.xlsx", index=False)

def transform_parameters(parameters):
   return {param["ExtName"]: param["ExtValue"] for param in parameters}

def get_dimensions(dimension):
#   {\"ExtValue\":\"D45*H80mm\"
    values = re.findall(r'\d+',dimension)
    return({
        "alto":values[0] if len(values) > 0 else "0",
        "largo":values[1] if len(values) > 1 else "0",
        "ancho":values[2] if len(values) > 2 else "0"
    })
def get_eprel(images_list):
    qreader = QReader()
    for url in images_list:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                image_cv = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                decoded_text = qreader.detect_and_decode(image=image_cv)
                if decoded_text:
                    parsed_url = urlparse(decoded_text[0])
                    if parsed_url[1] == 'eprel.ec.europa.eu':
                        path = parsed_url[2]
                        eprel_code = path.strip('/').split('/')[-1]
                        print(f"QR encontrado en {url}: {decoded_text}")
                        return eprel_code
                    else:
                        print(f"No se pudo descargar la imagen: {url}")
        except Exception as e:
            print(f"Error procesando la imagen {url}: {e}")
    return ""


generate_products_excel(data_excel, access_token)
