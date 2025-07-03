"""
For4Payments PIX API Integration
================================
Integração completa para pagamentos PIX usando a API For4Payments.
"""
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PaymentRequestData:
    """
    Dados necessários para criar um pagamento PIX
    """
    name: str
    email: str
    cpf: str
    amount: int  # Valor em centavos
    phone: Optional[str] = None
    description: Optional[str] = None

@dataclass
class PaymentResponse:
    """
    Resposta da criação de pagamento PIX
    """
    id: str
    pix_code: str
    pix_qr_code: str
    expires_at: str
    status: str

class For4PaymentsAPI:
    """
    Classe principal para integração com a API For4Payments
    """
    
    def __init__(self, secret_key: str):
        """
        Inicializar a API com chave de autenticação
        """
        self.API_URL = "https://app.for4payments.com.br/api/v1"
        self.secret_key = secret_key
        
        # Validar chave de API
        if not secret_key or len(secret_key) < 10:
            raise ValueError("Token de autenticação inválido")
    
    @classmethod
    def from_env(cls) -> 'For4PaymentsAPI':
        """
        Criar instância da API usando variável de ambiente
        """
        secret_key = os.getenv("FOR4PAYMENTS_SECRET_KEY")
        
        if not secret_key:
            raise ValueError(
                "Chave de API FOR4PAYMENTS_SECRET_KEY não configurada no ambiente"
            )
        
        return cls(secret_key)
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Headers padrão para as requisições HTTP
        """
        return {
            "Authorization": self.secret_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "For4Payments-Python-SDK/1.0.0",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        }
    
    def _validate_payment_data(self, data: PaymentRequestData) -> None:
        """
        Validar dados do pagamento antes do envio
        """
        # Validar campos obrigatórios
        if not data.name or not data.name.strip():
            raise ValueError("Nome é obrigatório")
        if not data.email or not data.email.strip():
            raise ValueError("Email é obrigatório")
        if not data.cpf or not data.cpf.strip():
            raise ValueError("CPF é obrigatório")
        if not data.amount or data.amount <= 0:
            raise ValueError("Valor é obrigatório e deve ser maior que zero")
        
        # Validar e formatar CPF
        cpf = ''.join(filter(str.isdigit, data.cpf))
        if len(cpf) != 11:
            raise ValueError("CPF deve conter exatamente 11 dígitos")
        
        # Validar email básico
        if "@" not in data.email or "." not in data.email:
            raise ValueError("Email inválido")
        
        # Validar valor
        if not isinstance(data.amount, int) or data.amount <= 0:
            raise ValueError("Valor deve ser um número inteiro positivo em centavos")
    
    def create_pix_payment(self, data: PaymentRequestData) -> PaymentResponse:
        """
        Criar um pagamento PIX
        """
        
        # Validar dados de entrada
        self._validate_payment_data(data)
        
        # Processar e formatar dados
        cpf = ''.join(filter(str.isdigit, data.cpf))
        phone = ''.join(filter(str.isdigit, data.phone)) if data.phone else "11999999999"
        
        # Construir payload completo para a API
        payment_data = {
            "name": data.name.strip(),
            "email": data.email.strip(),
            "cpf": cpf,
            "phone": phone,
            "paymentMethod": "PIX",
            "amount": data.amount,
            "traceable": True,
            "items": [
                {
                    "title": data.description or "Pagamento PIX",
                    "quantity": 1,
                    "unitPrice": data.amount,
                    "tangible": False
                }
            ],
            # Dados de endereço (obrigatórios)
            "cep": "01001000",
            "street": "Praça da Sé",
            "number": "1",
            "complement": "",
            "district": "Sé",
            "city": "São Paulo",
            "state": "SP",
            # Metadados adicionais
            "externalId": f"pix-{int(datetime.now().timestamp())}",
            "postbackUrl": "",
            "checkoutUrl": "",
            "referrerUrl": "",
            "utmQuery": "",
            "fingerPrints": []
        }
        
        try:
            print(f"[For4Payments] Criando pagamento PIX para {data.email}")
            print(f"[For4Payments] Valor: R$ {data.amount/100:.2f}")
            
            response = requests.post(
                f"{self.API_URL}/transaction.purchase",
                json=payment_data,
                headers=self._get_headers(),
                timeout=30
            )
            
            print(f"[For4Payments] Status HTTP: {response.status_code}")
            
            # Tratar erros HTTP
            if response.status_code != 200:
                error_message = self._extract_error_message(response)
                print(f"[For4Payments] Erro: {error_message}")
                raise requests.exceptions.RequestException(f"API Error: {error_message}")
            
            # Processar resposta de sucesso
            response_data = response.json()
            print(f"[For4Payments] Pagamento criado com sucesso")
            
            return self._parse_payment_response(response_data)
            
        except requests.exceptions.RequestException as e:
            print(f"[For4Payments] Erro na requisição: {str(e)}")
            raise
        except Exception as e:
            print(f"[For4Payments] Erro inesperado: {str(e)}")
            raise
    
    def _extract_error_message(self, response: requests.Response) -> str:
        """
        Extrair mensagem de erro da resposta da API
        """
        if response.status_code == 401:
            return "Falha na autenticação. Verifique sua chave de API."
        elif response.status_code == 400:
            return "Dados inválidos enviados para a API."
        elif response.status_code == 500:
            return "Erro interno do servidor For4Payments."
        
        # Tentar extrair mensagem do JSON
        try:
            error_data = response.json()
            return (
                error_data.get("message") or 
                error_data.get("error") or 
                error_data.get("errors", {}).get("message") or
                "Erro desconhecido"
            )
        except:
            return response.text or "Erro desconhecido"
    
    def _parse_payment_response(self, response_data: Dict[str, Any]) -> PaymentResponse:
        """
        Processar resposta da criação de pagamento
        """
        # Extrair códigos PIX da resposta real da For4Payments
        pix_code = response_data.get("pixCode", "")
        pix_qr_code = response_data.get("qrCode", "")
        
        print(f"[For4Payments] PIX Code extraído: {pix_code[:50]}...")
        print(f"[For4Payments] QR Code extraído: {'Presente' if pix_qr_code else 'Ausente'}")
        
        # Extrair data de expiração
        expires_at = (
            response_data.get("expiration") or
            response_data.get("expiresAt") or
            (datetime.now() + timedelta(minutes=30)).isoformat()
        )
        
        # Extrair status
        status = response_data.get("status", "pending").lower()
        
        # Extrair ID da transação
        payment_id = (
            response_data.get("id") or
            response_data.get("transactionId") or
            response_data.get("_id") or
            f"txn-{int(datetime.now().timestamp())}"
        )
        
        return PaymentResponse(
            id=str(payment_id),
            pix_code=pix_code,
            pix_qr_code=pix_qr_code,
            expires_at=expires_at,
            status=status
        )
    
    def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Verificar status de um pagamento
        """
        try:
            print(f"[For4Payments] Verificando status do pagamento {payment_id}")
            
            response = requests.get(
                f"{self.API_URL}/transaction.getPayment",
                params={"id": payment_id},
                headers=self._get_headers(),
                timeout=15
            )
            
            if response.status_code != 200:
                error_message = self._extract_error_message(response)
                print(f"[For4Payments] Erro na verificação: {error_message}")
                return {"status": "error", "message": error_message}
            
            response_data = response.json()
            status = response_data.get("status", "pending").lower()
            
            print(f"[For4Payments] Status atual: {status}")
            
            return {
                "status": status,
                "payment_data": response_data,
                "paid": status in ["paid", "approved", "completed"],
                "pending": status in ["pending", "waiting_payment"],
                "failed": status in ["failed", "cancelled", "expired"]
            }
            
        except Exception as e:
            print(f"[For4Payments] Erro na verificação de status: {str(e)}")
            return {"status": "error", "message": str(e)}

def gerar_codigo_pix_simulado(valor, protocolo):
    """Gerar código PIX simulado para demonstração"""
    import uuid
    # Gerar identificador único baseado no protocolo
    identificador = str(uuid.uuid4()).replace('-', '')[:32]
    # Valor formatado para PIX (sem ponto decimal)
    valor_centavos = str(int(valor * 100)).zfill(4)
    # Código PIX simulado no formato oficial
    codigo = f"00020126580014BR.GOV.BCB.PIX0136{identificador}52040000530398654{len(valor_centavos):02d}{valor_centavos}5802BR5925IBGE CONCURSO PUBLICO 20256008BRASILIA62070503{protocolo[-3:]}6304"
    # Calcular CRC (simplificado para demonstração)
    crc = hex(hash(codigo) % 65536)[2:].upper().zfill(4)
    return codigo + crc