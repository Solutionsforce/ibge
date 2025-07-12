"""
PayBets PIX API Integration
===========================
Integração completa para pagamentos PIX usando a API PayBets.
Base URL: https://elite-manager-api-62571bbe8e96.herokuapp.com/api
"""
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass
import uuid

@dataclass
class PaymentRequestData:
    """
    Dados necessários para criar um pagamento PIX via PayBets
    """
    name: str
    email: str
    cpf: str
    amount: float  # Valor em reais (não centavos)
    phone: Optional[str] = None
    description: Optional[str] = None

@dataclass
class PaymentResponse:
    """
    Resposta da criação de pagamento PIX via PayBets
    """
    transaction_id: str
    pix_code: str
    pix_qr_code: str
    status: str
    amount: float

class PayBetsAPI:
    """
    Classe principal para integração com a API PayBets
    """
    
    def __init__(self):
        """
        Inicializar a API PayBets
        """
        self.API_URL = "https://elite-manager-api-62571bbe8e96.herokuapp.com/api"
        
    def _get_headers(self) -> Dict[str, str]:
        """
        Headers padrão para as requisições HTTP
        """
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "PayBets-Python-SDK/1.0.0"
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
        if not isinstance(data.amount, (int, float)) or data.amount <= 0:
            raise ValueError("Valor deve ser um número positivo")
    
    def create_pix_payment(self, data: PaymentRequestData) -> PaymentResponse:
        """
        Criar um pagamento PIX via PayBets
        """
        
        # Validar dados de entrada
        self._validate_payment_data(data)
        
        # Processar e formatar dados
        cpf = ''.join(filter(str.isdigit, data.cpf))
        
        # Gerar external_id único
        external_id = f"IBGE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        
        # Construir payload para a API PayBets
        payment_data = {
            "amount": data.amount,
            "external_id": external_id,
            "clientCallbackUrl": "https://example.com/webhook",  # URL de callback opcional
            "name": data.name.strip(),
            "email": data.email.strip(),
            "document": cpf
        }
        
        try:
            print(f"[PayBets] Criando pagamento PIX para {data.email}")
            print(f"[PayBets] Valor: R$ {data.amount:.2f}")
            print(f"[PayBets] External ID: {external_id}")
            
            response = requests.post(
                f"{self.API_URL}/payments/paybets/pix/generate",
                json=payment_data,
                headers=self._get_headers(),
                timeout=30
            )
            
            print(f"[PayBets] Status HTTP: {response.status_code}")
            
            # Tratar erros HTTP
            if response.status_code != 201:
                error_message = self._extract_error_message(response)
                print(f"[PayBets] Erro: {error_message}")
                raise requests.exceptions.RequestException(f"API Error: {error_message}")
            
            # Processar resposta de sucesso
            response_data = response.json()
            print(f"[PayBets] Pagamento criado com sucesso")
            print(f"[PayBets] Response: {json.dumps(response_data, indent=2)}")
            
            return self._parse_payment_response(response_data)
            
        except requests.exceptions.RequestException as e:
            print(f"[PayBets] Erro na requisição: {str(e)}")
            raise
        except Exception as e:
            print(f"[PayBets] Erro inesperado: {str(e)}")
            raise
    
    def _extract_error_message(self, response: requests.Response) -> str:
        """
        Extrair mensagem de erro da resposta da API
        """
        if response.status_code == 400:
            return "Dados inválidos enviados para a API."
        elif response.status_code == 401:
            return "Acesso não autorizado."
        elif response.status_code == 429:
            return "Limite de requisições excedido. Tente novamente em breve."
        elif response.status_code == 500:
            return "Erro interno do servidor PayBets."
        
        # Tentar extrair mensagem do JSON
        try:
            error_data = response.json()
            if not error_data.get("success", True):
                return (
                    error_data.get("message") or 
                    error_data.get("error") or 
                    "Erro desconhecido"
                )
        except:
            pass
            
        return response.text or "Erro desconhecido"
    
    def _parse_payment_response(self, response_data: Dict[str, Any]) -> PaymentResponse:
        """
        Processar resposta da criação de pagamento PayBets
        """
        
        # Verificar se a resposta é bem-sucedida
        if not response_data.get("success", False):
            raise ValueError(f"Erro na API: {response_data.get('message', 'Erro desconhecido')}")
        
        # Extrair dados do QR Code da resposta
        qr_code_response = response_data.get("data", {}).get("qrCodeResponse", {})
        
        transaction_id = qr_code_response.get("transactionId", "")
        pix_code = qr_code_response.get("qrcode", "")
        status = qr_code_response.get("status", "PENDING")
        amount = qr_code_response.get("amount", 0)
        
        print(f"[PayBets] Transaction ID: {transaction_id}")
        print(f"[PayBets] PIX Code: {pix_code[:50]}...")
        print(f"[PayBets] Status: {status}")
        print(f"[PayBets] Amount: R$ {amount:.2f}")
        
        # Gerar QR Code como base64 (PayBets não retorna imagem, apenas código)
        pix_qr_code = self._generate_qr_code_base64(pix_code)
        
        return PaymentResponse(
            transaction_id=transaction_id,
            pix_code=pix_code,
            pix_qr_code=pix_qr_code,
            status=status,
            amount=amount
        )
    
    def _generate_qr_code_base64(self, pix_code: str) -> str:
        """
        Gerar QR Code em base64 a partir do código PIX
        """
        try:
            import qrcode
            import io
            import base64
            
            # Criar QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(pix_code)
            qr.make(fit=True)
            
            # Gerar imagem
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converter para base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{qr_base64}"
            
        except ImportError:
            print("[PayBets] qrcode não disponível, retornando placeholder")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    def check_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Verificar status de um pagamento PayBets
        Nota: A API PayBets usa endpoint diferente para verificação
        """
        try:
            print(f"[PayBets] Verificando status do pagamento {transaction_id}")
            
            # Usar endpoint específico para verificação de status
            response = requests.get(
                f"{self.API_URL}/payments/pix/status/{transaction_id}",
                headers=self._get_headers(),
                timeout=15
            )
            
            if response.status_code != 200:
                error_message = self._extract_error_message(response)
                print(f"[PayBets] Erro na verificação: {error_message}")
                return {"status": "error", "message": error_message}
            
            response_data = response.json()
            
            if not response_data.get("success", False):
                return {"status": "error", "message": response_data.get("message", "Erro desconhecido")}
            
            payment_data = response_data.get("data", {})
            status = payment_data.get("status", "PENDING")
            
            print(f"[PayBets] Status atual: {status}")
            
            return {
                "status": status,
                "payment_data": payment_data,
                "paid": status.upper() in ["PAID", "APPROVED", "COMPLETED"],
                "pending": status.upper() in ["PENDING", "WAITING_PAYMENT"],
                "failed": status.upper() in ["FAILED", "CANCELLED", "EXPIRED"]
            }
            
        except Exception as e:
            print(f"[PayBets] Erro na verificação de status: {str(e)}")
            return {"status": "error", "message": str(e)}

def gerar_codigo_pix_simulado(valor, protocolo):
    """Gerar código PIX simulado para demonstração (mantido para compatibilidade)"""
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