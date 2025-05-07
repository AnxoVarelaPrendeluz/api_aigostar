import requests


class Api_aigo:
    def __init__(self):
        self.identity_auth = 565569746200846336
        self.api_key = "46949eb9b19bbac16aaf931f68100269"
        self.tenant_id = 1436164625564569600
        self.api_url = "https://b2b-api.aigostar.com/api/v1.0/"

    def api_auth(self):

        url_auth = f"{self.api_url}open_api/auth?clientId={self.identity_auth}&clientSecret={self.api_key}"
        headers = {
            "Content-Type": "application/json",
            "tenantid": str(self.tenant_id),
        }
        response = requests.get(url_auth, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["access_token"]:
                access_token = data["access_token"]
                return access_token
            else:
                print(f"Error: {data['message']}")
                return None
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None

    def get_info(self, access_token, ean):
        url_product = f"{self.api_url}open_api/goods?barCode={ean}&lang=es&limit=1"
        headers = {
            "Content-Type": "application/json",
            "tenantid": str(self.tenant_id),
            "authorization": f"Bearer {access_token}",
        }
        response = requests.get(url_product, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["total"] > 0:
                return data["list"]
            else:
                print(f"Error: ean: {ean} not found")
                return None
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None

    def get_price(self, access_token, ean):
        url_product = (
            f"{self.api_url}open_api/goods/price?barCode={ean}&lang=es&limit=1"
        )
        headers = {
            "Content-Type": "application/json",
            "tenantid": str(self.tenant_id),
            "authorization": f"Bearer {access_token}",
        }
        response = requests.post(url = url_product, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["total"] > 0:
                return data["list"][0]["price"]
            else:
                print(f"Error: ean: {ean} not found")
                return None
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None
