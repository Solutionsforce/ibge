#!/usr/bin/env python3
"""
Teste da integração Cashtime API para o projeto IBGE
"""
import sys
import json
from cashtime_api import create_cashtime_api

def test_cashtime_integration():
    """Teste completo da integração Cashtime"""
    
    print("=== TESTE CASHTIME PIX INTEGRATION ===")
    
    # Dados de teste para inscrição IBGE
    test_data = {
        "name": "JAIR MESSIAS BOLSONARO",
        "email": "jair@hotmail.com",
        "cpf": "453.178.287-91",
        "amount": 87.90,  # R$ 87,90 (taxa de inscrição IBGE)
        "phone": "11981410022",
        "description": "Inscrição Concurso Público IBGE 2025 - Processo Seletivo Simplificado"
    }
    
    try:
        # Criar instância da API com a chave fornecida
        secret_key = "sk_live_sLJNf4hOupi7EBe8hVKeRW+AENhDiFhdn0m98dZOHgaNXMBHUwgAnDwEyMSFsaX05oLaDklKbjHe+WMR5wzrcX4AXeux7i8joSG6GB1Nk36BSKyrpuvDdHsXq9JzmAm8XtbaaiUPPmhpnfZNiNk/OGq2tl2CtztLJRVUIWLKhno="
        
        api = create_cashtime_api(secret_key=secret_key)
        
        print(f"API URL: {api.API_URL}")
        print(f"Dados do pagamento:")
        print(f"  - Nome: {test_data['name']}")
        print(f"  - Email: {test_data['email']}")
        print(f"  - CPF: {test_data['cpf']}")
        print(f"  - Valor: R$ {test_data['amount']:.2f}")
        print(f"  - Telefone: {test_data['phone']}")
        print(f"  - Descrição: {test_data['description']}")
        
        # Tentar gerar PIX
        print("\n--- Tentando gerar PIX via Cashtime ---")
        result = api.create_pix_payment(test_data)
        
        print("\n✅ PIX gerado com sucesso!")
        print(f"Transaction ID: {result.get('txid')}")
        print(f"Cashtime ID: {result.get('cashtime_id')}")
        print(f"Status: {result.get('status')}")
        print(f"Valor: R$ {result.get('amount'):.2f}")
        print(f"PIX Code: {result.get('pix_code')[:80]}...")
        print(f"QR Code: {'✓ Gerado' if result.get('qr_code_image') else '✗ Não gerado'}")
        print(f"Expira em: {result.get('expires_at')}")
        
        # Testar verificação de status
        print("\n--- Testando verificação de status ---")
        if result.get('txid'):
            status_result = api.check_payment_status(result.get('txid'))
            print(f"Status verificado: {status_result.get('status', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no teste: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_cashtime_integration()
    sys.exit(0 if success else 1)