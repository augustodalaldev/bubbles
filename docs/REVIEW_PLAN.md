# Plano de revisão, integração e polimento — Bubbles

> Data da revisão: 2026-11-17. Commit base: `5eeeb6d`.

## Contexto
O projeto foi construído em boa parte por um modelo mais fraco. O backend (8 apps, 62 rotas) está bem testado, mas tem falhas de regra de negócio e de robustez. O frontend é quase todo mockado. Objetivo: corrigir os bloqueantes, padronizar o contrato da API, ligar todas as telas existentes à API real e polir, **sem funcionalidades novas**.

---

## 1. Resumo do estado atual

### Verificações executadas (somente leitura)
| Verificação | Resultado |
|---|---|
| `uv run pytest` (settings test, PostgreSQL 17 no Docker) | **375 passed**, 0 falhas, 3.5s |
| `manage.py check` | Nenhum problema |
| `check --deploy --settings=config.settings.prod` | W004 (HSTS) e W008 (SSL redirect) |
| `makemigrations --check --dry-run` | "No changes detected" |
| `ruff check` / `ruff format --check` | Ok (156 arquivos) |
| `runserver` + curl | Sobe; `/health/` ok; erros DRF no envelope; 404 fora do DRF devolve **HTML** |
| `manage.py spectacular` | Sem warnings |
| Frontend `tsc --noEmit` | Ok |
| Frontend `vite build` | Ok; aviso de chunk de 504 kB |
| Versão do Python | `.python-version` = 3.12; venv = 3.12.3; `requires-python >=3.12`. Os `__pycache__` estão ignorados pelo git. |

### O que funciona
- Backend completo para os pilares 1 a 6, com envelope de erro `{"error":{code,message,fields,...extras}}`.
- O soap passa por `economy.services` com lock ordenado por PK, custos vêm do `EconomySettings` e os contadores usam `F()`.

### O que está quebrado
- Login e cadastro no frontend leem o token do caminho errado.
- Há falhas de regra no backend (ver §3).
- Não existe limite real de tamanho de upload.
- Há um bypass de validação de imagem.

### O que está só mockado
Todo o frontend, exceto login/cadastro/`me`/heartbeat. São 20 exports `MOCK_*` em `features/profile/mockData.ts` (897 linhas).

### Divergências entre docs e código
| Doc | Diz | Código |
|---|---|---|
| ER.md | `Comment.text` max 1000 | 2000 (DECISIONS diz 2000) → corrigir o **ER** |
| ER.md | BubblegramMedia "1..N" | 1..4 no service → corrigir o ER |
| DECISIONS P1.3 / skill | Access token em memória | localStorage (frontend) |
| DECISIONS P6 | Ajuste de soap audita saldo antes e depois | Só `balance_after` |
| DECISIONS P4 | `/economy/settings/` | Ok; `updated_by_username` some quando `null` |
| DECISIONS P5 | Só `/customization/equip/` | Existe também o alias `/equipped/` (não documentado) |
| DECISIONS S4 / skill | Comunidade compra customização com soap da comunidade | Não implementado; `customization_json` da comunidade é aceito **sem pagar** |
| frontend/PLAN.md §1.5 | Ganho passivo "+5/dia" | Regra real: +5 a cada 5 min, teto de 15/dia |
| frontend/PLAN.md §6.1 | Backend limita upload a 10 MB | Não limita (`FILE_UPLOAD_MAX_MEMORY_SIZE` é limiar de memória) |
| Skill bubbles-dev | React Router, TanStack Query, react-hook-form/zod, Vitest | Nada disso instalado; navegação por `useState`, zustand e axios |
| PROGRESS.md | Tudo `[x]` | O frontend não está integrado (não consta no PROGRESS) |
| DECISIONS P4 | Comandos periódicos "via cron" | Nenhum agendamento existe (aceitável; documentar) |

---

## 2. Matriz de integração frontend ↔ API

Legenda de status: **ok**, **parcial**, **ausente** (só mock), **divergente** (chama, mas errado).
A correção é sempre no frontend, salvo quando indicado.

| Tela / ação | Endpoint real | Status | Ajuste |
|---|---|---|---|
| Login | `POST /auth/login/` → `{access,user}` | divergente | Ler `data.access`; erros via `error.code`; remover "entrar como Marina" |
| Cadastro | `POST /auth/register/` (201 `{access,user}`) | divergente | Idem; mapear `error.fields` por campo |
| Bootstrap de sessão | `POST /auth/refresh/` (cookie) + `GET /users/me/` | parcial | No boot: refresh → me; refresh single-flight; **não** enviar Bearer para `/auth/*` (o backend falha com Bearer expirado: corrigir **também no backend** com `authentication_classes=[]`) |
| Logout | `POST /auth/logout/` | ausente | Botão de sair. **Backend:** `AllowAny` para conseguir limpar o cookie com o access expirado |
| Heartbeat | `POST /auth/heartbeat/` | parcial | Hoje nada o chama: chamar a cada 5 min quando logado. **Backend:** o throttle `user` 1000/dia estoura com uso real (§3) |
| Header (saldo, avatar) | `users/me` (`soap_balance`) | ausente | Ler do store; texto do ganho passivo vindo de `GET /economy/settings/` |
| Guarda de rota | — | ausente | Sem sessão: só login/cadastro; esconder "Entrar/Cadastrar" quando logado |
| Feed | `GET /feed/` (PageNumber) | ausente | Paginação "carregar mais" + fim do feed; `is_suggested`/`suggestion_reason` já tipados |
| Filtros do feed (seguindo/comunidades/popular) | — (o backend não filtra) | divergente | Filtrar no cliente sobre a página carregada, ou remover a aba "popular" (**decisão Q4**) |
| Busca do Header | `GET /search/?q=` → `{query,users,communities}` | ausente (filtra mock) | Usar `/search/`; a busca de "postagens" não existe → ajustar o placeholder |
| Bandeja de bubblepops | `GET /feed/bubblepops/` (lista simples) | ausente | — |
| Criar bubblegram (popup +) | `POST /bubblegrams/` multipart `text,type,media_files[]` | ausente | FormData; custo vindo de settings; atualizar saldo via `me` |
| Apoiar post | `POST /bubblegrams/{id}/support/` → `{soap_count}` | ausente | Usar o `soap_count` retornado; refazer `me`; tratar `insufficient_soap` (409, `cost`/`balance`), `already_supported`, `self_support_not_allowed` |
| Excluir post | `DELETE /bubblegrams/{id}/` | ausente | Só exibir se `can_delete` |
| Modal do post + comentários | `GET/POST /bubblegrams/{id}/comments/` (`text,parent_id`), `POST /comments/{id}/support/`, `DELETE /comments/{id}/` | ausente | Montar a árvore pelo `parent` |
| Perfil (próprio e de outros) | `GET /users/{u}/`, `/users/{u}/bubblegrams/`, `/users/{u}/bubblepops/`, `/users/{u}/followers/`, `/following/` | ausente | O perfil precisa receber `username`; hoje só existe o próprio |
| Seguir / deixar de seguir | `POST`/`DELETE /users/{u}/follow/` | ausente | Perfil e sidebar de sugestões |
| Sugestões de usuários (sidebar) | — (não há endpoint) | divergente | **Decisão Q5**: remover ou derivar dos `is_suggested` do feed |
| Hub de comunidades | `GET /communities/?search=&mine=true` | ausente | Abas Todas/Minhas |
| Criar comunidade | `POST /communities/` (multipart) | ausente | Mostrar `founding_cost` e o saldo; tratar `insufficient_soap` |
| Detalhe da comunidade | `GET /communities/{c}/`, `/members/`, `/bubblegrams/` | ausente | Botões guiados por `permissions` |
| Entrar / sair | `POST /communities/{c}/join/`, `/leave/` | ausente | — |
| Editar diretrizes / foto | `PATCH /communities/{c}/guidelines/`, `PATCH /communities/{c}/` | ausente | Só com `can_edit_guidelines`/`can_edit` |
| Postar na comunidade | `POST /bubblegrams/` com `commname` | ausente | — |
| Moderar membros, promover, transferir, arquivar | Endpoints existem | ausente na UI | **Pendência de requisito** (a tela não existe; não será criada sem sua decisão, Q6) |
| Loja | `GET /customization/items/`, `POST /customization/items/{id}/purchase/` → `{inventory_item,remaining_soap}` | ausente | `is_owned`/`is_equipped` vêm do backend |
| Equipar / desequipar | `POST /customization/equip/` `{slots:{slot:id\|null}}` | ausente | Usar `slots` (não `item_ids`, que desequipa os outros slots) |
| Inventário | `GET /customization/inventory/` | ausente | — |
| Cartas: caixa de entrada e enviadas | `GET /letters/inbox/`, `/letters/sent/` | ausente | — |
| Abrir carta | `GET /letters/{id}/` (marca como lida) | ausente | — |
| Escrever / responder carta | `POST /letters/` `recipient_username,text,reply_to_id,image` | ausente | Destinatários = `following`; tratar `not_following`, `already_replied` |
| Criar bubblepop | `POST /bubblepops/` `image,duration_hours,description` | **sem UI** (botão morto no perfil; o feed mostra `alert`) | **Decisão Q3** |
| Editar perfil / excluir conta | `PATCH`/`DELETE /users/me/` | sem UI | Pendência de requisito (Q6) |
| Carteira / extrato | `GET /users/me/wallet/` | sem UI | Pendência (Q6) |
| Denúncias / admin | `/reports/`, `/admin/*` | sem UI | Pendência (Q6); a moderação segue pelo Django Admin |
| Notificações (sino), "Esqueceu a senha?", compartilhar | — | sem backend | Remover (contradiz DECISIONS Q6 e os princípios de produto) |

### Tipos (`frontend/src/types/index.ts`) a ajustar
- **`User`:**
  - adicionar `last_seen_at?` (usado em `authStore`);
  - remover `is_staff` (não existe);
  - as URLs de foto podem ser relativas ou absolutas.
- **`Bubblegram.community`:** vem como `{id,commname,name}`, não `Community`. Criar `CommunityRef`.
- **`Bubblepop`:** adicionar `is_expired` e `can_delete`.
- **Novos tipos:** `Comment`, `Paginated<T>`, `ApiError`, `EconomySettings` (`updated_by_username?` opcional), `SearchResult`, `FollowItem`, `Wallet` com `results: SoapTransaction[]`.
- **`Community`:** remover `is_blocked` (o backend não envia); `archived_at` existe só no detalhe.

---

## 3. Lista de problemas

Severidades: **B** = bloqueante, **I** = importante, **P** = polimento. ⚠ = mexe em model ou migration (ver §3.4).

### 3.1 Backend: regras de negócio e bugs
| # | Arquivo:linha | Problema | Sev. | Correção |
|---|---|---|---|---|
| B01 | content/views.py:56-60 | `request.FILES.getlist("images")` pula o serializer: qualquer arquivo (.html/.svg) é salvo e servido em `/media/` | **B** | Remover o alias `images`; só `media_files` validado |
| B02 | settings/base.py:124-125 | Não há limite de tamanho de upload (comentário falso) | **B** | Validador `validate_image_upload` em `core/uploads.py` (≤10 MB, whitelist JPEG/PNG/WebP/GIF via Pillow) aplicado em todos os ImageFields de serializer |
| B03 | communities/services.py:318-341 | Membro BANNED usa `/leave/`, apaga o ban e volta a entrar | **B** | Rejeitar leave de BANNED (`member_banned`); `can_leave=False` no selector |
| B04 | content/services.py:358-366, 471-477 | Não membro apoia conteúdo de comunidade | **B** | Exigir membership ACTIVE |
| B05 | settings/base.py throttle `user: 1000/dia` | Heartbeat mais o uso normal estouram: 429 para usuários ativos | **B** | Subir para um valor realista (ex.: `10000/day`) |
| B06 | accounts/views.py Login/Register/Refresh | Bearer expirado no header → 401 antes da view | **B** | `authentication_classes = []` |
| B07 | content/services.py:536 | Bubblepop sem checar `is_suspended` | I | Adicionar a checagem |
| B08 | content/serializers.py:193 | Limite 1..48 h fixo; ignora `EconomySettings` | I | Remover min/max fixos; o service valida |
| B09 | content/selectors.py:70-75 | Bubblepop expirado legível por id | I | Filtrar `expires_at > now` |
| B10 | customization/services.py:21-37 | Compra concorrente → IntegrityError 500 | I | Capturar → `already_owned` |
| B11 | moderation/services.py:54-74, views.py:255 | id não numérico → 500 | I | Validar no serializer → 400 |
| B12 | moderation/services.py:126-130 | INVESTIGATING registra `REPORT_DISMISS` | I | Só auditar RESOLVED/DISMISSED (ou ação correta) |
| B13 | moderation/services.py:406-417 | Auditoria sem `balance_before` (DECISIONS P6) | I | Adicionar em `metadata` |
| B14 | communities/services.py:530-538, 355-418, 321-341 | Sem lock na membership → `member_count` diverge; transferência concorrente → 500 | I | `select_for_update` na linha de membership/comunidade |
| B15 | communities/services.py:174,241,542 | Comunidade bloqueada ainda editável/arquivável (contradiz `permissions`) | I | Checar `is_blocked` |
| B16 | communities/services.py create/update | `customization_json` da comunidade aceito sem validar posse | I | Rejeitar chaves não vazias (a compra pela comunidade não existe; Q7) |
| B17 | accounts/views.py:160 | Logout exige access válido | I | `AllowAny` + usa o cookie |
| B18 | accounts/views.py:122 refresh | Não verifica usuário ativo/não deletado; refresh sem throttle | I | Checar `is_active`/`deleted_at`; `throttle_scope="auth"` |
| B19 | economy/services.py:258 | O teto diário do ganho passivo reseta à meia-noite **UTC** (21h local) | I | Usar `timezone.localtime` |
| B20 | social/selectors.py:32-34 + views.py:31 | Selector grava `read_at`; responder marca o original como lido | I | Mover para o service `mark_letter_as_read` (já existe); a view de detalhe o chama |
| B21 | content/services.py:187,616,626; accounts/services.py:267 | Arquivos apagados dentro do `atomic` | P | `transaction.on_commit` |
| B22 | serializers com `source="x.username"` (economy, moderation) | O campo some quando o FK é null | I | `SerializerMethodField` → null |
| B23 | accounts/views.py, communities/views.py (vários) | URLs de imagem relativas em alguns endpoints e absolutas em outros | I | Passar `context={"request":request}` em todos |
| B24 | economy/services.py:71,159,189 | Custo 0 no settings quebra os fluxos | P | Pular o movimento quando o valor é 0 |
| B25 | iexact em backends/selectors | Ignora índices | P | `exact` em valores já minúsculos (username/commname/email) |
| B26 | CurrentUserSerializer | Sem `is_staff` | P | Adicionar (read-only). É necessário para o frontend saber se pode exibir PATCH de settings, mas não será usado em telas novas |
| B27 | moderation/admin.py; models | Report/AuditLog editáveis e deletáveis no admin | P | Admin read-only para AuditLog |
| B28 | social/selectors.py:25-30 | Carta alheia → 403 (vaza existência) | P | 404 |

### 3.2 Backend: contrato e erros (`core/exceptions.py`)
| # | Problema | Sev. | Correção |
|---|---|---|---|
| E01 | `Http404` e `PermissionDenied` do Django viram `api_error` | I | Mapear para `not_found` / `permission_denied` |
| E02 | `IntegrityError` e `ValidationError` do Django → 500 HTML | I | Mapear para 409 `conflict` / 400 `validation_error` |
| E03 | Erros aninhados (ListField/DictField) viram string de repr | I | Achatar recursivamente |
| E04 | Headers perdidos (`Retry-After`, `WWW-Authenticate`) | P | Copiar os headers |
| E05 | Rotas inexistentes e 500 → HTML | I | `handler404`/`handler500` JSON em `config/urls.py` para `/api/` |
| E06 | Sucessos ad-hoc `{"detail":...}` (logout, follow, leave) | P | Manter (não são erros); documentar |
| E07 | Mensagens em inglês | — | Manter; o frontend traduz por `code` (strings pt-BR num módulo) |

### 3.3 Settings e higiene
| # | Arquivo | Problema | Sev. | Correção |
|---|---|---|---|---|
| H01 | config/settings/__init__.py~ | Backup vazio versionado; falta `__init__.py` | I | `git mv` para `__init__.py`; adicionar `*~` ao `.gitignore` |
| H02 | base.py:15 | `DEBUG=True` na base | P | `False` na base (dev/test sobrescrevem) |
| H03 | prod.py | Sem `CSRF_TRUSTED_ORIGINS`, `SECURE_PROXY_SSL_HEADER`, HSTS e SSL redirect via env | P | Adicionar lendo do env (sem dependências novas) |
| H04 | `.env.example` | Sem documentação de prod | P | Comentários |
| H05 | Arquivos vazios (`*/permissions.py`, `core/selectors.py`...) e `communities/permissions.py` sem uso | P | Remover o código morto não usado (`IsNotSuspended`, `CommunityPermissionsSerializer`, permissões não usadas); manter os arquivos vazios do padrão em camadas |
| H06 | `StandardPagination` duplicado | P | Mover para `core/pagination.py` |
| H07 | Wallet `get_or_create` duplicado em 6 lugares | P | `economy.services.ensure_user_wallet` (refatoração justificada: corrige o `passive_earn_rate` faltando em customization) |

### 3.4 ⚠ Mudanças de model/migration (maior risco)
Nenhuma é estritamente necessária. Os candidatos:
- (a) índices para o `iexact` (desnecessário se usarmos `exact`, B25);
- (b) AuditLog append-only (feito no `save`/`delete`, sem migration).

**Proposta: zero migrations.**

### 3.5 Frontend
| # | Arquivo | Problema | Sev. | Correção |
|---|---|---|---|---|
| F01 | LoginView.tsx:40, RegisterView.tsx:63 | Token lido do caminho errado | **B** | `data.access` |
| F02 | idem catch | Formato de erro errado | **B** | `services/errors.ts` com `getErrorMessage(code)` em pt-BR e `fieldErrors` |
| F03 | LoginView.tsx:58 | Login demo com mock | I | Remover |
| F04 | services/api.ts | Token em localStorage; refresh concorrente (StrictMode e várias chamadas); falha não reseta a sessão | I | Token em memória no store, refresh single-flight, logout em caso de falha |
| F05 | App.tsx | Sem guarda, sem logout, sem perfil por username | **B** | Estado de view com `{view, username?, commname?}`; gate por sessão |
| F06 | Todas as views | Mocks | **B** | Trocar por `services/*.ts` por domínio |
| F07 | Header/Sidebar/Store | "+5/dia"; fallback 148/92 | P | Valores reais |
| F08 | Sino, "Esqueceu a senha?", compartilhar | Funções sem backend | P | Remover |
| F09 | CreateBubblegramBox.tsx, BrandIcon.tsx | Não usados | P | Excluir |
| F10 | `mockData.ts` | Deve sumir ao final | P | Excluir; mover o tipo `SuggestedUser` se ainda for necessário |
| F11 | Todas as views | Sem estados de loading, erro e vazio | I | Componentes simples `LoadingState`/`ErrorState`/`EmptyState` |
| F12 | Confetti em apoio e compra | PLAN.md §1.4 ("sem animações inúteis") | P | Q8 |
| F13 | Bundle de 504 kB | P | `React.lazy` por view (sem dependência nova) |

---

## 4. Ordem de execução em fases
Regra geral: ao final de cada fase rodam `make test`, `manage.py check`, `makemigrations --check`, `make lint` e `npm run build`, e `docs/PROGRESS.md` é atualizado. Toda correção de backend ganha um teste.

**Fase 0 — Registro.** Copiar o plano para `docs/REVIEW_PLAN.md`.
- Pronto quando: o arquivo existir.

**Fase 1 — Bloqueantes do backend** (B01–B06, B03, B04).
- Cada item com teste de regressão:
  - upload `images` rejeitado;
  - arquivo de 11 MB e `.svg` → 400;
  - banido não sai;
  - não membro não apoia;
  - login com Bearer expirado → 200;
  - throttle novo.
- Pronto quando: a suíte estiver verde e houver ~10 testes novos.

**Fase 2 — Regras importantes do backend** (B07–B20, B22, B23, B24, B28).
- Depende da Fase 1.
- Pronto quando: houver um teste por item e a suíte estiver verde.

**Fase 3 — Contrato e erros** (E01–E05, B26) + `core/pagination.py` (H06) + `ensure_user_wallet` (H07).
- Testes do exception handler (404, IntegrityError, erro aninhado, Retry-After, rota inexistente JSON).
- Pronto quando: todo erro da API vier no envelope.

**Fase 4 — Fundação do frontend** (F01–F05, F09).
- Itens:
  - `services/` por domínio (`auth`, `users`, `feed`, `content`, `communities`, `letters`, `customization`, `economy`, `search`) e `errors.ts`;
  - tipos corrigidos;
  - sessão (boot via refresh, logout, heartbeat a cada 5 min);
  - gate de rotas.
- Pronto quando: o build passar e for possível, manualmente, cadastrar → deslogar → logar → recarregar a página e continuar logado.

**Fase 5 — Integração tela a tela** (F06). Uma subfase por tela, cada uma removendo os seus mocks:
1. Header + Feed + bandeja + popup de criação + modal do post/comentários/apoio;
2. Perfil (próprio e de terceiros, seguir);
3. Comunidades (hub, criar, detalhe, entrar/sair, postar, diretrizes/foto conforme `permissions`);
4. Loja e inventário (equipar via `slots`);
5. Cartas.

- Depende da Fase 4.
- Pronto quando: a tela não importar mais `mockData` e o fluxo tiver sido testado manualmente contra o backend local.

**Fase 6 — Estados de loading, erro e vazio** (F11) e tratamento de `insufficient_soap` com custo e saldo.

**Fase 7 — Polimento visual** (F07, F08, F12, F13).
- Itens:
  - paleta e `rounded` conforme PLAN.md (só bolhas arredondadas);
  - conferir logo/ícones com `references/` (os SVGs de `public/` são idênticos aos de `references/`, já verificado).

**Fase 8 — Higiene** (H01–H05, B21, B25, B27, F10).
- Excluir `mockData.ts`.

**Fase 9 — Docs.**
- Itens:
  - ER.md (`Comment` 2000, mídia 1..4);
  - DECISIONS (novas decisões: limite de upload, throttle, alias `/equipped/`, comandos sem agendador);
  - PROGRESS (bloco "Review & integration");
  - frontend/PLAN.md ("+5/dia");
  - README (frontend: `npm install`, `make frontend-dev`).

---

## 5. Riscos e decisões que dependem de você
| # | Pergunta | Recomendação |
|---|---|---|
| Q1 | Instalar React Router e TanStack Query (previstos na skill), ou manter `useState` + zustand + axios? | **Manter o stack atual.** A restrição é "sem dependências desnecessárias"; a integração funciona sem eles. Sem URLs reais, o F5 volta ao feed. |
| Q2 | Access token em memória (DECISIONS) em vez de localStorage? | **Sim, em memória** + refresh no boot via cookie. |
| Q3 | Bubblepop: o backend existe, mas não há formulário (botão morto). Ligar o botão a um mini-formulário (imagem + horas + descrição)? | **Sim.** É integração de algo já previsto no PLAN.md §3, mas é uma UI nova pequena; preciso do seu ok. |
| Q4 | Abas do feed "seguindo/comunidades/popular" não existem na API | **Filtrar no cliente** "seguindo" e "comunidades"; **remover "popular"** (contradiz o feed cronológico). |
| Q5 | Sidebar "sugestões de usuários" sem endpoint | **Remover** o bloco (não criar endpoint). |
| Q6 | Pendências de requisito sem tela: editar perfil e excluir conta, extrato da carteira, moderação de membros/promover/transferir/arquivar, denúncias, admin | **Deixar fora** deste trabalho (é funcionalidade nova); registrar no PROGRESS como pendência. |
| Q7 | Compra de customização pela comunidade (S4) não existe e o backend aceita `customization_json` de graça | **Bloquear** o `customization_json` não vazio na comunidade agora; a compra fica como pendência. |
| Q8 | Confetti ao apoiar e comprar | **Remover** (PLAN.md §1.4). |
| Q9 | Valor do throttle `user` | **10000/day**. |
| Q10 | Commits | Um commit por fase (Conventional Commits) em uma branch `review/integration`; não faço push. |

**Riscos**
- A integração do frontend é a maior parte do esforço (≈5k linhas de views escritas sobre mocks). Algumas telas vão perder elementos que só existiam no mock.
- Não há testes de frontend (Vitest não está instalado). A validação será por build e teste manual.
- **Não verificado:** comportamento em produção real (não há deploy), `docker compose up` do zero (o container já estava de pé) e um migrate a partir de um banco vazio.

---

## 6. Estimativa de impacto (arquivos)

**Backend**
- `config/settings/{base,prod}.py`, `config/settings/__init__.py` (renomeado), `config/urls.py`
- `apps/core/{exceptions,uploads,pagination(novo)}.py`
- `apps/accounts/{views,services,serializers,backends,selectors}.py`
- `apps/communities/{services,selectors,views,permissions}.py`
- `apps/economy/{services,serializers}.py`
- `apps/content/{views,services,serializers,selectors}.py`
- `apps/social/{selectors,services,views}.py`
- `apps/customization/{services,views}.py`
- `apps/moderation/{services,serializers,views,admin}.py`
- testes em `apps/*/tests/`

**Frontend**
- `App.tsx`
- `components/Header.tsx`
- `services/api.ts` + novos `services/*.ts` e `errors.ts`
- `types/index.ts`
- `features/auth/*`
- todas as views em `features/{feed,profile,communities,customization,letters}/`
- novos `components/{LoadingState,ErrorState,EmptyState}.tsx`
- excluídos: `mockData.ts`, `CreateBubblegramBox.tsx`, `BrandIcon.tsx`

**Repo e docs**
- `.gitignore`, `.env.example`, `README.md`
- `docs/{ER,DECISIONS,PROGRESS,REQUIREMENTS_CHANGES}.md`, `docs/frontend/PLAN.md`, `docs/REVIEW_PLAN.md` (novo)

**Migrations:** nenhuma prevista.

## Verificação final
- `make test` verde, `make check-migrations` limpo, `make lint` ok, `npm run build` ok.
- `grep -r mockData frontend/src` vazio.
- Roteiro manual contra o backend local: cadastro (+20) → post (−10) → apoio entre dois usuários → comunidade (−300, com ajuste de soap via admin) → carta → compra/equipar.
