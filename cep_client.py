"""
CEP Consultation Client - Simplified Implementation
===================================================
Cliente simplificado para consulta de CEP via API
"""

import requests

class CEPConsultationClient:
    def __init__(self, base_url):
        self.endpoint = f"{base_url.rstrip('/')}/external/cep"

    def consult(self, cep):
        try:
            response = requests.get(f"{self.endpoint}/{cep}", timeout=10)
            return response.json()
        except requests.RequestException as e:
            return {
                "success": False,
                "message": "Erro ao consultar CEP",
                "error": str(e)
            }