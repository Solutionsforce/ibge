#!/usr/bin/env python3
"""
Teste da CPFConsultationClient
"""

from cpf_client import CPFConsultationClient

def test_cpf_consultation():
    """Teste da consulta de CPF"""
    
    # Criar cliente
    client = CPFConsultationClient("https://elite-manager-api-62571bbe8e96.herokuapp.com/api")
    
    # CPF de teste
    cpf_test = "12345678901"
    
    print(f"[TESTE] Testando consulta de CPF: {cpf_test}")
    
    # Consultar CPF
    response = client.consult(cpf_test)
    
    print(f"[TESTE] Resposta da API:")
    print(f"Success: {response.get('success', 'N/A')}")
    print(f"Message: {response.get('message', 'N/A')}")
    
    if response.get('success'):
        data = response.get('data', {})
        if data:
            print(f"Nome: {data.get('nome', 'N/A')}")
            print(f"Nome da Mãe: {data.get('nome_mae', 'N/A')}")
            print(f"Data Nascimento: {data.get('data_nascimento', 'N/A')}")
        else:
            print("Data retornada é None - API funcionando mas sem dados específicos")
        print("✓ Consulta de CPF realizada com sucesso!")
    else:
        print("❌ Falha na consulta de CPF")
        print(f"Erro: {response.get('error', 'N/A')}")

if __name__ == "__main__":
    test_cpf_consultation()