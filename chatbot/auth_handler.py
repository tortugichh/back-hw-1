import requests
from config import settings

class AuthHandler:
    def __init__(self):
        self.token = None
        self.fastapi_base_url = settings.fastapi_base_url
        self.username = settings.chatbot_username
        self.password = settings.chatbot_password

    def _get_new_token(self):
        token_url = f"{self.fastapi_base_url}/auth/token"
        response = requests.post(token_url, data={
            "username": self.username,
            "password": self.password,
        })
        response.raise_for_status() # Raise an exception for HTTP errors
        token_data = response.json()
        self.token = token_data["access_token"]
        return self.token

    def get_token(self):
        if not self.token:
            self._get_new_token()
        return self.token

    def get_authorized_headers(self):
        return {
            "Authorization": f"Bearer {self.get_token()}"
        }

auth_handler = AuthHandler() 