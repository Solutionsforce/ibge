#!/usr/bin/env python3
"""
Teste da implementação simplificada PayBets PIX
"""

from paybets_client import PayBetsPixClient
import uuid
from datetime import datetime

def test_simplified_pix():
    """Teste da geração de PIX com classe simplificada"""
    
    # Criar cliente
    client = PayBetsPixClient("https://elite-manager-api-62571bbe8e96.herokuapp.com/api")
    
    # Dados de teste
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    external_id = f"TEST-{timestamp}-{unique_id}"
    
    print(f"[TESTE] Testando geração de PIX...")
    print(f"[TESTE] External ID: {external_id}")
    
    # Gerar PIX
    response = client.generate_pix(
        amount=89.0,
        external_id=external_id,
        callback_url="https://webhook.site/test",
        name="João Silva Santos",
        email="joao.silva@email.com",
        document="12345678901"
    )
    
    print(f"[TESTE] Resposta da API:")
    print(f"Status: {response.get('success', 'N/A')}")
    print(f"Message: {response.get('message', 'N/A')}")
    
    if response.get('success'):
        data = response.get('data', {})
        qr_data = data.get('qrCodeResponse', {})
        
        print(f"Transaction ID: {qr_data.get('transactionId')}")
        print(f"QR Code: {qr_data.get('qrcode')[:50]}...")
        print(f"Status: {qr_data.get('status')}")
        print("✓ PIX gerado com sucesso!")
    else:
        print("❌ Falha na geração do PIX")
        print(f"Erro: {response.get('error', 'N/A')}")

if __name__ == "__main__":
    test_simplified_pix()