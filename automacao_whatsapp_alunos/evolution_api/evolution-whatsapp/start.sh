#!/bin/bash

# Nome dos contêineres, rede e portas
NETWORK_NAME="evolution-network"
DB_CONTAINER="evolution-db"
API_CONTAINER="evolution-api"
PORT_HOST=8085
API_KEY="multi_karambola_token_2026"

echo "Criando rede do Docker se não existir..."
docker network create $NETWORK_NAME 2>/dev/null || true

echo "Parando e removendo contêineres antigos se existirem..."
docker stop $API_CONTAINER $DB_CONTAINER evolution-redis 2>/dev/null
docker rm $API_CONTAINER $DB_CONTAINER evolution-redis 2>/dev/null

echo "Iniciando contêiner do banco de dados (PostgreSQL 16)..."
docker run -d \
  --name $DB_CONTAINER \
  --network $NETWORK_NAME \
  -e POSTGRES_DB=evolution \
  -e POSTGRES_USER=evolution \
  -e POSTGRES_PASSWORD=evolution_pass \
  -v evolution_db_data:/var/lib/postgresql/data \
  --restart unless-stopped \
  postgres:16-alpine

echo "Aguardando 5 segundos para o banco de dados inicializar..."
sleep 5

echo "Iniciando a Evolution API v2 (com Postgres ativo e Redis desativado)..."
docker run -d \
  --name $API_CONTAINER \
  --network $NETWORK_NAME \
  -p $PORT_HOST:8080 \
  -e SERVER_PORT=8080 \
  -e API_KEY=$API_KEY \
  -e AUTHENTICATION_TYPE=apikey \
  -e AUTHENTICATION_API_KEY=$API_KEY \
  -e DATABASE_ENABLED=true \
  -e DATABASE_PROVIDER=postgresql \
  -e DATABASE_CONNECTION_URI="postgresql://evolution:evolution_pass@$DB_CONTAINER:5432/evolution?schema=public" \
  -e REDIS_ENABLED=false \
  -e CACHE_REDIS_ENABLED=false \
  -v evolution_instances:/evolution/instances \
  --restart unless-stopped \
  evoapicloud/evolution-api:latest

echo "--------------------------------------------------------"
echo " Contêineres iniciados com sucesso!"
echo " Evolution API online em: http://localhost:$PORT_HOST"
echo " Token de segurança API_KEY: $API_KEY"
echo "--------------------------------------------------------"
echo "Para verificar os logs da API, rode: docker logs -f $API_CONTAINER"
