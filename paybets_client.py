"""
PayBets API Client - Simplified Implementation
=============================================
Cliente simplificado para integração com API PayBets
"""

import requests
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PayBetsPixClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url.rstrip('/')
        self.pix_endpoint = f"{self.base_url}/payments/paybets/pix/generate"
        self.cpf_endpoint = f"{self.base_url}/external/cpf"
        self.api_key = api_key or "3d6bd4c17dd31877b77482b341c74d32494a1d6fbdee4c239cf8432b424b1abf"
        
        # Headers padrão
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key
        }

    def generate_pix(self, amount, external_id, callback_url, name, email, document):
        """
        Gerar pagamento PIX via PayBets
        
        Args:
            amount: Valor em reais
            external_id: ID externo único
            callback_url: URL para callback
            name: Nome do pagador
            email: Email do pagador
            document: CPF do pagador
            
        Returns:
            Dict com resposta da API
        """
        payload = {
            "amount": float(amount),
            "external_id": external_id,
            "clientCallbackUrl": callback_url,
            "name": name,
            "email": email,
            "document": document
        }

        try:
            logger.info(f"Generating PIX payment - Amount: R$ {amount}, External ID: {external_id}")
            response = requests.post(
                self.pix_endpoint, 
                json=payload, 
                headers=self.headers,
                timeout=10
            )
            
            logger.info(f"PIX API response: HTTP {response.status_code}")
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"PIX generation error: {str(e)}")
            return {
                "success": False,
                "message": "Erro ao comunicar com a API",
                "error": str(e)
            }

    def consult_cpf(self, cpf):
        """
        Consultar dados de CPF via PayBets
        
        Args:
            cpf: CPF para consulta (apenas números)
            
        Returns:
            Dict com dados do CPF ou erro
        """
        # Limpar CPF (apenas números)
        cpf_clean = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf_clean) != 11:
            return {
                "success": False,
                "message": "CPF deve ter 11 dígitos"
            }
        
        try:
            logger.info(f"Consulting CPF: {cpf_clean[:3]}***{cpf_clean[-2:]}")
            response = requests.get(
                f"{self.cpf_endpoint}/{cpf_clean}",
                headers=self.headers,
                timeout=10
            )
            
            logger.info(f"CPF API response: HTTP {response.status_code}")
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"CPF consultation error: {str(e)}")
            return {
                "success": False,
                "message": "Erro ao comunicar com a API",
                "error": str(e)
            }

# Instância global para uso na aplicação
paybets_client = PayBetsPixClient(
    base_url="https://elite-manager-api-62571bbe8e96.herokuapp.com/api"
)