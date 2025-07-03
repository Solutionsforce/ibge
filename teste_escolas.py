
import requests
from escola_utils import buscar_escolas_proximas, carregar_escolas_cache

def teste_cep_completo(cep="74950300"):
    """Teste completo do fluxo: CEP -> Coordenadas -> Escolas próximas"""
    print(f"🧪 Testando CEP: {cep}")
    
    # 1. Buscar endereço pelo CEP
    try:
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=5)
        cep_data = response.json()
        print(f"✅ Endereço: {cep_data}")
        
        # 2. Geocodificar usando Nominatim
        endereco_busca = f"{cep_data.get('localidade', '')}, {cep_data.get('uf', '')}, Brasil"
        nominatim_response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                'q': endereco_busca,
                'format': 'json',
                'limit': 1
            },
            headers={'User-Agent': 'ibge-teste-2025'},
            timeout=10
        )
        nominatim_data = nominatim_response.json()
        
        if nominatim_data:
            user_lat = float(nominatim_data[0]['lat'])
            user_lon = float(nominatim_data[0]['lon'])
            print(f"✅ Coordenadas: {user_lat}, {user_lon}")
            
            # 3. Buscar escolas próximas
            escolas = buscar_escolas_proximas(user_lat, user_lon, limite_distancia=50, max_escolas=3)
            
            print(f"✅ Escolas encontradas: {len(escolas)}")
            for i, escola in enumerate(escolas, 1):
                print(f"  {i}. {escola['nome']}: {escola['distancia_km']:.2f}km")
            
            return escolas
        else:
            print("❌ Erro ao geocodificar endereço")
            return []
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return []

def verificar_estrutura_csv():
    """Verifica se o CSV tem a estrutura correta"""
    print("\n📋 Verificando estrutura do CSV...")
    escolas = carregar_escolas_cache()
    
    if escolas:
        primeira_escola = escolas[0]
        print(f"✅ Total de escolas carregadas: {len(escolas)}")
        print(f"✅ Campos disponíveis: {list(primeira_escola.keys())}")
        print(f"✅ Exemplo de escola: {primeira_escola['nome']} - {primeira_escola['municipio']}/{primeira_escola['uf']}")
        return True
    else:
        print("❌ Nenhuma escola foi carregada do CSV")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes do sistema de escolas...")
    
    # Verificar CSV primeiro
    if verificar_estrutura_csv():
        # Testar com diferentes CEPs
        ceps_teste = ["74950300", "01310100", "20040020"]  # Aparecida de Goiânia, São Paulo, Rio de Janeiro
        
        for cep in ceps_teste:
            print(f"\n{'='*50}")
            teste_cep_completo(cep)
            print(f"{'='*50}")
    
    print("\n✅ Testes concluídos!")
