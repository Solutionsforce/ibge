#!/usr/bin/env python3
"""
Teste integrado das classes CPFConsultationClient e PayBetsPixClient
"""

from cpf_client import CPFConsultationClient
from paybets_client import PayBetsPixClient
import uuid
from datetime import datetime

def test_full_integration():
    """Teste completo da integração CPF + PIX"""
    
    print("=== TESTE INTEGRADO CPF + PIX ===")
    
    # 1. Testar consulta de CPF
    print("\n1. Testando consulta de CPF...")
    cpf_client = CPFConsultationClient("https://elite-manager-api-62571bbe8e96.herokuapp.com/api")
    
    cpf_test = "12345678901"
    cpf_result = cpf_client.consult(cpf_test)
    
    print(f"CPF Consultation Success: {cpf_result.get('success')}")
    print(f"CPF Message: {cpf_result.get('message')}")
    
    # 2. Testar geração de PIX
    print("\n2. Testando geração de PIX...")
    pix_client = PayBetsPixClient("https://elite-manager-api-62571bbe8e96.herokuapp.com/api")
    
    # Gerar dados únicos para PIX
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    external_id = f"IBGE-INTEGRATION-{timestamp}-{unique_id}"
    
    pix_result = pix_client.generate_pix(
        amount=89.0,
        external_id=external_id,
        callback_url="https://webhook.site/integration-test",
        name="João Silva Santos",
        email="joao.silva@email.com",
        document=cpf_test
    )
    
    print(f"PIX Generation Success: {pix_result.get('success')}")
    print(f"PIX Message: {pix_result.get('message')}")
    
    if pix_result.get('success'):
        data = pix_result.get('data', {})
        qr_data = data.get('qrCodeResponse', {})
        print(f"Transaction ID: {qr_data.get('transactionId')}")
        print(f"QR Code Preview: {qr_data.get('qrcode')[:50]}...")
        print(f"Status: {qr_data.get('status')}")
    
    # 3. Resultado final
    print("\n=== RESULTADO FINAL ===")
    cpf_ok = cpf_result.get('success', False)
    pix_ok = pix_result.get('success', False)
    
    if cpf_ok and pix_ok:
        print("✓ INTEGRAÇÃO COMPLETA - Ambos os clientes funcionando!")
        print("✓ CPF: OK")
        print("✓ PIX: OK")
        return True
    else:
        print("❌ INTEGRAÇÃO INCOMPLETA:")
        print(f"CPF: {'OK' if cpf_ok else 'FALHA'}")
        print(f"PIX: {'OK' if pix_ok else 'FALHA'}")
        return False

if __name__ == "__main__":
    success = test_full_integration()
    exit(0 if success else 1)