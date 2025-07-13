#!/usr/bin/env python3
"""
Script para testar a nova implementação PayBets
"""
import sys
import json
from paybets_api import PayBetsAPI, PaymentRequestData

def test_paybets_pix_generation():
    """Teste da geração de PIX via PayBets"""
    
    print("=== TESTE PayBets PIX Generation ===")
    
    # Dados de teste
    test_data = PaymentRequestData(
        name="João da Silva",
        email="joao.silva@email.com",
        cpf="12345678900",
        amount=87.90,  # R$ 87,90 (taxa de inscrição IBGE)
        phone="11999999999",
        description="Inscrição Concurso Público IBGE"
    )
    
    try:
        # Criar instância da API
        api = PayBetsAPI()
        
        print(f"API URL: {api.API_URL}")
        print(f"Dados do pagamento:")
        print(f"  - Nome: {test_data.name}")
        print(f"  - Email: {test_data.email}")
        print(f"  - CPF: {test_data.cpf}")
        print(f"  - Valor: R$ {test_data.amount:.2f}")
        print(f"  - Telefone: {test_data.phone}")
        print(f"  - Descrição: {test_data.description}")
        
        # Tentar gerar PIX
        print("\n--- Tentando gerar PIX via PayBets ---")
        response = api.create_pix_payment(test_data)
        
        print("\n✅ PIX gerado com sucesso!")
        print(f"Transaction ID: {response.transaction_id}")
        print(f"Status: {response.status}")
        print(f"Valor: R$ {response.amount:.2f}")
        print(f"PIX Code: {response.pix_code[:50]}...")
        print(f"QR Code: {'✓ Gerado' if response.pix_qr_code else '✗ Não gerado'}")
        
        # Testar verificação de status
        print("\n--- Testando verificação de status ---")
        status_result = api.check_payment_status(response.transaction_id)
        print(f"Status verificado: {status_result.get('status', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no teste: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_paybets_with_minimal_data():
    """Teste com dados mínimos"""
    
    print("\n=== TESTE PayBets com Dados Mínimos ===")
    
    # Dados mínimos
    test_data = PaymentRequestData(
        name="Maria Santos",
        email="maria@test.com",
        cpf="98765432100",
        amount=1.00  # R$ 1,00 para teste
    )
    
    try:
        api = PayBetsAPI()
        
        print(f"Testando com valor mínimo: R$ {test_data.amount:.2f}")
        
        response = api.create_pix_payment(test_data)
        
        print(f"✅ PIX mínimo gerado: {response.transaction_id}")
        print(f"Status: {response.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste mínimo: {str(e)}")
        return False

if __name__ == "__main__":
    print("Iniciando testes da API PayBets...")
    
    # Teste 1: Geração de PIX completa
    test1_success = test_paybets_pix_generation()
    
    # Teste 2: Dados mínimos
    test2_success = test_paybets_with_minimal_data()
    
    print("\n=== RESUMO DOS TESTES ===")
    print(f"Teste 1 (PIX completo): {'✅ PASSOU' if test1_success else '❌ FALHOU'}")
    print(f"Teste 2 (Dados mínimos): {'✅ PASSOU' if test2_success else '❌ FALHOU'}")
    
    if test1_success and test2_success:
        print("\n🎉 Todos os testes passaram! API PayBets está funcionando.")
        sys.exit(0)
    else:
        print("\n⚠️  Alguns testes falharam. Verifique a implementação.")
        sys.exit(1)