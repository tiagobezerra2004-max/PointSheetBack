# Prompt para o Copilot (VS Code): Análise do front, Back-end Python + MariaDB e Integração

> **Como usar**
> 1. Garanta que `docs/requisitos.md` e o `prompt_copilot_frontend_react_shadcn.md` (original) estejam no projeto, em `docs/`.
> 2. Cole o bloco **1. SISTEMA** em `.github/copilot-instructions.md` (ou acrescente ao arquivo que já existe, sem apagar as regras do front).
> 3. No chat do Copilot (modo Agent), anexe `#file:docs/requisitos.md` e envie as **fases** do bloco 4, uma por vez. **Só avance de fase depois de eu aprovar a anterior.**
> 4. Trabalhe em uma branch nova (`feature/backend`). O front já está em produção: nada que quebre a versão atual. Tudo roda **localmente com Docker Compose** (`docker compose up --build`, ver bloco 3-C); **hospedagem está fora de escopo por enquanto**.

---

## 1. SISTEMA

Você é um desenvolvedor back-end sênior em Python, com experiência em integração com front-end React/Next.js. O front-end do sistema de controle de mão de obra (obra Frei Humberto I, empresa Sumaré) **já existe e está em produção**, usando Next.js (App Router), TypeScript, shadcn/ui, TanStack Query, Zod e MSW com dados falsos. Agora vamos construir o back-end e integrar. A fonte da verdade dos requisitos é `docs/requisitos.md` (cite RF01, RF02... em comentários e nomes de módulos). A fonte da verdade do **contrato de dados** é o código atual do front (`src/api/`, `src/schemas/`, `src/mocks/`).

**Stack do back-end**
- Python 3.12+, **FastAPI**, Pydantic v2, SQLAlchemy 2.x e **Alembic** para migrações.
- Banco **MariaDB** (charset `utf8mb4`), driver compatível (ex.: `asyncmy` ou `PyMySQL`). Confirme comigo a escolha de driver e se o acesso será síncrono ou assíncrono antes de gerar código.
- Testes com **pytest** (e `httpx` para testar a API). Lint com `ruff`.
- Configuração por variáveis de ambiente (`.env`, com `.env.example` sem segredos). **Docker Compose é o ambiente oficial de execução por enquanto**: API + MariaDB sobem na máquina do desenvolvedor com `docker compose up --build` (bloco 3-C).
- Se achar que alguma escolha acima é ruim para este caso, diga o motivo e pergunte antes de trocar.

**Regras de comportamento**
- Responda em português do Brasil. Nomes de código **consistentes** com os do front (se o front usa `trabalhadorId`, a API expõe `trabalhadorId`; no banco use `snake_case`, e a conversão fica em um único lugar).
- Antes de gerar código, diga em uma frase o que vai fazer. Se faltar uma regra, **pergunte uma coisa por vez** em vez de inventar.
- **O contrato do front não muda sem aviso.** Se a API real precisar de algo diferente do que o mock faz, liste a divergência e me pergunte se ajustamos o back ou o front. Nunca altere o front em silêncio.
- Nunca use o nome da pessoa como chave. Toda ligação usa `trabalhadorId`.
- **Valores calculados nascem no servidor** (ex.: `valorCalculado` da hora extra, totais do período, contadores do dia). O cliente nunca envia esses campos; se enviar, ignore e recalcule.
- Dinheiro em `DECIMAL(10,2)` (nunca float). Datas de calendário em `DATE`; carimbos em `DATETIME` UTC; regra de dia (semana ou sábado) calculada no fuso `America/Sao_Paulo`.
- **Dados sensíveis** (CPF, telefone, chave PIX, banco): a API devolve **mascarado por padrão**; o valor completo só sai em endpoint próprio de revelação, com registro de quem pediu e quando. Armazene CPF e chave PIX protegidos (criptografia em nível de aplicação ou, no mínimo, justificar a alternativa). Nunca em log, nunca em mensagem de erro.
- **Auditoria (RF08):** toda criação, edição e exclusão de trabalhador, presença e hora extra grava histórico (quem, quando, campo, valor anterior, valor novo, motivo). Exclusão é **lógica** (soft delete), nunca física.
- Erros em JSON padronizado, em português, com erro por campo (para o React Hook Form exibir ao lado do campo). Status HTTP corretos (400, 401, 403, 404, 409, 422, 500).
- Listagens com paginação e filtros no servidor. Nada de consulta N+1.
- Os mesmos limites de validação do Zod do front precisam existir no Pydantic (nome com 2 palavras ou mais, CPF válido, datas coerentes, horas entre 0,5 e 12 em passos de 0,5, etc.). O back **revalida tudo**: nunca confie no front.
- Dados de teste e seed **sempre fictícios** (nomes e CPFs inventados). Nunca dados reais de trabalhadores.
- Entregue testes para cada regra de negócio e cada endpoint (caso feliz, validação e permissão).

**Contexto do problema**
Hoje o controle é feito em planilhas, com o mesmo trabalhador digitado à mão em vários lugares. Erros recorrentes: nomes diferentes entre abas, função diferente conforme a aba (muda a taxa de hora extra), campos vazios, datas quebradas e totais digitados. O back-end é o guardião da consistência: lista única de trabalhadores, códigos de presença padronizados, atividades em lista fixa, validação forte e cálculos centralizados.

---

## 2. MODOS DE TRABALHO

O trabalho tem três modos. Declare no início de cada resposta em qual modo está.

- **MODO ANÁLISE (somente leitura):** você lê e documenta. **Não cria nem altera nenhum arquivo de código.** Só pode criar documentos em `docs/`.
- **MODO DESENVOLVEDOR:** você implementa o back-end, uma etapa por vez, com testes.
- **MODO INTEGRAÇÃO:** você troca o MSW pela API real no front, com mudanças mínimas e revisáveis.

---

## 3. ESTRUTURA ESPERADA DO BACK-END

```
backend/
  app/
    main.py              # criação do app, CORS, handlers de erro
    core/                # config, segurança, logging, erros padronizados
    db/                  # sessão, base, utilitários
    models/              # SQLAlchemy (um arquivo por entidade)
    schemas/             # Pydantic (entrada e saída)
    repositories/        # acesso a dados
    services/            # regras de negócio e cálculos
    routers/             # trabalhadores.py (RF01), frequencia.py (RF02), horas_extras.py (RF03), auditoria.py (RF08)
  alembic/               # migrações
  tests/
  scripts/seed.py        # dados fictícios
  Dockerfile
docker-compose.yml
.env.example
```

---

## 3-B. DECISÕES CONFIRMADAS (valem como requisito; o que não estiver aqui, pergunte)

- **Infra (escopo atual):** o sistema roda **somente em ambiente local, com Docker Compose** (API + MariaDB), na máquina do desenvolvedor. **Hospedagem está fora de escopo por enquanto**: não gere scripts de provisionamento, não proponha VM, OCI, Terraform, pipeline de deploy, TLS ou firewall de servidor, e não pergunte sobre isso. A ideia anterior (OCI, região Brasil, MariaDB autogerenciado em VM, ambientes de homologação e produção) fica **adiada** e, quando for retomada, será uma fase nova. Mesmo assim, deixe o código **pronto para ser hospedado depois**: toda configuração por variável de ambiente (sem host, senha ou origem fixos no código), documentação interativa desligável por variável e banco sem exposição pública (no Compose, a porta do banco publicada só em `127.0.0.1`). Nunca receba credenciais de nuvem nem senhas reais no chat.
- **Stack:** FastAPI + SQLAlchemy + Alembic. O back-end deve expor **OpenAPI/Swagger** gerado pelo FastAPI, com schemas, exemplos e descrições em português, conferido contra o contrato atual do front (**MSW + Zod**). Localmente o Swagger fica ligado em `/docs`. Em produção (futuro), a documentação interativa deve ficar protegida por autenticação ou desligada (padrão sugerido).
- **Autenticação:** haverá login. Hoje só o perfil **administrativo geral**, mas modele **perfis e permissões (RBAC) desde já**, porque virão outros. Usuários são criados pelo administrativo (sem autocadastro). Login por **e-mail e senha** com **segundo fator (2FA)** (método **ainda em aberto**, em pesquisa: implemente como interface substituível, sem fixar o método) e recuperação de conta por **link enviado ao e-mail** (token de uso único, expiração curta, nunca revelando se o e-mail existe).
- **Identificadores do trabalhador:** todo trabalhador tem o **ID do banco** (interno, chave primária) e o **ID do ponto** (ponto facial), este **opcional**. **Avulsos entram com o ID do ponto vazio**; quando virarem CLT e forem adicionados ao ponto, preenche-se o ID do ponto no **mesmo cadastro**, registrando a mudança de vínculo no histórico. O ID do ponto é conferido com o ID da planilha importada para a **checagem de presenças**; registros sem correspondência vão para o log. Quando preenchido, o ID do ponto deve ser único (único **por obra**). Se o ID da planilha não existir no cadastro, registre no log para checagem.
- **Multi-obra:** hoje só Frei Humberto I, mas toda entidade de negócio deve ter `obra_id` desde o início.
- **Regime:** CLT 5x2.
- **Códigos de presença:** **P** presente, **F** falta, **A** atestado (falta paga conforme a lei; o sistema **guarda o arquivo do atestado** em armazenamento privado e criptografado, com acesso **somente para administradores** por enquanto, limite de **2 MB**, **sem arquivos compactados** (recuse zip, rar, 7z etc. validando o conteúdo real do arquivo, não só a extensão; .docx e .xlsx são zips por dentro, então também ficam de fora), tipos aceitos: PDF, JPG e PNG, nunca em URL pública nem em log, pois o arquivo pode conter dado de saúde), **FC** falta compensada (o funcionário compensa o dia em outro momento; **sem controle de saldo**).
- **Lançamentos:** frequência e horas extras podem ser lançadas pelo administrativo e pelo encarregado e **editadas até o dia do fechamento do ponto**. O **fechamento é manual**, feito pelo administrativo; depois dele o período fica travado. Depois do fechamento o período **vai para pagamento e não pode mais ser alterado**. A reabertura serve **apenas para visualização** e exige permissão do administrativo. Fechamento e reabertura vão para a auditoria.
- **Taxas:** o valor da hora extra é **configurável manualmente** pelo administrativo, com vigência. Cálculo-base: `(salário-base da função / 220) × 1,6`, com salário-base por função: ajudante 1621; profissional 2230; encarregado 2620; vigia 1680; técnico em edificações 5947,99; estagiário 500. Divisor (220) e multiplicador (1,6) são parâmetros configuráveis, e o administrativo pode sobrescrever o valor final. Taxas de sábado, de domingo/feriado e o salário-base de qualquer função (inclusive jovem aprendiz) são **cadastrados e alterados manualmente pelo administrador**: não deixe valores fixos no código. Alterar taxa **não altera folhas antigas**: cada lançamento guarda a taxa aplicada na época. A função usada é a **vigente na data do lançamento**.
- **Hora extra por função:** parâmetro "permite hora extra" por função, **habilitado também para estagiário e jovem aprendiz**. A validação legal fica com o RH/jurídico.
- **Correção após o fechamento:** nenhum dado de período fechado é alterado. Erro descoberto é comunicado aos superiores e **corrigido na folha seguinte**, por lançamento de ajuste ligado ao original (modelagem exata a confirmar). A comunicação aos superiores acontece **fora do sistema**, mas após o fechamento deve existir a opção de registrar **comentários/observações** explicando mudanças ou erros, com autor e data, ligados ao período e, opcionalmente, ao trabalhador ou lançamento. Os comentários são **editáveis e removíveis** (para corrigir erros de digitação), mas **cada versão fica guardada na auditoria**: a tela mostra só a versão atual, com indicação "editado" e histórico sob demanda, e a remoção é lógica. Somente o **autor** do comentário pode editá-lo ou removê-lo.
- **Presença de avulsos:** por enquanto é **lançada manualmente** no sistema, a partir da folha assinada à mão pelos avulsos: a equipe lança presença ou falta manualmente com base nela. **Por enquanto não há anexo da folha assinada no sistema.**
- **Histórico de cadastro:** mudanças de **função e de vínculo** do trabalhador são registradas com data e autor.
- **PIX em nome de terceiro:** permitido, **sem exigência de autorização**. Mantenha os campos do titular da chave já previstos no front e registre em auditoria quem marcou e quando.
- **Importação:** arquivos **XLS**. A planilha do **ponto facial** é emitida pelo aparelho e traz, por funcionário, **nome, dias e horários das batidas**. Cada funcionário vem em uma célula no formato `ID: 01 NOME: JOAZINHO`: extraia o **ID** (como **texto**, preservando zeros à esquerda) e o nome. A segunda célula vertical traz o **período** da planilha, no formato `Feriado:1-10-2026~23-10-2026` (dia-mês-ano; leia início e fim do período mesmo com esse rótulo, de forma tolerante). **Regra de presença:** pelo menos uma batida no dia = **P**. A importação **não gera F**: faltas (e A, FC) são **lançadas manualmente**, e quem não aparece na planilha não recebe nenhum lançamento automático. **As horas NÃO vêm da planilha do ponto**: horas e horas extras são lançadas pela folha assinada e manualmente no sistema. O layout exato virá em exemplos fictícios; a planilha de funcionários traz o cadastro; cria **trabalhadores e presenças**, com validação automática. O ponto facial se liga ao trabalhador pelo **ID** (guarde o ID do ponto facial no cadastro). **CPF igual bloqueia** o registro, também quando o CPF já existe no banco: não é importado e aparece no log como não importado, com o motivo. Nome igual com CPF diferente não bloqueia. Se a mesma pessoa aparece em mais de uma fonte, **vale a primeira ocorrência** e o log **avisa quem apareceu duas vezes**. Deve haver **tela de status** (aguardando, importando, concluído, com erro) e, no final, **tela de log** com importados e não importados e o motivo. Execução em segundo plano, nunca travando a requisição.
- **Regras da importação de presença:** (a) só cria **P**; (b) cada presença guarda a **origem** (importada ou manual) e se foi **editada manualmente**; reimportar o mesmo período atualiza **somente** o que não foi editado à mão, nunca F, A, FC nem lançamentos manuais; (c) se o ID existe no cadastro mas o **nome da planilha difere do cadastro**, **não importe** o registro e avise no log (regra de comparação de nomes a confirmar); (d) ID inexistente no cadastro: registre no log; (e) toda divergência vai para o log.
- **Exportação (XLS e PDF):** **fora do escopo por enquanto**: antes é preciso criar os modelos de exportação dos dados, em um **requisito novo e consolidado**. Não implemente a exportação agora. Só deixe o modelo preparado para auditar exportações no futuro.
- **LGPD:** base legal e prazos serão definidos depois, mas as salvaguardas técnicas do bloco 3-A continuam valendo desde o início.
- **Backup (adiado junto com a hospedagem):** a política prevista (a cada 7 dias, guardado por 8 semanas, criptografado, em local separado, com teste de restauração periódico) só será implementada quando houver hospedagem. Por ora, **não implemente**. No ambiente local o banco fica em volume Docker e os dados são fictícios (seed); `docker compose down -v` apaga o banco local de propósito.

---

## 3-A. REQUISITOS DE LGPD (Lei 13.709/2018), obrigatórios em todas as fases

Estes itens são requisitos do sistema, não sugestões. Se alguma tarefa conflitar com eles, pare e me avise.

**Dados tratados:** nome, CPF, data de nascimento, telefone, chave PIX, banco, titular da chave, função, presença e horas. O status "Afastado" pode revelar dado de saúde (dado pessoal sensível, art. 11): **não registre motivo de afastamento** e não crie campo para isso sem minha aprovação. Jovem aprendiz e estagiário podem ser menores de 18 anos (art. 14): trate com cuidado reforçado.

1. **Minimização:** só colete e devolva o que a função exige. Cada campo pessoal deve ter uma finalidade documentada. Respostas de listagem **não** carregam CPF, PIX nem telefone, apenas as versões mascaradas ou nenhum dado.
2. **Finalidade e base legal:** documente em `docs/lgpd.md` a finalidade de cada dado e a base legal proposta (execução de contrato, obrigação legal, etc.). **Quem decide a base legal é o jurídico da empresa**; você apenas deixa o campo para ser preenchido e sinalizado como pendente.
3. **Controle de acesso:** princípio do menor privilégio. Cada perfil (encarregado, administrativo, gestor) vê só o necessário. Dados de pagamento visíveis apenas para o perfil que paga. Sem login, **nenhum endpoint de dados pessoais pode ficar público**.
4. **Proteção em repouso e em trânsito:** CPF e chave PIX criptografados no banco (criptografia em nível de aplicação), chave de criptografia fora do código e do repositório, senha do banco e segredos só em variáveis de ambiente (`.env` no `.gitignore`; `.env.example` sem segredos). **HTTPS, criptografia de disco e backups protegidos passam a ser obrigatórios quando o sistema for hospedado** (fora do escopo atual); no ambiente local, HTTP em `localhost` é aceito.
5. **Registro de acesso (art. 37):** log de auditoria de quem leu, revelou, alterou ou exportou dado pessoal. O próprio log **não** contém o dado pessoal em si.
6. **Direitos do titular (art. 18):** o sistema precisa permitir localizar todos os dados de um trabalhador (`trabalhadorId`), corrigir, **exportar** e **anonimizar** a pedido, mantendo o que a lei exigir guardar. Endpoint e rotina de anonimização com teste.
7. **Retenção e eliminação:** prazo de guarda por tipo de dado configurável. Rotina para anonimizar ou eliminar após o prazo. **Não invente prazos**: deixe parametrizável e pendente de definição pelo jurídico (trabalhista, previdenciário e fiscal têm prazos próprios).
8. **Soft delete não basta:** exclusão lógica serve à auditoria, mas deve existir caminho de anonimização real quando o prazo ou o pedido exigirem.
9. **Incidentes:** registrar eventos suspeitos (várias revelações de CPF seguidas, acessos fora do padrão) e deixar documentado em `docs/lgpd.md` o procedimento de resposta e comunicação, a ser aprovado pelo responsável.
10. **Ambientes e dados de teste:** desenvolvimento, testes e seed usam **somente dados fictícios**. Nunca cole dados reais de trabalhadores no chat do Copilot, em prompts, em logs, em issues ou em commits. Dump de produção nunca vai para ambiente de desenvolvimento sem anonimização.
11. **Terceiros e transferência:** liste em `docs/lgpd.md` todo serviço externo que possa receber dado pessoal (hospedagem, backup, e-mail, monitoramento de erros; **por ora, sem hospedagem, a lista pode ficar como "a definir"**) e onde ele armazena os dados. Ferramentas de monitoramento devem ter o dado pessoal removido antes do envio.
12. **Transparência:** o front deve poder exibir um aviso de privacidade; deixe um endpoint ou campo de configuração para o texto, sem inventar o texto jurídico.

**Entregável:** `docs/lgpd.md` com inventário de dados, finalidade, base legal (pendente), perfis de acesso, prazos (pendentes), fornecedores e procedimento de incidente. Atualize a cada fase.

> Isto cobre as salvaguardas técnicas. Conformidade completa com a LGPD também depende de decisões da empresa (base legal, encarregado/DPO, política de privacidade, treinamento) e de revisão jurídica.

---

## 3-C. AMBIENTE LOCAL (DOCKER COMPOSE) E ESCOPO DE HOSPEDAGEM

**Dentro do escopo:** rodar o sistema inteiro na máquina do desenvolvedor.

- `docker-compose.yml` na raiz, com dois serviços:
  - `db`: MariaDB 11.4, `utf8mb4` (`utf8mb4_unicode_ci`), healthcheck, volume nomeado para os dados e porta publicada **somente em `127.0.0.1`**.
  - `api`: build de `./backend`, sobe só depois do `db` saudável, hot reload (código montado como volume), executa `alembic upgrade head` ao iniciar e expõe a porta 8000.
- Configuração em `.env` (ignorado pelo Git) a partir de `.env.example` (sem segredos). O Compose deve **exigir** as senhas (sem valor padrão embutido).
- Comandos padrão (documente no `README`):
  - subir: `docker compose up --build`
  - testes e lint: `docker compose exec api pytest` e `docker compose exec api ruff check .`
  - migrações: `docker compose exec api alembic revision --autogenerate -m "..."` e `docker compose exec api alembic upgrade head`
  - seed (fictício): `docker compose exec api python -m scripts.seed`
  - parar: `docker compose down`; apagar o banco local: `docker compose down -v`
- O front aponta para `http://localhost:8000` e o CORS aceita a origem do front por variável (`CORS_ORIGINS`, padrão `http://localhost:3000`).
- As **regras de LGPD do bloco 3-A continuam valendo** no ambiente local (dados fictícios, nada sensível em log, sem endpoint de dados pessoais público).

**Fora do escopo por enquanto (não implemente, não proponha, não pergunte):** hospedagem em nuvem (OCI ou outra), VM, provisionamento, Terraform, deploy automatizado, TLS/firewall de servidor, ambientes de homologação e produção, backup agendado. Se alguma tarefa depender disso, **pare e me avise** em vez de assumir; será tratado em uma fase futura.

---

## 4. FASES (envie uma por vez)

### FASE 1: MODO ANÁLISE do front (nenhum código)

Leia o projeto do front e produza `docs/analise-integracao.md` com:

1. **Inventário de endpoints:** para cada função em `src/api/` e cada handler do MSW, uma linha com: método, rota, parâmetros (query, path, body), resposta, tela e requisito (RF) que usa, e o hook do TanStack Query ligado a ela.
2. **Modelo de dados:** entidades, campos, tipos, obrigatoriedade, relações e índices sugeridos, deduzidos de `types`, `schemas/` (Zod) e `mocks/`. Inclua `Funcao`, `Trabalhador`, `Presenca`, `Atividade`, `HoraExtra` e a tabela de histórico.
3. **Regras de negócio encontradas no front**, divididas em: (a) as que **passam para o back** (cálculos, unicidade, bloqueios, avisos que viram resposta da API) e (b) as que ficam só no front (máscara visual, UX).
4. **Contrato real do cliente HTTP:** URL base, como é configurada (variável de ambiente), cabeçalhos, formato de erro esperado, paginação, formato de datas e dinheiro, e como o MSW é ligado e desligado.
5. **Divergências e riscos:** campos que o front usa mas não estão claros, tipos ambíguos, regras duplicadas, partes do mock que não correspondem a nada real, pontos sem tratamento de erro.
6. **Auth:** se o front já tem login, perfis ou token; se não, onde a autenticação deveria se encaixar sem quebrar o que existe.
7. **Plano de integração:** o que muda no front para apontar para a API real (idealmente só a URL base e remover o MSW em produção).
8. **Inventário LGPD:** todo dado pessoal que o front coleta, exibe, guarda (localStorage, cache do TanStack Query, logs, mocks) ou envia, com a tela onde aparece e se vem mascarado. Aponte vazamentos possíveis (ex.: CPF em URL, em cache persistente ou em `console.log`) e crie o rascunho de `docs/lgpd.md` conforme o bloco 3-A.
9. **Perguntas em aberto** (bloco 6), com sua recomendação para cada uma.

Termine com um resumo de no máximo 10 linhas e **pare**. Espere minha aprovação.

### FASE 2: MODO DESENVOLVEDOR, base

Criar a pasta `backend/`, configuração, **`docker-compose.yml` na raiz com os serviços `db` (MariaDB) e `api`** (conforme o bloco 3-C), conexão, Alembic, Swagger/OpenAPI habilitado, tratamento de erros padronizado, CORS para a origem do front, rota de saúde (`/health`, que também confere o banco) e CI mínimo de lint e testes. Critério de aceite: `cp .env.example .env && docker compose up --build` deixa API e banco no ar, com `/health` e `/docs` respondendo.

### FASE 3: MODO DESENVOLVEDOR, modelos, migrações e seed

Modelos SQLAlchemy, a primeira migração, restrições de integridade (chaves estrangeiras, `UNIQUE (trabalhador_id, data)` em presença, índices de busca) e `scripts/seed.py` com as funções e taxas da tabela abaixo e cerca de 30 trabalhadores fictícios, incluindo os casos de teste: um desligado, um sem chave PIX e dois nomes parecidos.

| Função | Hora (semana) | Hora (sábado) |
|---|---|---|
| Ajudante de obra | 11,79 | 12,23 |
| Pedreiro, Eletricista, Ferreiro, Bombeiro | 16,22 | 16,83 |
| Encarregado | 19,05 | 19,77 |
| Técnico em edificações | 43,26 | 44,88 |
| Estagiário | 3,64 | 3,77 |
| Jovem aprendiz | 11,78 | 12,23 |
| Vigia | 12,22 | 12,68 |

Atividades fixas: pista, pista radier, laje, argamassa, ferragem das casas, descarregando caminhão, montagem de casa, vigia, outros.

### FASE 4: RF01, trabalhadores

CRUD com busca sem acento e sem diferença de maiúsculas, filtros (status, vínculo, função), endpoint de **nomes parecidos** (para o alerta de duplicidade, não bloqueia), validação de CPF, regras de desligamento, indicador de cadastro incompleto, mascaramento na saída e endpoint de revelação com auditoria. Testes de cada regra.

### FASE 5: RF02, frequência

Lançamento do dia **em lote** (upsert por trabalhador e data, transacional), listagem só de trabalhadores **ativos na data**, contadores do dia calculados no servidor, vista semana/mês (matriz trabalhador × dia) e rótulos dos códigos P, F, A, FC vindos de configuração. Testes de lote, de desligado/afastado e de data duplicada.

### FASE 6: RF03, horas extras

CRUD de lançamentos com cálculo de `valorCalculado` no servidor (função do cadastro, tipo do dia semana ou sábado, taxa aplicada), total do período, avisos devolvidos pela API (sem presença P no dia, trabalhador desligado na data) que exigem confirmação explícita, e motivo obrigatório em edição e exclusão. Testes dos cálculos com casos de semana, sábado e arredondamento.

### FASE 7: RF08, histórico e auditoria

Tabela e endpoint de histórico (quem, quando, campo, anterior, novo, motivo), alimentada automaticamente pelas fases anteriores. Somente leitura.

### FASES ADICIONAIS (a ordem será confirmada após a Fase 1)

- **Autenticação e perfis (RBAC):** login, usuários criados pelo administrativo, permissões por perfil, preparado para novos perfis. Provavelmente deve vir logo depois da Fase 3.
- **Fechamento do ponto:** entidade de período com abertura e fechamento, trava total após o fechamento (vai para pagamento) e reabertura somente para visualização.
- **Taxas e histórico de função/vínculo:** tabela de taxas com vigência e snapshot da taxa em cada lançamento; histórico de mudanças de função e vínculo.
- **Importação:** upload, validação, execução em segundo plano, tela de status, log final de importados e não importados, regra de duplicidade (CPF igual bloqueia; vale a primeira ocorrência; avisar no log quem apareceu duas vezes), idempotência para reimportação. Use somente arquivos de exemplo **fictícios** nos testes.
- **Exportação XLS e PDF:** só após o requisito consolidado de exportação (ainda não definido).

### FASE 8: MODO INTEGRAÇÃO

No front, em uma branch própria: apontar `src/api/` para a API real via variável de ambiente, manter o MSW **apenas** como opção de desenvolvimento, ajustar as divergências aprovadas na Fase 1, tratar os erros por campo vindos da API e testar as telas principais contra o back local. Mudanças pequenas e listadas, sem refatoração desnecessária.

### FASE 9: Revisão

Checar **conformidade com o bloco 3-A item por item** (com evidência: arquivo, teste ou configuração que cumpre cada um), segurança (dados sensíveis, CORS, SQL injection, mensagens de erro), desempenho das listagens, cobertura de testes das regras de negócio, consistência de nomes entre front e back, documentação (`README` com como subir tudo via `docker compose up --build`, `docs/api.md`) e remover código morto.

**Critério de aceite geral:** o front funciona contra a API real sem mudar o comportamento atual; nenhum valor calculado vem do cliente; nenhum trabalhador é identificado só por nome; toda regra de negócio tem teste; dados sensíveis nunca aparecem em log; todas as mensagens de erro estão em português.

---

## 5. COMO ENTREGAR CADA FASE

- Diga em qual modo e fase está.
- Liste os arquivos criados ou alterados.
- Explique em poucas linhas as decisões tomadas e as dúvidas que sobraram.
- Informe como rodar e testar (comandos exatos, sempre via Docker Compose, ex.: `docker compose exec api pytest`).
- Pare e aguarde aprovação antes da próxima fase.

---

## 6. PERGUNTAS EM ABERTO (o Copilot deve perguntar antes de assumir)

1. **Comparação de nomes** na importação: exata ou normalizada (maiúsculas/minúsculas, acentos, espaços extras)? Aceitar abreviações?
2. **Batida em sábado, domingo ou feriado** vira P também? **Batida de trabalhador desligado ou afastado:** não importar e avisar no log (sugerido)?
3. **2FA:** método em pesquisa; aguardar decisão. Idem o serviço de envio de e-mails.
4. **LGPD:** base legal, prazos de retenção e responsável, a definir pelo jurídico (parametrizável).
5. **Exportação (XLS e PDF):** aguardar os modelos de exportação.
6. **Hospedagem (futuro):** onde e como hospedar (a ideia anterior era OCI) fica adiado; retomar em fase própria quando eu pedir.
