# Controle de mão de obra — ambiente local

O ambiente local de desenvolvimento usa Docker Compose com MariaDB 11.4 e uma API FastAPI. A API oferece verificação de saúde, documentação OpenAPI e o esquema de dados de negócio; endpoints de negócio e autenticação dependem das próximas fases aprovadas. Não use dados reais.

## Requisitos

- Docker Desktop com Docker Compose v2.
- Porta `8000` e, se desejado acesso local direto ao banco, porta `3306` disponíveis.

## Configurar e iniciar

Na raiz do projeto, copie o exemplo e substitua os valores ilustrativos por segredos locais:

```powershell
Copy-Item .env.example .env
```

O Compose exige `DB_PASSWORD`, `DB_ROOT_PASSWORD`, `DATA_ENCRYPTION_KEY` e `CPF_HASH_KEY`. O `.env.example` contém chaves públicas de demonstração para que o ambiente local vazio possa iniciar; elas **não protegem dados reais**. Gere chaves privadas locais antes de rodar o seed ou armazenar qualquer dado:

```powershell
python -c "import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie os resultados para `DATA_ENCRYPTION_KEY` e `CPF_HASH_KEY`, respectivamente. A chave Fernet deve ser válida e a chave HMAC do CPF deve ter pelo menos 32 bytes. O arquivo `.env` é ignorado pelo Git; nunca reutilize chaves de teste ou envie segredos ao chat. Perder ou trocar essas chaves impede descriptografar os dados cifrados e conferir os hashes de CPF existentes.

Suba os serviços:

```powershell
docker compose up --build
```

Quando o MariaDB estiver saudável, a API aplica as migrações Alembic e inicia com hot reload. A API e o banco são publicados apenas em `127.0.0.1`. Verifique:

- Saúde da API e do banco: <http://localhost:8000/health>
- Swagger/OpenAPI: <http://localhost:8000/docs>

`/health` responde `200` quando a API consegue executar uma consulta simples ao banco e `503` quando o banco está indisponível. A documentação interativa pode ser desligada com `DOCS_ENABLED=false`.

## Testes e lint

```powershell
docker compose exec api pytest
docker compose exec api ruff check .
```

## Migrações

```powershell
docker compose exec api alembic revision --autogenerate -m "descricao"
docker compose exec api alembic upgrade head
docker compose exec api alembic downgrade base
```

O Compose executa `alembic upgrade head` ao iniciar a API. `downgrade base` remove todas as tabelas criadas pelas migrações; use apenas quando puder descartar os dados locais.

## Seed fictício

```powershell
docker compose exec api python -m scripts.seed
```

O script carrega somente dados fictícios e é idempotente. Não execute seeds com dados reais.

## Parar e limpar

```powershell
docker compose down
```

Para apagar também o volume local do banco:

```powershell
docker compose down -v
```

## Configuração do front e CORS

O front deve usar `NEXT_PUBLIC_API_URL=http://localhost:8000`. A variável `CORS_ORIGINS` define as origens permitidas e, por padrão, aceita `http://localhost:3000`. Separe múltiplas origens por vírgula.

## Segurança e escopo

Ainda não há endpoints de dados pessoais. CPF, telefone, banco e chave PIX são protegidos por criptografia em nível de aplicação; a chave Fernet e a chave HMAC do CPF devem permanecer somente no `.env`. Nunca registrar dados pessoais em logs nem expor endpoints pessoais antes de implementar autenticação e autorização. Veja [`docs/lgpd.md`](docs/lgpd.md). Hospedagem, provisionamento e ambientes remotos estão fora do escopo atual.
