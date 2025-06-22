import requests
import time
import os


class Api_aigo:
    def __init__(self):
        self.identity_auth = os.getenv(
            "AIGOSTAR_IDENTITY_AUTH", "default_identity_auth"
        )
        self.api_key = os.getenv("AIGOSTAR_API_KEY", "default_api_key")
        self.tenant_id = os.getenv("AIGOSTAR_TENANT_ID", "default_tenant_id")
        self.api_url = os.getenv(
            "AIGOSTAR_API_URL", "https://b2b-api.aigostar.com/api/v1.0/"
        )
        self.token_timestamp = 0

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
                self.token_timestamp = time.time()
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
        response = requests.post(url=url_product, headers=headers)
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

    def get_time_expiration(self):
        return self.token_timestamp
