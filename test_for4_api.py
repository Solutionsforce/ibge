#!/usr/bin/env python3
"""
Script para diagnosticar problemas com a API For4Payments
"""
import os
import requests
import json
from datetime import datetime

def test_for4_payments_api():
    secret_key = os.environ.get('FOR4PAYMENTS_SECRET_KEY')
    
    if not secret_key:
        print("❌ FOR4PAYMENTS_SECRET_KEY não encontrada")
        return False
        
    print("🔍 DIAGNÓSTICO FOR4PAYMENTS API")
    print("=" * 50)
    
    # Informações da chave
    print(f"🔑 Chave: {secret_key[:10]}...{secret_key[-6:]}")
    print(f"📏 Tamanho: {len(secret_key)} caracteres")
    print(f"🏷️  Formato: {'UUID' if '-' in secret_key else 'Token'}")
    print()
    
    # Teste básico de conectividade
    print("🌐 Testando conectividade...")
    try:
        response = requests.get('https://app.for4payments.com.br', timeout=5)
        print(f"✓ Site principal: {response.status_code}")
    except Exception as e:
        print(f"❌ Site principal: {e}")
        return False
    
    # Teste de autenticação com dados mínimos
    print("\n🔐 Testando autenticação...")
    
    headers = {
        'Authorization': f'Bearer {secret_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Payload mínimo para teste
    minimal_payload = {
        "paymentMethod": "PIX",
        "amount": 100
    }
    
    try:
        response = requests.post(
            'https://app.for4payments.com.br/api/v1/transaction.purchase',
            json=minimal_payload,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.text}")
        
        if response.status_code == 401:
            print("\n❌ ERRO DE AUTENTICAÇÃO CONFIRMADO")
            print("Possíveis soluções:")
            print("1. Verificar se a chave está ativa no painel For4Payments")
            print("2. Verificar se a conta tem permissões para PIX")
            print("3. Gerar nova chave no painel de administração")
            print("4. Verificar se não é conta de sandbox vs produção")
            return False
            
        elif response.status_code == 400:
            print("\n⚠️ DADOS INVÁLIDOS (mas autenticação OK)")
            print("A chave está funcionando, mas os dados estão incompletos")
            return True
            
        elif response.status_code == 200:
            print("\n✅ API FUNCIONANDO PERFEITAMENTE!")
            return True
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    
    return False

def test_complete_payload():
    """Teste com payload completo e válido"""
    secret_key = os.environ.get('FOR4PAYMENTS_SECRET_KEY')
    
    complete_payload = {
        "name": "Teste Usuario",
        "email": "teste@exemplo.com",
        "cpf": "12345678901",
        "phone": "11999999999",
        "paymentMethod": "PIX",
        "amount": 8790,  # R$ 87,90
        "traceable": True,
        "items": [
            {
                "title": "IBGE Concurso Público 2025",
                "quantity": 1,
                "unitPrice": 8790,
                "tangible": False
            }
        ],
        "cep": "01310100",
        "street": "Avenida Paulista",
        "number": "1000",
        "complement": "",
        "district": "Bela Vista",
        "city": "São Paulo",
        "state": "SP",
        "externalId": f"ibge-test-{int(datetime.now().timestamp())}",
        "postbackUrl": "",
        "checkoutUrl": "",
        "referrerUrl": "",
        "utmQuery": "",
        "fingerPrints": []
    }
    
    headers = {
        'Authorization': f'Bearer {secret_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'IBGE-System/1.0'
    }
    
    print("\n🧪 TESTE COM PAYLOAD COMPLETO")
    print("=" * 50)
    
    try:
        response = requests.post(
            'https://app.for4payments.com.br/api/v1/transaction.purchase',
            json=complete_payload,
            headers=headers,
            timeout=15
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PIX GERADO COM SUCESSO!")
            data = response.json()
            print(f"💰 Payment ID: {data.get('id', 'N/A')}")
            print(f"🔗 PIX Code: {data.get('pix_code', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO DIAGNÓSTICO FOR4PAYMENTS")
    print("=" * 60)
    
    # Teste básico
    basic_ok = test_for4_payments_api()
    
    if basic_ok:
        # Se autenticação OK, testar payload completo
        complete_ok = test_complete_payload()
        
        if complete_ok:
            print("\n🎉 CONCLUSÃO: API FOR4PAYMENTS FUNCIONANDO!")
        else:
            print("\n⚠️ CONCLUSÃO: Autenticação OK, mas problema nos dados")
    else:
        print("\n💡 RECOMENDAÇÃO:")
        print("Solicite uma nova chave FOR4PAYMENTS_SECRET_KEY")
        print("ou verifique as permissões da conta atual")
    
    print("\n" + "=" * 60)