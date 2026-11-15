   PASSO 1: O Plano de Ação — Arquitetura do Frontend 
  ──────
  ## 1. Configuração Inicial do Projeto & Stack Tecnológica
  
  O frontend será criado no diretório frontend/ na raiz do repositório, integrado com a API do Django já existente.
  
  • Build Tool & Framework: Vite com React 19 e TypeScript (compilação ultrarrápida, HMR instantâneo e tipagem segura compatível com o schema OpenAPI).
  • Estilização & Design System:                                                                                                                          
      • TailwindCSS + PostCSS + Autoprefixer: Base utilitária para layout flexível e responsivo.
      • Design Tokens Customizados no Tailwind: Configuração de utilitários específicos para estética Frutiger Aero / Liquid Glass (sombras volumétricas
      internas inner-shadow, reflexos especulares lineares, efeito arco-íris iridescente de bolha de sabão e vidros com backdrop-blur).                   
  • Interatividade & Física das Bolhas:
      • framer-motion: Mecânica fundamental para posts e stories em formato de bolhas que flutuam, colidem, reagem ao arrastar com física de mola (spring
      drag physics) e animações fluidas de abertura. 
      • canvas-confetti: Efeito visual festivo de gotas d'água / bolhas estourando ao expirar Bubblepops ou confirmar transações de sabão.
  • Ícones & UI Elements: 
      • lucide-react: Ícones de alta precisão que receberão acabamento tridimensional e gradientes luminosos.
  • Comunicação com a API & Estado Global:   
      • axios: Cliente HTTP com interceptors para gerenciamento de JWT (injeção de token Bearer, renovação transparente via /api/v1/auth/refresh/ e      
      captura do formato padrão de erro da API).
      • zustand: Gerenciamento leve do estado de autenticação, dados do usuário ativo, presença/heartbeat e carrinho/inventário de customização.
  • Estrutura de Diretórios (frontend/src/):
    frontend/src/
    ├── assets/          # Texturas de água, reflexos, molduras de bolhas e sons suaves 
    ├── components/      # UI atômica (GlassCard, GlossyButton, BubbleNode, AvatarRing, SoapBadge) 
    ├── features/        # Módulos de domínio conectados à API 
    │   ├── auth/        # Login, Cadastro com verificação de idade e Heartbeat 
    │   ├── feed/        # Feed cronológico, bandeja de Bubblepops e sugestões 
    │   ├── profile/     # Tela de Perfil Orkut-style, playground de Bubblegrams flutuantes
    │   ├── communities/ # Painel de comunidade, murais, membros e carteira coletiva
    │   ├── customization/# Loja de tokens de design, provador e inventário
    │   ├── letters/     # Mensageria de cartas encadeadas com visual de correspondência
    │   └── moderation/  # Modais de denúncia (Report) e ações de moderação
    ├── hooks/           # useAuth, useHeartbeat, useBubblePhysics, useThemeTokens
    ├── layouts/         # Shell de 3 colunas (Sidebar Esquerda, Palco Central, Painel Direito)
    ├── services/        # Cliente axios configurado com interceptors e endpoints da API
    ├── styles/          # index.css com utilitários de vidro líquido, gradientes e iridescência
    └── types/           # Interfaces TypeScript espelhando a API do backend 
  
  ──────
  ## 2. Mapa de Telas Divididas por Seções
  
  ### Seção 1: Autenticação & Entrada 
  
  1. Tela de Login: Janela vítrea flutuante sobre fundo aquático translúcido, campos com brilho interno para usuário/e-mail e senha, botão glossy com 
  reflexo de luz e link de recuperação. 
  2. Tela de Registro & Boas-Vindas: Formulário com validação de idade mínima (14 anos), escolha de username único (@ proibido), preview de avatar em    
  moldura esférica e modal festivo de boas-vindas destacando a bonificação inicial de +20 Sabões.
  
  ### Seção 2: Feed Social & Descoberta
  
  3. Feed Principal (Estritamente Cronológico): Linha do tempo central com publicações de amigos e comunidades seguidas, intercaladas com os blocos
  sinalizados de "Sugerido para você" (recomendações populares das últimas 24h e conexões de 2º grau). Ao final da lista, indicador visual amigável: "Você
  chegou ao fim por hoje!". 
  4. Bandeja de Bubblepops (Stories Tray): Faixa superior com esferas aquáticas flutuantes com borda ondulante e contador regressivo indicando a tensão 
  superficial antes da bolha estourar. 
  5. Modal Imersivo de Bubblepop: Visualizador de mídia com efeito de expansão esférica (zoom físico de mola) e botão de doação rápida de sabão.
  6. Descoberta & Busca Global: Dropdown dinâmico com visual glassmorphism exibindo resultados separados entre perfis e comunidades, com contadores de    
  membros e conexões mútuas.
  
  ### Seção 3: Comunidades (Estrutura Orkut 2.0)
  
  7. Hub de Comunidades: Catálogo de comunidades em que o usuário participa e destaques populares em blocos translúcidos com contadores de membros e selo 
  do fundador.
  8. Página da Comunidade:
      • Header Volumétrico: Banner com efeito de água, avatar esférico da comunidade e botões de ação ("Participar", "Sair", "Doar para a Carteira").
      • Mural de Bubblegrams: Publicações exclusivas de membros ativos com comentários encadeados (threaded replies).
      • Bloco Lateral de Diretrizes: Card vítreo fixo com as regras de convivência definidas pela liderança. 
      • Aba de Membros: Grid com categorização clara de cargos (Líder, Admin, Membro) e status (Ativo, Silenciado). 
      • Carteira Coletiva: Visualizador dos sabões arrecadados pela comunidade para personalizações coletivas.
  
  
  ### Seção 4: Perfil do Usuário (Foco do MVP — Passo 3)
  
  9. Tela de Perfil (Layout Orkut Revisitado):
      • Coluna Esquerda (Identidade): Avatar com a moldura cosmética equipada, indicador de presença em tempo real (Ativo agora / Visto há 5 min),    
      biografia, saldo de sabão pessoal e botões de interação direta ("Seguir", "Enviar Carta", "Apoiar com Sabão").
      • Coluna Central (Conteúdo & Bolhas Interativas):   
          • Playground de Bubblegrams (Posts Fixos): Em vez de grade quadrada monótona, os posts são esferas translúcidas interativas que o usuário pode
          arrastar, soltar, colidir e explorar com física elástica via framer-motion. Ao clicar em uma bolha, ela se expande suavemente revelando imagens,
          texto e comentários.
          • Carrossel de Bubblepops (Posts Efêmeros): Bolhas menores com pulsação aquática e indicador de horas restantes antes de estourarem.
      • Coluna Direita (Conexões & Blocos Clássicos):
          • Bloco de Amigos/Seguidores (Grid 3x3 de avatares com contador total e link "Ver todos"). 
          • Bloco de Comunidades que participa.
          • Bloco de Cartas/Recados recentes recebidos. 
  
  
  
  ### Seção 5: Loja de Sabão & Inventário (Customização)
  
  10. Catálogo de Cosméticos: Vitrine modular com cartões tridimensionais divididos por tipos: Molduras de Avatar (AVATAR_FRAME), Temas de Perfil       
  (PROFILE_THEME), Estilos de Bolha (CHAT_BUBBLE), Emblemas (BADGE) e Cores de Nome (NAME_COLOR). 
  11. Provador em Tempo Real (Live Preview): Simulador visual que aplica os tokens de design instantaneamente no perfil do usuário antes de efetuar a     
  compra com sabão. 
  12. Inventário do Usuário: Painel com todos os itens possuídos e botões de "Equipar" e "Desequipar" que salvam o estado ativo em customization_json.
  13. Extrato da Carteira: Tabela transparente com o histórico auditável de sabões (ganhos passivos periódicos de +5, apoios recebidos/enviados e gastos 
  em customização).
  
  ### Seção 6: Mensageria (Cartas) & Moderação
  
  14. Caixa de Cartas (Letters Inbox): Interface inspirada em papel de carta translúcido e selos postais, com separação de Recebidas e Enviadas e threads
  encadeadas (reply_to).
  15. Central de Moderação & Denúncias: Modal acessível para qualquer usuário denunciar posts/perfis e painel administrativo para staff gerenciar     
  denúncias e aplicar suspensões com auditoria.
  ──────
  ## 3. Estrutura Base de Layouts (Shell Orkut Modernizado)
  
  O layout geral do Bubbles seguirá uma grade balanceada de 3 colunas (Three-Column Grid), com cabeçalho translúcido superior:
  
    ┌──────────────────────────────────────────────────────────────────────────────────┐ 
    │  [Logo 3D Bubbles]      [ Barra de Busca Vítrea ]      (52 Sabões)  [Avatar Ring]│ 
    ├───────────────────┬──────────────────────────────────┬───────────────────────────┤ 
    │                   │                                  │                           │ 
    │  COLUNA ESQUERDA  │         PALCO CENTRAL            │      COLUNA DIREITA       │
    │  (Identidade)     │     (Feed / Playground)          │      (Social & Blocos)    │
    │                   │                                  │                           │
    │  - Foto de Perfil │  - Bandeja de Bubblepops         │  - Bloco de Amigos (3x3)  │
    │  - Nome & Status  │  - Área de Criação de Post       │  - Bloco de Comunidades   │ 
    │  - Saldo de Sabão │  - Stream / Bolhas Arrastáveis   │  - Bloco de Cartas        │
    │  - Menu Rápido    │    (Física Interativa)           │  - Atividades Recentes    │
    │                   │                                  │                           │
    └───────────────────┴──────────────────────────────────┴───────────────────────────┘ 
  
  1. Header Flutuante ("Liquid Glass Bar"): 
      • Fundo translúcido com forte desfoque (bg-white/45 backdrop-blur-xl border-b border-white/60).
      • Sombra interna sutil na borda superior (inset 0 1px 1px rgba(255, 255, 255, 0.9)). 
      • Logotipo do Bubbles com esferas aquáticas brilhantes. 
      • Pílula de Sabão interativa: exibe o saldo com brilho iridescente e animação de bolha ao receber novos sabões passivos. 
      • Heartbeat silencioso integrado em segundo plano mantendo o last_seen_at atualizado.
  2. Left Rail (~260px - Painel de Navegação & Identidade):
      • Bloco vítreo com foto do usuário, status de presença e atalhos com ícones volumétricos (Início, Comunidades, Cartas, Loja de Sabão, Meu Perfil). 
  3. Center Stage (~680px - Fluxo Principal): 
      • Espaço amplo dedicado ao consumo de conteúdo, seja o feed de notícias ou o playground de bolhas flutuantes interativas no perfil.
  4. Right Rail (~300px - Blocos Sociais Estilo Orkut): 
      • Caixas modulares translúcidas com cantos super-arredondados (rounded-3xl), sombra profunda suave e cabeçalho com reflexo glossy.
  
  ──────
  ## 4. Paleta de Cores Tailwind & Design Tokens (Frutiger Aero & Liquid Glass)
  
  As cores foram desenhadas para reproduzir a luz, a água, a transparência e o otimismo visual dos anos 2000, com refinamento moderno da Apple: 
  
  ### A. Paleta de Cores Primárias (Água, Céu & Sabão) 
  
  • Cyan Aqua (Água Cristalina): 
      • bubble-cyan-50: #E6FAFC (fundo suave de cards)
      • bubble-cyan-100: #B8F2F8 (vidro translúcido com reflexo) 
      • bubble-cyan-300: #4EE2F2 (destaques, bordas luminosas)
      • bubble-cyan-500: #08C4DB (botões primários volumétricos)
      • bubble-cyan-700: #057A8A (textos de alto contraste) 
  • Seafoam Teal (Verde Mar):
      • water-teal-50: #E8F8F5 
      • water-teal-300: #64D2B8 
      • water-teal-500: #1EB995 (indicador de online e comunidade ativa)
  • Soap Pink (Iridescência de Bolha): 
      • soap-pink-50: #FDF0F5
      • soap-pink-200: #F9B7D3 (reflexo rosado na casca da bolha)
      • soap-pink-400: #EE5B9B (botões de apoiar com sabão e notificações)
      • soap-pink-600: #B52264 
  • Pure White & Opacidades Vítreas:   
      • glass-base: rgba(255, 255, 255, 0.40)
      • glass-highlight: rgba(255, 255, 255, 0.75) 
      • glass-border: rgba(255, 255, 255, 0.65)
      • glass-shadow: rgba(8, 196, 219, 0.12)
  
  
  ### B. Classes e Efeitos Utilitários Especiais 
  
  • glass-card:
      • background: rgba(255, 255, 255, 0.45);
      • backdrop-filter: blur(16px) saturate(180%);
      • border: 1px solid rgba(255, 255, 255, 0.7); 
      • box-shadow: 0 10px 30px -10px rgba(8, 196, 219, 0.15), inset 0 1px 2px rgba(255, 255, 255, 0.9);
  • glossy-bubble:
      • Esfera com gradiente radial que simula volume 3D: ponto de luz branco no topo superior esquerdo (inset 4px 6px 12px rgba(255, 255, 255, 0.85)),   
      centro translúcido e borda inferior com dispersão de luz ciano/rosa.
  • liquid-button:
      • Botão volumétrico estilo pílula com brilho superior permanente, sombra suave de elevação e animação elástica ao clique (scale: 0.96).
  
  ──────
  Este plano de ação está aprovado para darmos início ao PASSO 2 (Configuração Inicial) e ao PASSO 3 (MVP da Tela de Perfil com bolhas interativas)