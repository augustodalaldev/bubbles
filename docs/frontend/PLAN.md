# Plano de Arquitetura e Design do Frontend — Bubbles

## 1. Identidade Visual & Princípios de Design (Anti-AI Slop)

Este documento redefine as diretrizes estéticas e a arquitetura do frontend do Bubbles, substituindo clichês genéricos e efeitos sobrecarregados por um design intencional, funcional e fundamentado na web do início dos anos 2000 (Orkut + Windows Aero / Segoe UI), alinhado com a paleta oficial da marca.

### Princípios Chave de Design

1. **Estrutura Reta e Firme (Estilo Clássico 2000s / Orkut):**
   - Os painéis, caixas e cartões da interface possuem cantos retos ou sutilmente chanfrados (bordas de 0 a 4px, sem o visual arredondado de "pílula SaaS" em todo lugar).
   - Cabeçalhos de blocos bem delimitados com linha divisória sutil, garantindo alta densidade de informação e leitura limpa.
   - **Bordas arredondadas e volumétricas são reservadas exclusivamente para elementos que de fato representam bolhas** (avatares esféricos, posts Bubblegrams no mural, stories Bubblepops e o token de soap).

2. **Tipografia Segoe UI:**
   - Família tipográfica: `"Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif`.
   - Hierarquia clássica e sóbria: sem textos em caixa-alta desnecessários (*all-caps eyebrow labels*), sem palavras isoladas em itálico colorido e sem enfeites tipográficos artificiais. Textos objetivos em sentence-case.

3. **Zero Emojis — Apenas Ícones Profissionais:**
   - Emojis (`🫧`, `🧼`, `⭐️`, `🧊`, etc.) foram banidos da UI.
   - Todas as ações e metáforas utilizam ícones vetoriais SVG limpos e padronizados (Lucide e SVGs proprietários da marca).
   - A marca Bubbles utiliza os arquivos vetoriais oficiais de `@references/icon.svg` e `@references/logo.svg`.
   - A moeda de troca **soap** possui um glifo/ícone vetorial proprietário marcante.

4. **Performance, Calmaria Visual e Fim de Animações Inúteis:**
   - Remoção de elementos piscantes (*animate-ping*), anéis pulsantes contínuos nos stories e partículas de fundo que sobrecarregavam a renderização.
   - Movimento restrito a ações intencionais do usuário: a física de arraste dos Bubblegrams (`framer-motion`), abertura de modais e transições de abas.

5. **Compatibilidade Rigorosa com a API (100% Fiel ao Backend):**
   - Eliminação de dados fictícios sem respaldo no modelo de dados (como medidores de "Confiável/Legal/Sexy" e "Cidade").
   - Apenas campos reais dos modelos Django:
     - `User`: `username`, `name`, `birth_date`, `description`, `profile_photo`, `customization_json`, `created_at`, `status`, `followers_count`, `following_count`.
     - `Letter`: Correspondência privada e direta entre dois usuários (`sender`, `recipient`, `text`, `image`, `sent_at`, `read_at`).
     - `Bubblegram`: Publicação perene (`user`, `community`, `text`, `type`, `media`, `soap_count`, `published_at`, `comments`).
     - `Bubblepop`: Mídia efêmera (`user`, `image`, `description`, `created_at`, `expires_at`).
     - `Soap / Carteira`: Saldo do usuário e geração passiva (valores vindos de `GET /economy/settings/`: +5 soap a cada 5 min de uso, até 15 por dia).

6. **Mecânica de Engajamento Exclusiva por Soap:**
   - No Bubbles não existem "curtidas" nem "corações". A única forma de apoiar criadores e interagir com publicações é através do envio de **soap** (`BubblegramSupport`).

---

## 2. Paleta de Cores e Tokens Oficiais

A paleta é baseada nos arquivos vetoriais de `@references/` com ênfase no **branco** e no **rosa**:

| Token | Hex | Função e Aplicação |
|---|---|---|
| **White Base** | `#FFFFFF` | Fundo principal de cartões e painéis retos, transparências vítreas leves. |
| **Pink Primary** | `#F465AC` | Cor de destaque primária da marca Bubbles, botões principais de ação, badges ativas. |
| **Purple Accent** | `#7B63FF` | Profundidade, botões secundários, anéis de foco e elementos de contraste. |
| **Lime Green Accent** | `#4BF521` | Destaques pontuais, indicador de status ativo/online e indicadores positivos. |
| **Surface Gray** | `#F8FAFC` / `#F1F5F9` | Fundo geral da página e trilhas estruturais neutras. |
| **Slate Text** | `#0F172A` / `#334155` | Tipografia de alto contraste e máxima legibilidade. |
| **Borders** | `#E2E8F0` / `#CBD5E1` | Linhas de divisão retas e contornos estruturais sutis. |

*Nota: Tons de ciano saturados foram removidos.*

---

## 3. Estrutura de Telas e Módulos do Sistema

### Seção 1: Autenticação & Entrada
1. **Login:** Painel reto translúcido centralizado, inputs limpos com borda fina, botão primário em rosa `#F465AC` e recuperação de conta.
2. **Cadastro:** Formulário estruturado com validação de idade mínima (14 anos exigidos pelo backend), criação de usuário e aviso do bônus inicial de +20 soap.

### Seção 2: Feed Principal & Descoberta
3. **Feed Cronológico:** Linha do tempo central com postagens de seguidos e comunidades, com injeção intercalada de sugestões populares (posts com mais soap das últimas 24h e seguidos de seguidos) com limite fixo e indicação de fim de feed.
4. **Bandeja de Bubblepops:** Faixa horizontal com bolhas compactas, sem pulsação contínua, indicando o tempo restante de forma discreta.
5. **Busca:** Campo de busca direto para perfis e comunidades.

### Seção 3: Comunidades (Orkut 2.0)
6. **Hub de Comunidades:** Lista de comunidades com contagem de membros e avatar esférico.
7. **Página de Comunidade:** Painel reto com cabeçalho, diretrizes, lista de membros categorizados por cargo e mural de Bubblegrams exclusivo.

### Seção 4: Perfil do Usuário (MVP Validado)
8. **Layout de 3 Colunas Orkut Revisitado:**
   - **Coluna Esquerda:** Avatar esférico do usuário com moldura cosmética, nome, `@username`, data de nascimento, data de entrada, biografia, saldo de soap (e ganho passivo conforme as configurações) e botões de ação ("Seguir" e "Enviar carta").
   - **Coluna Central:**
     - Bandeja compacta de Bubblepops com menor espaçamento.
     - Mural de Bolhas (Bubblegrams) interativo com física elástica via `framer-motion`, bolhas maiores e mais expressivas (~160px a 210px), e alternador para modo Grade.
   - **Coluna Direita:**
     - Bloco de Amigos (grid 3x3 com contador real e link "Ver todos").
     - Bloco de Comunidades (lista com contadores).
     - Seção de Cartas (correspondências diretas recentes e botão para redigir nova carta).

### Seção 5: Loja de Customizações & Inventário
9. **Loja de Itens:** Catálogo de itens adquiríveis com soap (molduras de avatar, temas de perfil, estilos de bolha).
10. **Inventário do Usuário:** Painel de itens possuídos com ação de equipar/desequipar que atualiza o `customization_json`.

### Seção 6: Mensageria Direta (Cartas)
11. **Caixa Postal de Cartas:** Conversas privadas entre usuários, com threads encadeadas (`reply_to`), suporte a anexo de imagem e marcação de lida (`read_at`).

---

## 4. Especificações do Modal de Detalhes da Bolha

- **Visual:** Janela limpa, fundo escurecido estático com desfoque moderado.
- **Engajamento Único:** Botão **"Apoiar com 1 soap"** com exibição do contador atualizado. Remoção total de ícones de coração/curtidas.
- **Comentários:** Lista encadeada de comentários com suporte a réplica e entrada de texto direta.

---

## 5. Próximos Passos de Execução
1. Atualização dos tokens de cor, tipografia e estilos globais em `tailwind.config.js` e `index.css`.
2. Criação dos componentes de ícone vetorial (`BrandLogo.tsx`, `SoapIcon.tsx`).
3. Refatoração dos componentes da Tela de Perfil (`Header.tsx`, `ProfileView.tsx`, `BubblegramBall.tsx`, `BubblepopStory.tsx`, `PostDetailModal.tsx`).
4. Verificação de build com TypeScript e validação visual no navegador.

---

## 6. Decisões Arquiteturais e Políticas do Sistema (Persistidas)

1. **Upload de Mídia de Alta Resolução (Até 10 MB por arquivo):**
   - O limite de **10 MB** por imagem (JPEG, PNG, WebP, GIF) é imposto pelo backend em `core.uploads.validate_image_upload` (`SafeImageField`); o frontend apenas antecipa a checagem. As configurações `DATA_UPLOAD_MAX_MEMORY_SIZE`/`FILE_UPLOAD_MAX_MEMORY_SIZE` não limitam tamanho, só o uso de memória.

2. **Criação de Publicações (Popup no Canto Inferior Direito):**
   - A criação de publicações no feed geral foi desacoplada da linha do tempo e acionada por um botão flutuante com símbolo de `+` fixado no canto inferior direito.
   - Publicações originadas desse popup são sempre destinadas ao mural pessoal do usuário (com o custo `bubblegram_profile_cost`, 10 soap por padrão). Publicar em comunidade também custa soap (`bubblegram_community_cost`).
   - **Publicações em comunidades são estritamente proibidas no popup geral:** postagens em comunidades só podem ser feitas de dentro da página da respectiva comunidade por membros autorizados.

3. **Arquitetura de Rolagem da Interface:**
   - Apenas a raia central (feed de publicações) possui barra de rolagem interna (`overflow-y-auto`), mantendo o cabeçalho e as barras laterais (perfil à esquerda, comunidades e recomendações à direita) visíveis e acompanhando o scroll sem deslocamentos desnecessários.

---

## 7. Estado da integração (2026-11-17)

Todas as telas acima consomem a API real (`frontend/src/services/*`), com estados de carregamento, erro e vazio.
Não há mais dados mockados. Pendências que **não** têm tela (existem no backend; decisão do produto): editar perfil e excluir conta,
extrato da carteira, moderação de membros/promover/transferir liderança/arquivar comunidade, denúncias e administração
(use o Django Admin), compra de customização pela carteira da comunidade (S4).

