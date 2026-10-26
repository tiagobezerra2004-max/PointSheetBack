# Inventário e salvaguardas de dados pessoais

> **Rascunho para revisão.** Este documento descreve o front-end atual e registra salvaguardas exigidas para a integração. Não é parecer jurídico nem aviso de privacidade. A empresa e seu jurídico devem confirmar controlador, operadores, bases legais, prazos, perfis e textos antes do uso com dados reais.

## 1. Escopo e situação atual

O front-end Next.js atende ao cadastro de trabalhadores, frequência e horas extras. A camada de dados usa TanStack Query e, em desenvolvimento, MSW com dados demonstrativos. No momento da análise, não há login, perfis, token, persistência do cache do TanStack Query, `localStorage`/`sessionStorage` usados pela aplicação para dados de trabalhadores, nem chamadas a ferramentas de analytics ou monitoramento de erros identificadas no código. O back-end agora define proteção de CPF, telefone, banco e PIX por criptografia em nível de aplicação, com chaves mantidas fora do repositório.

O mock contém nomes fictícios, CPFs gerados para demonstração, telefones e chaves PIX de domínio reservado (`example.invalid`), além de registros de presença e horas extras fictícios. **Não usar dados reais em desenvolvimento, testes, prompts, logs, issues ou commits.**

## 2. Inventário, finalidade e base legal

| Dado | Onde é coletado/recebido e exibido | Mascaramento atual | Finalidade no produto | Base legal proposta |
|---|---|---|---|---|
| Nome e identificador `trabalhadorId` | Formulário e lista de trabalhadores; seleção em frequência e horas extras; nomes também aparecem em avisos e rótulos acessíveis | Nome não mascarado; ID não é dado exibido normalmente | Identificar cadastro e relacionar registros sem usar o nome como chave | A definir pelo jurídico; avaliar execução de contrato e/ou obrigação legal |
| CPF | Formulário de trabalhador; enviado junto do cadastro/edição; recebido na resposta do trabalhador | Campo visual tipo senha, inicialmente oculto e revelável por até 10 segundos. O valor do estado do formulário, resposta da API e cache não é mascarado pelo front atual | Identificação e cadastro do trabalhador | A definir pelo jurídico; avaliar obrigação legal e necessidade estrita |
| Data de nascimento | Formulário de trabalhador; enviada no cadastro/edição | Não mascarada | Identificação e validação cadastral; eventual cuidado com menor de idade | A definir pelo jurídico; avaliar obrigação legal/execução de contrato e art. 14 quando aplicável |
| Telefone | Formulário de trabalhador; enviado no cadastro/edição | Não mascarado | Contato operacional, se necessário | A definir pelo jurídico; avaliar execução de contrato e necessidade |
| Chave PIX | Formulário de dados de pagamento; enviada no cadastro/edição | Campo visual tipo senha, inicialmente oculto e revelável por até 10 segundos. Valor do estado, API, MSW e cache não é mascarado | Processar pagamento, se aplicável | A definir pelo jurídico; avaliar execução de contrato e obrigação legal |
| Banco | Formulário de dados de pagamento; enviado no cadastro/edição | Não mascarado | Identificar a instituição para pagamento | A definir pelo jurídico; avaliar execução de contrato |
| Titular da chave PIX | Recebido no formulário de pagamento. Quando não é terceiro, o front usa o nome do trabalhador; quando é terceiro, solicita o nome do titular | Não mascarado | Identificar o titular da chave e permitir pagamento | A definir pelo jurídico; avaliar execução de contrato e necessidade de documentar autorização do terceiro |
| Vínculo, função e status | Formulário e lista de trabalhadores; função também aparece nas telas de frequência e horas extras | Não mascarados | Organizar cadastro, elegibilidade operacional e cálculo de horas extras | A definir pelo jurídico; avaliar execução de contrato e/ou obrigação legal |
| Status “Afastado” | Formulário e lista de trabalhadores; afeta elegibilidade na frequência | Não mascarado | Evitar lançamentos incompatíveis com a situação cadastrada | Pode revelar dado de saúde (dado sensível). Não coletar nem registrar motivo de afastamento. Base legal e necessidade devem ser avaliadas especificamente pelo jurídico, inclusive à luz do art. 11 |
| Datas de início e desligamento | Formulário e lista de trabalhadores; usadas na elegibilidade da frequência e avisos de hora extra | Não mascaradas | Manter histórico do vínculo e aplicar regras operacionais | A definir pelo jurídico; avaliar obrigação legal/execução de contrato |
| Código de presença e observação | Tela de frequência; enviados no lote e exibidos na grade semanal/mensal | Não mascarados. A observação é texto livre | Controlar frequência diária | A definir pelo jurídico; avaliar obrigação legal/execução de contrato. Não inserir diagnóstico ou motivo de saúde na observação |
| Data, horas, atividade, observação e valor de hora extra | Formulário e listagem de horas extras; enviadas e recebidas pela API | Não mascarados | Registrar trabalho extra e calcular valores | A definir pelo jurídico; avaliar obrigação legal/execução de contrato. Evitar dados pessoais desnecessários em observação |
| Motivo de edição/exclusão de hora extra e snapshots de auditoria | Formulários de edição/exclusão; enviado ao MSW/API; histórico no mock | Não mascarados. Snapshots podem conter dados de trabalhador e valor calculado | Rastreabilidade e auditoria | A definir pelo jurídico; avaliar obrigação legal/interesse de auditoria, com minimização e retenção definida |
| Identificador e instante de criação do histórico | Criados pelo MSW no histórico de hora extra | Não aplicável | Auditoria de alteração | A definir pelo jurídico. O front ainda não identifica o ator autenticado |

As funções de lista e os schemas atuais de trabalhador incluem CPF, data de nascimento, telefone e objeto de pagamento. A UI da lista não mostra esses campos, mas o payload e o cache de consulta podem conter os valores completos. A API real deve aplicar minimização no servidor: listagens não devem devolver dados pessoais desnecessários e dados sensíveis devem vir mascarados por padrão.

Jovens aprendizes e estagiários podem ser menores de 18 anos. Aplicar cuidado reforçado, restringir acesso e confirmar com o jurídico a necessidade, a base legal e as salvaguardas do tratamento.

## 3. Fluxo, armazenamento e exposição no front atual

- **Coleta e envio:** cadastro/edição de trabalhador envia nome, função, vínculo, status, datas, CPF e, quando informado, telefone e pagamento. Frequência envia trabalhador, data, código e observação. Hora extra envia trabalhador, data, horas, atividade, observação e, em edição/exclusão, motivo. As requisições usam JSON em [`src-do-front/api/`](../src-do-front/api/).
- **Recebimento:** `getWorkers` espera a resposta completa conforme o schema Zod do front. O MSW devolve os objetos completos em memória. Essa resposta inclui CPF, nascimento, telefone e pagamento quando presentes.
- **Cache:** `QueryClient` é criado em memória em [`app-providers.tsx`](../src-do-front/components/providers/app-providers.tsx). Não foi encontrada configuração de persistência para `localStorage` ou `sessionStorage`. Ainda assim, dados retornados permanecem no cache JavaScript durante a sessão e podem estar disponíveis na memória do navegador enquanto a página estiver aberta.
- **Formulário:** CPF e chave PIX têm ocultação visual inicial e botão para revelar por até 10 segundos. Isso não é mascaramento criptográfico nem controle de acesso; valores completos continuam no estado do formulário. Telefone, banco, titular da chave e data de nascimento aparecem sem mascaramento.
- **URL:** não foram encontrados CPF, chave PIX ou telefone em parâmetros de rota ou query. As rotas usam IDs e filtros como datas, trabalhador e atividade.
- **Logs:** não foram encontrados usos de `console.log`, `console.warn`, `console.error`, `localStorage`, `sessionStorage` ou persistência do TanStack Query no front analisado. Não registrar bodies, schemas com dados, mensagens com valores pessoais ou objetos de erro em logs futuros.
- **Mocks:** MSW e arrays de dados fictícios são exclusivos de desenvolvimento no provider atual. Devem permanecer com dados fictícios; nunca carregar dumps de produção.
- **Erros:** o cliente HTTP atual converte o corpo de erro em texto e a UI pode exibir mensagens de erro. A API não deve incluir CPF, chave, telefone ou snapshots sensíveis em mensagens de erro.
- **Estado de afastamento e observações:** status “Afastado” pode inferir saúde; observações são texto livre. Não adicionar campos ou conteúdo de motivo de afastamento sem aprovação, e instruir usuários a não inserir dados de saúde ou outros dados pessoais desnecessários nas observações.

## 4. Acesso e salvaguardas necessárias

Não há autenticação, perfis ou autorização no front atual. A API real não deve expor publicamente endpoints de dados pessoais antes de implementar autenticação e autorização. Aplicar menor privilégio e, no mínimo, definir os seguintes perfis, ainda sujeitos à validação da empresa:

| Perfil proposto | Acesso mínimo a definir |
|---|---|
| Encarregado | Lançamento/consulta operacional de frequência e dados cadastrais estritamente necessários; sem dados de pagamento por padrão |
| Administrativo | Gestão cadastral e consultas necessárias às rotinas administrativas; dados pessoais apenas quando necessários |
| Gestor | Consultas e indicadores necessários à gestão; sem acesso automático a CPF/chave PIX completos |
| Responsável por pagamento | Acesso a dados de pagamento apenas para executar a finalidade de pagamento |

Os nomes e permissões acima são uma proposta inicial, não uma configuração existente. Definir se haverá perfil adicional para pagamento e quais operações cada papel pode executar. Não disponibilizar dados completos de CPF, telefone, PIX ou banco em listagens. A revelação de dado sensível deve ocorrer em endpoint próprio, autorizada e auditada com ator, instante e finalidade; o evento de auditoria não deve conter o valor revelado.

Salvaguardas exigidas para o back-end (as tabelas de negócio e campos cifrados estão definidos na Fase 3; controle de acesso, auditoria de operações e endpoints seguem pendentes):

- Criptografar CPF e chave PIX em nível de aplicação, com chave fora do código e do repositório; proteger segredos por variáveis de ambiente.
- Proteger dados sensíveis em trânsito quando houver hospedagem; HTTP em `localhost` é aceito somente no ambiente local previsto.
- Redigir dados pessoais de logs, erros, auditoria e monitoramento. Limitar snapshots de auditoria ao necessário; não guardar dados sensíveis em claro.
- Aplicar controle de acesso no servidor em cada endpoint; não confiar em ocultação de campos ou rotas no front.
- Permitir localizar dados pelo `trabalhadorId`, corrigir, exportar e anonimizar mediante solicitação, preservando apenas o que houver obrigação de manter.
- Implementar retenção configurável e rotina de anonimização/eliminação real. Soft delete isoladamente não atende ao descarte.
- Criar trilha de acesso a dados pessoais (leitura, revelação, alteração e futura exportação), registrando ator e instante sem incluir o dado pessoal no próprio log.

## 5. Base legal, retenção e responsabilidades pendentes

| Decisão | Estado |
|---|---|
| Controlador e operadores | A definir pela empresa |
| Finalidade e base legal por categoria | Propostas indicadas no inventário; confirmação obrigatória pelo jurídico |
| Encarregado/DPO e canal para titulares | A definir |
| Prazos de retenção por categoria | Pendente de definição pelo jurídico; não presumir nem inventar prazo |
| Regras para menores de 18 anos | Pendente de avaliação jurídica e definição de salvaguardas |
| Dados de pagamento em nome de terceiro e comprovação de autorização | Pendente de definição; coletar somente o necessário e restringir o acesso |
| Texto do aviso de privacidade | Pendente de fornecimento/aprovação jurídica; o front deve recebê-lo de configuração ou endpoint, sem texto jurídico inventado |

Após definição dos prazos, configurar prazos por categoria, executar anonimização ou eliminação ao final do prazo e manter teste da rotina. A retenção deve considerar obrigações trabalhistas, previdenciárias e fiscais confirmadas pelo jurídico.

## 6. Fornecedores e transferências

| Serviço | Situação conhecida | Dados/localização |
|---|---|---|
| API e banco em desenvolvimento local | Planejados para execução via Docker Compose local | Dados de teste fictícios; MariaDB em volume local. Não utilizar dados reais nessa fase |
| Hospedagem | Fora do escopo atual | A definir antes de qualquer implantação; registrar fornecedor, região, operador e transferências |
| Backup | Adiado junto com hospedagem | A definir; quando implementado, deverá ser criptografado e protegido |
| E-mail/transporte de mensagens | Não identificado no front atual | A definir caso seja introduzido; minimizar conteúdo e destinatários |
| Analytics/monitoramento de erros | Não identificado no front atual | Não enviar dados pessoais. Se adotado, fornecedor, local de armazenamento e remoção/redação de dados deverão ser documentados |
| Fontes da interface | Uso de `next/font/google` no build do Next.js | As fontes são configuradas para integração pelo Next.js; confirmar o processo de build/distribuição antes da implantação. Não incluir dados de formulário em requisições de fonte |

Não há transferência internacional ou fornecedor de produção identificado neste momento. Atualizar esta tabela antes de adicionar serviços ou implantar o sistema.

## 7. Incidentes e solicitações de titulares

Procedimento preliminar, sujeito à aprovação do responsável da empresa:

1. Conter o incidente e restringir acessos ou credenciais comprometidas sem apagar evidências necessárias à investigação.
2. Registrar data, sistemas afetados, categorias de dados, volume estimado e medidas adotadas; não copiar valores pessoais para o registro do incidente.
3. Comunicar imediatamente o responsável interno e o encarregado/DPO, quando definido, e preservar evidências com acesso restrito.
4. Avaliar risco aos titulares e definir, com o responsável e o jurídico, se e como comunicar titulares e autoridades, observando as obrigações aplicáveis.
5. Corrigir a causa, revisar acessos e controles, documentar a conclusão e testar as medidas corretivas.

Disponibilizar canal a definir para pedidos de acesso, correção, exportação e anonimização. Localizar registros usando `trabalhadorId`; verificar identidade e autorização antes de atender. Prazos de resposta, responsáveis e fluxo de aprovação dependem de definição jurídica/organizacional.

O sistema deve registrar eventos suspeitos, como várias revelações de CPF em sequência ou acessos fora do padrão, sem incluir o valor do dado nos logs. Limiares, alertas, responsáveis e procedimento de resposta precisam ser aprovados antes da operação real.

## 8. Aviso de privacidade

O front deverá poder exibir o aviso de privacidade fornecido e aprovado pela empresa. Prever configuração ou endpoint para disponibilizar o texto e sua versão/data de vigência. **Não publicar texto jurídico fictício**; conteúdo, canal de contato e mecanismo de atualização estão pendentes.

## 9. Revisão e atualização

Este inventário reflete o código disponível nesta fase de análise. Atualizá-lo a cada fase, especialmente após autenticação, integração da API, inclusão de endpoints de revelação, auditoria, exportação, persistência, monitoramento ou fornecedores. A conformidade depende de validação jurídica e operacional, além das medidas técnicas.
