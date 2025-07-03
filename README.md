# IBGE Trabalhe Conosco - Sistema de Inscrição em Concursos Públicos

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Solutionsforce/IbgeClone)

## Descrição

Sistema web brasileiro estilo governo para "IBGE Trabalhe Conosco" - um sistema completo de inscrição em concursos públicos com múltiplas etapas incluindo:

- ✅ Login gov.br simulado
- ✅ Seleção de cargo/endereço
- ✅ Seleção de local de prova com geolocalização
- ✅ Pagamento via PIX usando API FOR4PAYMENTS
- ✅ Sistema completo de dados do usuário
- ✅ Busca de escolas por CEP com dados reais

## Stack Tecnológico

- **Framework:** Flask 3.1.1 (Python)
- **Banco de Dados:** PostgreSQL (Heroku Postgres)
- **Frontend:** HTML5, Tailwind CSS, JavaScript vanilla
- **Integração PIX:** FOR4PAYMENTS API
- **APIs Externas:** ViaCEP, Nominatim (OpenStreetMap)
- **Deploy:** Heroku com Gunicorn

## Pré-requisitos para Deploy

### Variáveis de Ambiente Necessárias

1. **FOR4PAYMENTS_SECRET_KEY** (obrigatório)
   - Chave da API For4Payments para processamento PIX
   - Obtida em: https://app.for4payments.com.br

2. **SESSION_SECRET** (gerado automaticamente)
   - Chave secreta para sessões Flask
   - Gerada automaticamente pelo Heroku

3. **DATABASE_URL** (fornecido automaticamente)
   - URL do PostgreSQL
   - Fornecida automaticamente pelo Heroku Postgres

## Deploy no Heroku

### Opção 1: Deploy Automático (Recomendado)

1. Clique no botão "Deploy to Heroku" acima
2. Configure o nome da aplicação
3. Adicione a variável `FOR4PAYMENTS_SECRET_KEY`
4. Clique em "Deploy app"

### Opção 2: Deploy Manual via Heroku CLI

```bash
# 1. Clone o repositório
git clone https://github.com/Solutionsforce/IbgeClone.git
cd IbgeClone

# 2. Login no Heroku
heroku login

# 3. Criar aplicação
heroku create seu-app-ibge

# 4. Adicionar PostgreSQL
heroku addons:create heroku-postgresql:essential-0

# 5. Configurar variáveis de ambiente
heroku config:set FOR4PAYMENTS_SECRET_KEY=sua_chave_aqui

# 6. Deploy
git push heroku main

# 7. Executar migrações (se necessário)
heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Estrutura do Projeto

```
IbgeClone/
├── app.py                 # Configuração principal da aplicação Flask
├── main.py               # Ponto de entrada da aplicação
├── routes.py             # Rotas e endpoints da aplicação
├── models.py             # Modelos do banco de dados (SQLAlchemy)
├── for4_payments.py      # Integração com API PIX For4Payments
├── escola_utils.py       # Utilitários para busca de escolas
├── templates/            # Templates HTML (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── checkout.html
│   └── ...
├── static/              # Arquivos estáticos (CSS, JS, imagens)
├── escolas_brasil.csv   # Base de dados das escolas
├── Procfile            # Configuração Heroku
├── requirements-heroku.txt # Dependências Python
├── runtime.txt         # Versão Python
└── app.json           # Configuração Heroku automática
```

## Funcionalidades Principais

### 1. Sistema de Inscrição Completo
- Login gov.br simulado com validação CPF
- Formulário de dados pessoais editável
- Sistema de seções I, III e IV
- Transmissão de dados via localStorage

### 2. Seleção de Local de Prova
- Busca por CEP usando ViaCEP
- Geolocalização com Nominatim
- Base de dados de 62+ escolas reais
- Cálculo de distância por coordenadas

### 3. Sistema PIX Integrado
- API For4Payments real funcionando
- Geração de QR Code automática
- Produto: "CURSO TECNICO FOTOGRAFO AVANCE"
- Valor: R$ 89,00
- Verificação de status em tempo real

### 4. Data e Hora Dinâmica
- Timezone de Brasília (America/Sao_Paulo)
- Atualização automática a cada minuto
- Formato brasileiro: DD/MM/AAAA às HH:MM

## Arquivos de Configuração Heroku

### Procfile
```
web: gunicorn --bind 0.0.0.0:$PORT --reuse-port main:app
```

### runtime.txt
```
python-3.11.10
```

### app.json
Configuração completa para deploy automático com:
- Heroku Postgres Essential
- Variáveis de ambiente configuradas
- Scripts de pós-deploy

## Monitoramento e Logs

```bash
# Ver logs em tempo real
heroku logs --tail

# Ver logs específicos
heroku logs --source app

# Executar comandos no Heroku
heroku run python -c "from app import app; print('App funcionando!')"
```

## Troubleshooting

### Erro de Variável de Ambiente
```bash
heroku config:set FOR4PAYMENTS_SECRET_KEY=sua_chave_aqui
```

### Erro de Banco de Dados
```bash
heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Erro de Build
Verifique se todas as dependências estão em `requirements-heroku.txt`

## Suporte

Para suporte técnico:
1. Verificar logs: `heroku logs --tail`
2. Verificar variáveis: `heroku config`
3. Verificar status: `heroku ps`

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto é uma implementação educacional do sistema IBGE Trabalhe Conosco.

---

**🚀 Deploy rápido:** Use o botão "Deploy to Heroku" para deploy em 1 clique!