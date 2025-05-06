import aigostar
import json
import pandas as pd
import re

URL_PRINCIPAL_IMAGE = "https://aigo-oss-mall.oss-accelerate.aliyuncs.com/"
COLUMNAS = [
    "NOMBRE",
    "REF/SKU",
    "EAN",
    "PRECIO",
    "PESO",
    "LARGO",
    "ANCHO",
    "ALTO",
    "IMAGEN",
]
data_excel = pd.read_excel("aigostar_nuevos_productos.xlsx", sheet_name="Hoja1")
aigo = aigostar.Api_aigo()
access_token = aigo.api_auth()


def generate_products_excel(data_excel, access_token):
    """
    Generate a new Excel file with the product information from Aigostar.
    """
    data = []
    for index, row in data_excel.iterrows():
        ean = row["Código barra"]
        product_info = aigo.get_info(access_token, ean)
        if product_info:
            for item in product_info:
                largo = 0
                ancho = 0
                alto = 0
                parameters = json.loads(item["parameter"])
                for parameter in parameters:
                    if parameter["ExtName"] == "Dimensión":
                        parameter_value = parameter["ExtValue"]
                        matches = re.findall(
                            r"L(\d+\.?\d*)\*W(\d+\.?\d*)\*H(\d+\.?\d*)", parameter_value
                        )

                        # Convertir los valores a números
                        largos = []
                        anchos = []
                        altos = []

                        for match in matches:
                            largo, ancho, alto = map(float, match)
                            largos.append(largo)
                            anchos.append(ancho)
                            altos.append(alto)

                        # Obtener los valores máximos
                        largo = max(largos)
                        ancho = max(anchos)
                        alto = max(altos)

                data.append(
                    {
                        "NOMBRE": item["appName"],
                        "REF/SKU": item["goodsCode"],
                        "EAN": ean,
                        "PRECIO": aigo.get_price(access_token, ean),
                        "PESO": item["peso"],
                        "LARGO": largo,
                        "ANCHO": ancho,
                        "ALTO": alto,
                        "IMAGEN": f"{URL_PRINCIPAL_IMAGE}{item['imageUrl']}",
                    }
                )
            print(f"EAN: {ean} - {item['name']}")
        else:
            data.append(
                {
                    "NOMBRE": "",
                    "REF/SKU": "",
                    "EAN": ean,
                    "PRECIO": "",
                    "PESO": "",
                    "LARGO": "",
                    "ANCHO": "",
                    "ALTO": "",
                    "IMAGEN": "",
                }
            )
    df = pd.DataFrame(data, columns=COLUMNAS)
    df.to_excel("productos_aigostar_datos.xlsx", index=False)


generate_products_excel(data_excel, access_token)
