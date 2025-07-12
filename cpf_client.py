"""
CPF Consultation Client - Simplified Implementation
==================================================
Cliente simplificado para consulta de CPF via PayBets
"""

import requests

class CPFConsultationClient:
    def __init__(self, base_url):
        self.endpoint = f"{base_url.rstrip('/')}/external/cpf"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": "3d6bd4c17dd31877b77482b341c74d32494a1d6fbdee4c239cf8432b424b1abf"
        }

    def consult(self, cpf):
        try:
            response = requests.get(f"{self.endpoint}/{cpf}", headers=self.headers, timeout=10)
            return response.json()
        except requests.RequestException as e:
            return {
                "success": False,
                "message": "Erro ao consultar CPF",
                "error": str(e)
            }

# Instância global para uso na aplicação
cpf_client = CPFConsultationClient(
    base_url="https://elite-manager-api-62571bbe8e96.herokuapp.com/api"
)