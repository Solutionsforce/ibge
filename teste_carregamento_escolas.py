
#!/usr/bin/env python3
from escola_utils import carregar_escolas_cache, buscar_escolas_proximas

def teste_carregamento():
    print("=== TESTE DE CARREGAMENTO DE ESCOLAS ===")
    
    # Testar carregamento do cache
    escolas = carregar_escolas_cache()
    print(f"Total de escolas carregadas no cache: {len(escolas)}")
    
    if len(escolas) > 0:
        print("\nPrimeiras 5 escolas carregadas:")
        for i, escola in enumerate(escolas[:5]):
            print(f"  {i+1}. {escola['nome']} - {escola['municipio']}/{escola['uf']}")
            print(f"     Coordenadas: {escola['latitude']:.6f}, {escola['longitude']:.6f}")
    
    # Testar busca por proximidade (São Paulo)
    print("\n=== TESTE DE BUSCA POR PROXIMIDADE ===")
    escolas_proximas = buscar_escolas_proximas(-23.5505, -46.6333, max_escolas=5)
    print(f"Escolas encontradas próximas a São Paulo: {len(escolas_proximas)}")
    
    for i, escola in enumerate(escolas_proximas):
        print(f"  {i+1}. {escola['nome']} - {escola['distancia_km']:.2f}km")
        print(f"     {escola['municipio']}/{escola['uf']}")

if __name__ == "__main__":
    teste_carregamento()
