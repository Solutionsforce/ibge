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
            headers = {
                'x-api-key': '3d6bd4c17dd31877b77482b341c74d32494a1d6fbdee4c239cf8432b424b1abf'
            }
            response = requests.get(f"{self.endpoint}/{cep}", headers=headers, timeout=10)
            return response.json()
        except requests.RequestException as e:
            return {
                "success": False,
                "message": "Erro ao consultar CEP",
                "error": str(e)
            }