"""
PayBets PIX Client - Simplified Implementation
==============================================
Cliente simplificado para geração de PIX via PayBets
"""

import requests

class PayBetsPixClient:
    def __init__(self, base_url):
        self.endpoint = f"{base_url.rstrip('/')}/payments/paybets/pix/generate"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": "3d6bd4c17dd31877b77482b341c74d32494a1d6fbdee4c239cf8432b424b1abf"
        }

    def generate_pix(self, amount, external_id, callback_url, name, email, document):
        payload = {
            "amount": amount,
            "external_id": external_id,
            "clientCallbackUrl": callback_url,
            "name": name,
            "email": email,
            "document": document
        }

        try:
            response = requests.post(self.endpoint, json=payload, headers=self.headers, timeout=10)
            return response.json()
        except requests.RequestException as e:
            return {
                "success": False,
                "message": "Erro ao comunicar com a API",
                "error": str(e)
            }

# Instância global para uso na aplicação
paybets_client = PayBetsPixClient(
    base_url="https://elite-manager-api-62571bbe8e96.herokuapp.com/api"
)