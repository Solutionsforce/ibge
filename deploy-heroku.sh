#!/bin/bash

# Script de Deploy Automatizado para Heroku - IBGE Trabalhe Conosco
# Uso: ./deploy-heroku.sh [nome-da-app]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 IBGE Trabalhe Conosco - Deploy Heroku${NC}"
echo "=========================================="

# Verificar se Heroku CLI está instalado
if ! command -v heroku &> /dev/null; then
    echo -e "${RED}❌ Heroku CLI não encontrado. Instale em: https://devcenter.heroku.com/articles/heroku-cli${NC}"
    exit 1
fi

# Login no Heroku
echo -e "${YELLOW}🔐 Verificando login no Heroku...${NC}"
if ! heroku whoami &> /dev/null; then
    echo -e "${YELLOW}📝 Fazendo login no Heroku...${NC}"
    heroku login
fi

echo -e "${GREEN}✅ Usuário logado: $(heroku whoami)${NC}"

# Nome da aplicação
if [ -z "$1" ]; then
    read -p "Digite o nome da aplicação Heroku: " APP_NAME
else
    APP_NAME=$1
fi

echo -e "${BLUE}📱 Nome da aplicação: $APP_NAME${NC}"

# Verificar se a aplicação já existe
if heroku apps:info $APP_NAME &> /dev/null; then
    echo -e "${YELLOW}⚠️  Aplicação $APP_NAME já existe${NC}"
    read -p "Deseja continuar com deploy? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo -e "${RED}❌ Deploy cancelado${NC}"
        exit 1
    fi
else
    # Criar aplicação
    echo -e "${YELLOW}🆕 Criando aplicação $APP_NAME...${NC}"
    heroku create $APP_NAME
fi

# Configurar Git remote
echo -e "${YELLOW}🔗 Configurando Git remote...${NC}"
heroku git:remote -a $APP_NAME

# Adicionar PostgreSQL addon
echo -e "${YELLOW}🗄️  Adicionando PostgreSQL...${NC}"
heroku addons:create heroku-postgresql:essential-0 -a $APP_NAME || echo "PostgreSQL já existe"

# Configurar variáveis de ambiente
echo -e "${YELLOW}🔐 Configurando variáveis de ambiente...${NC}"

# Verificar se FOR4PAYMENTS_SECRET_KEY existe
if ! heroku config:get FOR4PAYMENTS_SECRET_KEY -a $APP_NAME &> /dev/null; then
    read -p "Digite sua chave FOR4PAYMENTS_SECRET_KEY: " FOR4PAYMENTS_KEY
    heroku config:set FOR4PAYMENTS_SECRET_KEY="$FOR4PAYMENTS_KEY" -a $APP_NAME
else
    echo -e "${GREEN}✅ FOR4PAYMENTS_SECRET_KEY já configurada${NC}"
fi

# Preparar requirements.txt para Heroku
echo -e "${YELLOW}📦 Preparando dependências...${NC}"
cp requirements-heroku.txt requirements.txt

# Verificar status do Git
echo -e "${YELLOW}📝 Verificando status do Git...${NC}"
git status

# Commit das mudanças
echo -e "${YELLOW}💾 Fazendo commit das mudanças...${NC}"
git add .
git commit -m "Deploy: Preparação para Heroku com arquivos de configuração" || echo "Nenhuma mudança para commit"

# Deploy
echo -e "${YELLOW}🚀 Iniciando deploy...${NC}"
git push heroku main

# Executar post-deploy (criar tabelas)
echo -e "${YELLOW}🗄️  Criando tabelas do banco de dados...${NC}"
heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()" -a $APP_NAME

# Informações finais
echo ""
echo -e "${GREEN}🎉 DEPLOY CONCLUÍDO COM SUCESSO! 🎉${NC}"
echo "=========================================="
echo -e "${BLUE}📱 Aplicação: $APP_NAME${NC}"
echo -e "${BLUE}🌐 URL: https://$APP_NAME.herokuapp.com${NC}"
echo -e "${BLUE}📊 Dashboard: https://dashboard.heroku.com/apps/$APP_NAME${NC}"
echo ""
echo -e "${YELLOW}Comandos úteis:${NC}"
echo "• Ver logs: heroku logs --tail -a $APP_NAME"
echo "• Abrir app: heroku open -a $APP_NAME"
echo "• Ver config: heroku config -a $APP_NAME"
echo ""
echo -e "${GREEN}✅ Sistema IBGE Trabalhe Conosco deployado com sucesso!${NC}"