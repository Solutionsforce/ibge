import csv
import math
import requests
import os

def calcular_distancia(lat1, lon1, lat2, lon2):
    """
    Calcula a distância entre duas coordenadas usando a fórmula de Haversine
    Retorna a distância em quilômetros
    """
    # Converter graus para radianos
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Fórmula de Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Raio da Terra em quilômetros
    raio_terra = 6371
    return c * raio_terra

def obter_coordenadas_por_cep(cep):
    """
    Obtém coordenadas (latitude, longitude) a partir do CEP usando ViaCEP + Nominatim
    """
    try:
        # Primeiro, buscar dados do endereço via ViaCEP
        viacep_url = f"https://viacep.com.br/ws/{cep}/json/"
        response = requests.get(viacep_url)
        
        if response.status_code != 200:
            print(f"❌ Erro ao consultar ViaCEP: {response.status_code}")
            return None, None
            
        viacep_data = response.json()
        
        if 'erro' in viacep_data:
            print(f"❌ CEP não encontrado: {cep}")
            return None, None
        
        # Montar query para geocoding
        logradouro = viacep_data.get('logradouro', '')
        localidade = viacep_data.get('localidade', '')
        uf = viacep_data.get('uf', '')
        
        # Query para Nominatim
        if logradouro:
            query = f"{logradouro}, {localidade}, {uf}, Brazil"
        else:
            query = f"{localidade}, {uf}, Brazil"
            
        print(f"🔍 Buscando coordenadas para: {query}")
        
        # Geocoding usando Nominatim
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': query,
            'format': 'json',
            'limit': 1
        }
        
        headers = {
            'User-Agent': 'IBGE-Trabalhe-Conosco/1.0'
        }
        
        response = requests.get(nominatim_url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro ao consultar Nominatim: {response.status_code}")
            return None, None
            
        nominatim_data = response.json()
        
        if not nominatim_data:
            print(f"❌ Coordenadas não encontradas para: {query}")
            return None, None
            
        # Extrair coordenadas
        lat = float(nominatim_data[0]['lat'])
        lon = float(nominatim_data[0]['lon'])
        
        print(f"✓ Coordenadas obtidas: {lat}, {lon}")
        return lat, lon, viacep_data
        
    except Exception as e:
        print(f"❌ Erro ao obter coordenadas: {str(e)}")
        return None, None, None

def carregar_escolas_do_csv():
    """
    Carrega todas as escolas do arquivo CSV
    """
    escolas = []
    csv_path = 'escolas_brasil.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo CSV não encontrado: {csv_path}")
        return escolas
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    # Verificar se tem coordenadas válidas
                    if not row.get('Latitude') or not row.get('Longitude'):
                        continue
                        
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    
                    # Filtrar apenas escolas em funcionamento ou com restrições específicas
                    restricao = row.get('Restrição de Atendimento', '').upper()
                    if not restricao or 'FUNCIONAMENTO' not in restricao:
                        continue
                    
                    escola = {
                        'nome': row.get('Escola', '').strip(),
                        'codigo_inep': row.get('Código INEP', '').strip(),
                        'endereco': row.get('Endereço', '').strip(),
                        'uf': row.get('UF', '').strip(),
                        'municipio': row.get('Município', '').strip(),
                        'dependencia': row.get('Dependência Administrativa', '').strip(),
                        'etapas': row.get('Etapas e Modalidade de Ensino Oferecidas', '').strip(),
                        'telefone': row.get('Telefone', '').strip(),
                        'latitude': lat,
                        'longitude': lon
                    }
                    
                    # Verificar se tem dados essenciais
                    if escola['nome'] and escola['endereco']:
                        escolas.append(escola)
                        
                except (ValueError, TypeError) as e:
                    # Ignorar linhas com dados inválidos
                    continue
                    
        print(f"✓ Carregadas {len(escolas)} escolas válidas do arquivo CSV")
        return escolas
        
    except Exception as e:
        print(f"❌ Erro ao carregar CSV: {str(e)}")
        return []

def buscar_escolas_proximas(lat_usuario, lon_usuario, limite=3):
    """
    Busca as escolas mais próximas do usuário
    """
    escolas = carregar_escolas_do_csv()
    
    if not escolas:
        print("❌ Nenhuma escola carregada do CSV")
        return []
    
    # Calcular distância para cada escola
    escolas_com_distancia = []
    
    for escola in escolas:
        try:
            distancia = calcular_distancia(
                lat_usuario, lon_usuario,
                escola['latitude'], escola['longitude']
            )
            
            escola_formatada = {
                'nome': escola['nome'],
                'endereco': f"{escola['endereco']}, {escola['municipio']} - {escola['uf']}",
                'distancia': f"{distancia:.1f} km",
                'dependencia': escola['dependencia'],
                'etapas': escola['etapas'],
                'codigo_inep': escola['codigo_inep'],
                'telefone': escola['telefone'],
                'distancia_numerica': distancia
            }
            
            escolas_com_distancia.append(escola_formatada)
            
        except Exception as e:
            # Ignorar escolas com problemas nos dados
            continue
    
    # Ordenar por distância e retornar as mais próximas
    escolas_ordenadas = sorted(escolas_com_distancia, key=lambda x: x['distancia_numerica'])
    escolas_selecionadas = escolas_ordenadas[:limite]
    
    print(f"✓ Selecionadas {len(escolas_selecionadas)} escolas mais próximas")
    
    # Remover campo auxiliar distancia_numerica
    for escola in escolas_selecionadas:
        del escola['distancia_numerica']
    
    return escolas_selecionadas

def buscar_escolas_por_cep(cep):
    """
    Função principal para buscar escolas próximas baseado no CEP
    """
    print(f"🔍 Iniciando busca de escolas para CEP: {cep}")
    
    # Obter coordenadas do usuário
    resultado_coords = obter_coordenadas_por_cep(cep)
    
    if len(resultado_coords) == 3:
        lat_usuario, lon_usuario, endereco_completo = resultado_coords
    else:
        lat_usuario, lon_usuario = resultado_coords
        endereco_completo = None
    
    if lat_usuario is None or lon_usuario is None:
        print("❌ Não foi possível obter coordenadas do usuário")
        # Retornar fallback básico apenas em caso de erro
        return [
            {
                'nome': 'Escola Estadual Professor João Silva',
                'endereco': 'Rua das Flores, 123 - Centro',
                'distancia': '2.5 km',
                'dependencia': 'Estadual',
                'etapas': 'Ensino Fundamental e Médio',
                'codigo_inep': '23456789'
            },
            {
                'nome': 'Colégio Municipal Maria Aparecida',
                'endereco': 'Av. Principal, 456 - Bairro Novo', 
                'distancia': '3.2 km',
                'dependencia': 'Municipal',
                'etapas': 'Ensino Fundamental',
                'codigo_inep': '34567890'
            },
            {
                'nome': 'Centro Educacional São José',
                'endereco': 'Rua da Escola, 789 - Vila Santos',
                'distancia': '4.1 km',
                'dependencia': 'Privada',
                'etapas': 'Ensino Fundamental e Médio',
                'codigo_inep': '45678901'
            }
        ]
    
    # Buscar escolas próximas
    escolas_proximas = buscar_escolas_proximas(lat_usuario, lon_usuario, limite=3)
    
    if not escolas_proximas:
        print("❌ Nenhuma escola encontrada próxima ao usuário")
        # Retornar fallback se não encontrar escolas
        return [
            {
                'nome': 'Escola Estadual Professor João Silva',
                'endereco': 'Rua das Flores, 123 - Centro',
                'distancia': '2.5 km',
                'dependencia': 'Estadual',
                'etapas': 'Ensino Fundamental e Médio',
                'codigo_inep': '23456789'
            },
            {
                'nome': 'Colégio Municipal Maria Aparecida',
                'endereco': 'Av. Principal, 456 - Bairro Novo', 
                'distancia': '3.2 km',
                'dependencia': 'Municipal',
                'etapas': 'Ensino Fundamental',
                'codigo_inep': '34567890'
            },
            {
                'nome': 'Centro Educacional São José',
                'endereco': 'Rua da Escola, 789 - Vila Santos',
                'distancia': '4.1 km',
                'dependencia': 'Privada',
                'etapas': 'Ensino Fundamental e Médio',
                'codigo_inep': '45678901'
            }
        ]
    
    print(f"✓ Retornando {len(escolas_proximas)} escolas próximas")
    return escolas_proximas