import { User, Community, Bubblegram, Bubblepop } from "@/types";

export const MOCK_USER: User = {
  id: 1,
  username: "marina_aqua",
  name: "Marina Santos",
  description: "Entusiasta de design de interfaces, fotografia aquática e computação dos anos 2000. Explorando novos formatos de interação para a web.",
  profile_photo: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=500&q=80",
  customization_json: {
    avatar_frame: {
      id: 1,
      code: "pink_sphere_glow",
      name: "Moldura Esférica Rosa",
      metadata: { border_color: "#F465AC", glow: "0 0 16px rgba(244, 101, 172, 0.45)" },
    },
    profile_theme: {
      id: 2,
      code: "bubbles_pink_clean",
      name: "Tema Rosa Bubbles",
      metadata: { primary: "#F465AC", secondary: "#7B63FF" },
    },
  },
  is_active: true,
  created_at: "2026-01-15T10:00:00Z",
  email: "marina@bubbles.social",
  birth_date: "2000-05-20",
  status: "ACTIVE",
  is_suspended: false,
  suspended_until: null,
  soap_balance: 78,
  wallet: {
    soap_balance: 78,
    passive_earn_rate: 5,
  },
  followers_count: 148,
  following_count: 92,
  is_following: false,
  is_followed_by: false,
};

export const MOCK_BUBBLEPOPS: Bubblepop[] = [
  {
    id: 101,
    user: MOCK_USER,
    image: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=400&q=80",
    description: "Reflexos de sol na superfície da água.",
    created_at: "2026-11-15T16:00:00Z",
    expires_at: "2026-11-15T22:00:00Z",
  },
  {
    id: 102,
    user: MOCK_USER,
    image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=400&q=80",
    description: "Registro da manhã na praia.",
    created_at: "2026-11-15T17:30:00Z",
    expires_at: "2026-11-16T01:30:00Z",
  },
  {
    id: 103,
    user: MOCK_USER,
    image: "https://images.unsplash.com/photo-1520038410233-7141be7e6f97?auto=format&fit=crop&w=400&q=80",
    description: "Exploração de renderização 3D de esferas.",
    created_at: "2026-11-15T18:15:00Z",
    expires_at: "2026-11-16T08:00:00Z",
  },
  {
    id: 104,
    user: MOCK_USER,
    image: "https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=400&q=80",
    description: "Estudo de layout com painéis clássicos.",
    created_at: "2026-11-15T19:00:00Z",
    expires_at: "2026-11-16T12:00:00Z",
  },
];

export const MOCK_BUBBLEGRAMS: (Bubblegram & { size: number; initialX: number; initialY: number })[] = [
  {
    id: 1,
    user: MOCK_USER,
    community: null,
    text: "Fotografia em alta velocidade de gotas de chuva formando micro-bolhas no lago. A tensão superficial cria esferas quase perfeitas.",
    type: "MEDIA",
    media: [
      { id: 1, media: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80", position: 0 },
      { id: 2, media: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80", position: 1 },
    ],
    soap_count: 34,
    published_at: "2026-11-13T14:20:00Z",
    size: 195,
    initialX: 25,
    initialY: 35,
  },
  {
    id: 2,
    user: MOCK_USER,
    community: null,
    text: "A clareza e estrutura dos sistemas operacionais dos anos 2000 continuam sendo uma das melhores referências de hierarquia visual.",
    type: "MEDIA",
    media: [
      { id: 3, media: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80", position: 0 },
    ],
    soap_count: 52,
    published_at: "2026-11-12T19:00:00Z",
    size: 215,
    initialX: 240,
    initialY: 15,
  },
  {
    id: 3,
    user: MOCK_USER,
    community: null,
    text: "Passeio de caiaque pelas águas de Bonito. A luz natural cria reflexos fascinantes na água.",
    type: "MEDIA",
    media: [
      { id: 4, media: "https://images.unsplash.com/photo-1498855926480-d98e83099315?auto=format&fit=crop&w=800&q=80", position: 0 },
    ],
    soap_count: 27,
    published_at: "2026-11-11T16:45:00Z",
    size: 185,
    initialX: 45,
    initialY: 250,
  },
  {
    id: 4,
    user: MOCK_USER,
    community: null,
    text: "Bolhas de sabão são estruturas com espessura de filme na escala de nanômetros que criam interferência óptica de luz.",
    type: "TEXT",
    media: [],
    soap_count: 19,
    published_at: "2026-11-10T11:15:00Z",
    size: 170,
    initialX: 260,
    initialY: 265,
  },
  {
    id: 5,
    user: MOCK_USER,
    community: null,
    text: "Novos tokens de design em andamento para a loja de personalizações. Em breve disponíveis.",
    type: "TEXT",
    media: [],
    soap_count: 41,
    published_at: "2026-11-09T08:30:00Z",
    size: 180,
    initialX: 440,
    initialY: 120,
  },
];

export const MOCK_FRIENDS = [
  { id: 2, username: "lucas_sky", name: "Lucas Melo", avatar: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=200&q=80" },
  { id: 3, username: "carol_ocean", name: "Carol Diniz", avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=200&q=80" },
  { id: 4, username: "diego_aero", name: "Diego Farias", avatar: "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?auto=format&fit=crop&w=200&q=80" },
  { id: 5, username: "bianca_soap", name: "Bianca Luz", avatar: "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=200&q=80" },
  { id: 6, username: "andre_aqua", name: "André Rocha", avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80" },
  { id: 7, username: "juliana_vibe", name: "Juliana Paz", avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=200&q=80" },
  { id: 8, username: "gabriel_tech", name: "Gabriel Vaz", avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80" },
  { id: 9, username: "larissa_glow", name: "Larissa Dias", avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=200&q=80" },
  { id: 10, username: "rodrigo_wave", name: "Rodrigo Sol", avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=200&q=80" },
];

export const MOCK_COMMUNITIES: Community[] = [
  {
    id: 1,
    commname: "frutigeraero",
    name: "Frutiger Aero Club",
    description: "Espaço dedicado à estética dos anos 2000, design de vidro e iluminação natural.",
    guidelines: "1. Mantenha o foco em estética Frutiger Aero, skeuomorfismo e design translúcido.\n2. Não publique anúncios comerciais ou conteúdo irrelevante.\n3. Seja cordial e respeite opiniões divergentes.\n4. Apoie publicações de qualidade com soap.",
    community_photo: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=200&q=80",
    banner_photo: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    customization_json: {},
    member_count: 2480,
    created_at: "2026-02-01T00:00:00Z",
    my_membership: {
      role: "MEMBER",
      current_state: "ACTIVE",
      joined_at: "2026-02-15T10:00:00Z",
    },
    permissions: {
      can_edit: false,
      can_edit_guidelines: false,
      can_manage_members: false,
      can_manage_admins: false,
      can_transfer_leadership: false,
      can_archive: false,
      can_view_wallet: false,
      can_join: false,
      can_leave: true,
    },
  },
  {
    id: 2,
    commname: "aquatica",
    name: "Fotografia Aquática",
    description: "Compartilhamento de fotos, reflexos e técnicas de registro sob a água.",
    guidelines: "1. Fotos subaquáticas e experimentos de refração de luz são bem-vindos.\n2. Inclua parâmetros técnicos quando possível (câmera, lente, abertura).\n3. Valorize o trabalho de outros fotógrafos enviando soap.",
    community_photo: "https://images.unsplash.com/photo-1498855926480-d98e83099315?auto=format&fit=crop&w=200&q=80",
    banner_photo: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80",
    customization_json: {},
    member_count: 1390,
    created_at: "2026-03-10T00:00:00Z",
    my_membership: {
      role: "COMM_ADMIN",
      current_state: "ACTIVE",
      joined_at: "2026-03-10T12:00:00Z",
    },
    permissions: {
      can_edit: true,
      can_edit_guidelines: true,
      can_manage_members: true,
      can_manage_admins: false,
      can_transfer_leadership: false,
      can_archive: false,
      can_view_wallet: true,
      can_join: false,
      can_leave: true,
    },
  },
  {
    id: 3,
    commname: "orkut2000",
    name: "Nostalgia Anos 2000",
    description: "Recordações da estrutura da web clássica, fóruns e comunidades.",
    guidelines: "1. Celebração de interfaces clássicas, MSN, Orkut e fóruns antigos.\n2. Sem toxicidade ou discussões políticas.",
    community_photo: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=200&q=80",
    banner_photo: null,
    customization_json: {},
    member_count: 5120,
    created_at: "2026-01-20T00:00:00Z",
    my_membership: null,
    permissions: {
      can_edit: false,
      can_edit_guidelines: false,
      can_manage_members: false,
      can_manage_admins: false,
      can_transfer_leadership: false,
      can_archive: false,
      can_view_wallet: false,
      can_join: true,
      can_leave: false,
    },
  },
  {
    id: 4,
    commname: "liquidglass",
    name: "Liquid Glass Designers",
    description: "Explorações de profundidade, translucidez e sombras internas no design digital.",
    guidelines: "1. Compartilhe estudos de caso de sombras internas, difusão e vidro líquido.\n2. Dê créditos a trabalhos derivados.",
    community_photo: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=200&q=80",
    banner_photo: null,
    customization_json: {},
    member_count: 870,
    created_at: "2026-04-05T00:00:00Z",
    my_membership: null,
    permissions: {
      can_edit: false,
      can_edit_guidelines: false,
      can_manage_members: false,
      can_manage_admins: false,
      can_transfer_leadership: false,
      can_archive: false,
      can_view_wallet: false,
      can_join: true,
      can_leave: false,
    },
  },
];

export interface MockLetter {
  id: number;
  sender: {
    id: number;
    username: string;
    name: string;
    avatar: string;
  };
  text: string;
  sent_at: string;
  read_at: string | null;
}

export const MOCK_LETTERS: MockLetter[] = [
  {
    id: 1,
    sender: {
      id: 3,
      username: "carol_ocean",
      name: "Carol Diniz",
      avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=200&q=80",
    },
    text: "Marina, apoiei sua publicação das micro-bolhas com 2 soap. A nitidez ficou excelente.",
    sent_at: "14:32",
    read_at: "14:40",
  },
  {
    id: 2,
    sender: {
      id: 2,
      username: "lucas_sky",
      name: "Lucas Melo",
      avatar: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=200&q=80",
    },
    text: "Olá! Vamos alinhar o novo layout da comunidade Frutiger Aero quando puder?",
    sent_at: "Ontem às 20:10",
    read_at: null,
  },
];

export const MOCK_CAROL: User = {
  id: 3,
  username: "carol_ocean",
  name: "Carol Diniz",
  description: "Fotógrafa aquática e bióloga marinha em formação. Registrando a vida e as cores sob a superfície.",
  profile_photo: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=200&q=80",
  customization_json: {},
  is_active: true,
  created_at: "2026-02-10T12:00:00Z",
  followers_count: 312,
  following_count: 145,
  soap_balance: 64,
  is_following: true,
};

export const MOCK_LUCAS: User = {
  id: 2,
  username: "lucas_sky",
  name: "Lucas Melo",
  description: "Arquiteto de software e nostálgico de sistemas operacionais clássicos.",
  profile_photo: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=200&q=80",
  customization_json: {},
  is_active: true,
  created_at: "2026-01-18T10:00:00Z",
  followers_count: 240,
  following_count: 88,
  soap_balance: 50,
  is_following: true,
};

export const MOCK_DIEGO: User = {
  id: 4,
  username: "diego_aero",
  name: "Diego Farias",
  description: "Artista 3D focado em aerodinâmica, vidro líquido e iluminação realista.",
  profile_photo: "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?auto=format&fit=crop&w=200&q=80",
  customization_json: {},
  is_active: true,
  created_at: "2026-03-01T15:00:00Z",
  followers_count: 420,
  following_count: 110,
  soap_balance: 112,
  is_following: true,
};

export const MOCK_BIANCA: User = {
  id: 5,
  username: "bianca_soap",
  name: "Bianca Luz",
  description: "Pesquisadora de física óptica e dinâmica de fluidos. Bolhas são laboratórios de luz.",
  profile_photo: "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=200&q=80",
  customization_json: {},
  is_active: true,
  created_at: "2026-02-28T09:00:00Z",
  followers_count: 580,
  following_count: 170,
  soap_balance: 185,
  is_following: false,
};

export const MOCK_GABRIEL: User = {
  id: 8,
  username: "gabriel_tech",
  name: "Gabriel Vaz",
  description: "Desenvolvedor de sistemas distribuídos e admirador do design de interfaces dos anos 2000.",
  profile_photo: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80",
  customization_json: {},
  is_active: true,
  created_at: "2026-03-12T11:00:00Z",
  followers_count: 165,
  following_count: 94,
  soap_balance: 38,
  is_following: false,
};

export const MOCK_FEED_BUBBLEPOPS: Bubblepop[] = [
  {
    id: 201,
    user: MOCK_USER,
    image: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=400&q=80",
    description: "Reflexos de sol na superfície da água.",
    created_at: "2026-11-15T16:00:00Z",
    expires_at: "2026-11-15T22:00:00Z",
  },
  {
    id: 202,
    user: MOCK_CAROL,
    image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=400&q=80",
    description: "Mergulho em águas cristalinas ao amanhecer.",
    created_at: "2026-11-15T17:30:00Z",
    expires_at: "2026-11-16T01:30:00Z",
  },
  {
    id: 203,
    user: MOCK_DIEGO,
    image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=80",
    description: "Estudo de refração em esferas vítreas.",
    created_at: "2026-11-15T18:15:00Z",
    expires_at: "2026-11-16T08:00:00Z",
  },
  {
    id: 204,
    user: MOCK_BIANCA,
    image: "https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=400&q=80",
    description: "Filme fino de sabão gerando arco-íris natural.",
    created_at: "2026-11-15T19:00:00Z",
    expires_at: "2026-11-16T12:00:00Z",
  },
  {
    id: 205,
    user: MOCK_LUCAS,
    image: "https://images.unsplash.com/photo-1520038410233-7141be7e6f97?auto=format&fit=crop&w=400&q=80",
    description: "Testando novas janelas com transparência Aero.",
    created_at: "2026-11-15T19:40:00Z",
    expires_at: "2026-11-16T14:00:00Z",
  },
];

export const MOCK_FEED_BUBBLEGRAMS: Bubblegram[] = [
  {
    id: 1001,
    user: MOCK_CAROL,
    community: null,
    text: "Ensaio fotográfico subaquático em Bonito. A luz natural ao meio-dia produz reflexos em formato de prisma na rocha calcária e destaca partículas em suspensão.",
    type: "MEDIA",
    media: [
      { id: 101, media: "https://images.unsplash.com/photo-1498855926480-d98e83099315?auto=format&fit=crop&w=800&q=80", position: 0 },
    ],
    soap_count: 42,
    published_at: "2026-11-15T18:30:00Z",
    is_suggested: false,
    suggestion_reason: null,
  },
  {
    id: 1002,
    user: MOCK_DIEGO,
    community: MOCK_COMMUNITIES[0], // Frutiger Aero Club
    text: "Nova textura de vidro com aberração cromática e reflexo especular concluída para os temas da comunidade Frutiger Aero. Renderizado com traçado de raios em tempo real.",
    type: "MEDIA",
    media: [
      { id: 102, media: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80", position: 0 },
    ],
    soap_count: 58,
    published_at: "2026-11-15T17:15:00Z",
    is_suggested: false,
    suggestion_reason: null,
  },
  {
    id: 1003,
    user: MOCK_BIANCA,
    community: null,
    text: "A espessura ideal de uma película de sabão para produzir interferência construtiva de luz visível varia entre 400nm e 700nm. Quanto mais fina a camada fica antes de estourar, mais escura ela se torna porque a luz refletida cancela a si mesma por oposição de fase.",
    type: "TEXT",
    media: [],
    soap_count: 94,
    published_at: "2026-11-15T15:00:00Z",
    is_suggested: true,
    suggestion_reason: "popular",
  },
  {
    id: 1004,
    user: MOCK_LUCAS,
    community: MOCK_COMMUNITIES[2], // Nostalgia Anos 2000
    text: "A hierarquia visual do Windows 7 e do Orkut clássico com painéis retos, densos e bem delimitados permitia encontrar qualquer informação em menos de dois cliques. Hoje em dia interfaces escondem tudo atrás de menus desnecessários.",
    type: "MEDIA",
    media: [
      { id: 103, media: "https://images.unsplash.com/photo-1520038410233-7141be7e6f97?auto=format&fit=crop&w=800&q=80", position: 0 },
    ],
    soap_count: 31,
    published_at: "2026-11-15T13:45:00Z",
    is_suggested: false,
    suggestion_reason: null,
  },
  {
    id: 1005,
    user: MOCK_GABRIEL,
    community: null,
    text: "Configurando meu novo ambiente com fontes Segoe UI e layout de 3 colunas. O contraste com tons neutros e toques suaves de rosa dá uma identidade única sem cansar a visão.",
    type: "TEXT",
    media: [],
    soap_count: 18,
    published_at: "2026-11-15T11:20:00Z",
    is_suggested: true,
    suggestion_reason: "network",
  },
  {
    id: 1006,
    user: MOCK_USER,
    community: null,
    text: "Fotografia em alta velocidade de gotas de chuva formando micro-bolhas no lago. A tensão superficial cria esferas quase perfeitas.",
    type: "MEDIA",
    media: [
      { id: 104, media: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80", position: 0 },
    ],
    soap_count: 34,
    published_at: "2026-11-14T14:20:00Z",
    is_suggested: false,
    suggestion_reason: null,
  },
];

export interface SuggestedUser {
  id: number;
  user: User;
  mutualInfo: string;
}

export const MOCK_SUGGESTED_USERS: SuggestedUser[] = [
  {
    id: 1,
    user: MOCK_BIANCA,
    mutualInfo: "Seguida por Carol Diniz e Lucas Melo",
  },
  {
    id: 2,
    user: MOCK_GABRIEL,
    mutualInfo: "Membro de Frutiger Aero Club",
  },
  {
    id: 3,
    user: {
      id: 9,
      username: "larissa_glow",
      name: "Larissa Dias",
      description: "Entusiasta de fotografia e interfaces translúcidas.",
      profile_photo: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=200&q=80",
      customization_json: {},
      is_active: true,
      created_at: "2026-03-20T10:00:00Z",
      followers_count: 98,
      following_count: 62,
      soap_balance: 24,
    },
    mutualInfo: "Seguida por Diego Farias",
  },
];

import { CommunityMemberItem } from "@/types";

export const MOCK_COMMUNITY_MEMBERS: Record<string, CommunityMemberItem[]> = {
  frutigeraero: [
    {
      id: 1,
      user: MOCK_DIEGO,
      role: "LEADER",
      current_state: "ACTIVE",
      joined_at: "2026-02-01T00:00:00Z",
    },
    {
      id: 2,
      user: MOCK_LUCAS,
      role: "COMM_ADMIN",
      current_state: "ACTIVE",
      joined_at: "2026-02-05T12:00:00Z",
    },
    {
      id: 3,
      user: MOCK_USER,
      role: "MEMBER",
      current_state: "ACTIVE",
      joined_at: "2026-02-15T10:00:00Z",
    },
    {
      id: 4,
      user: MOCK_BIANCA,
      role: "MEMBER",
      current_state: "ACTIVE",
      joined_at: "2026-02-20T14:30:00Z",
    },
    {
      id: 5,
      user: MOCK_GABRIEL,
      role: "MEMBER",
      current_state: "ACTIVE",
      joined_at: "2026-03-01T09:00:00Z",
    },
  ],
  aquatica: [
    {
      id: 6,
      user: MOCK_CAROL,
      role: "LEADER",
      current_state: "ACTIVE",
      joined_at: "2026-03-10T00:00:00Z",
    },
    {
      id: 7,
      user: MOCK_USER,
      role: "COMM_ADMIN",
      current_state: "ACTIVE",
      joined_at: "2026-03-10T12:00:00Z",
    },
    {
      id: 8,
      user: MOCK_DIEGO,
      role: "MEMBER",
      current_state: "ACTIVE",
      joined_at: "2026-03-15T16:00:00Z",
    },
  ],
  orkut2000: [
    {
      id: 9,
      user: MOCK_LUCAS,
      role: "LEADER",
      current_state: "ACTIVE",
      joined_at: "2026-01-20T00:00:00Z",
    },
    {
      id: 10,
      user: MOCK_GABRIEL,
      role: "COMM_ADMIN",
      current_state: "ACTIVE",
      joined_at: "2026-01-25T11:00:00Z",
    },
  ],
  liquidglass: [
    {
      id: 11,
      user: MOCK_DIEGO,
      role: "LEADER",
      current_state: "ACTIVE",
      joined_at: "2026-04-05T00:00:00Z",
    },
  ],
};

export const MOCK_COMMUNITY_POSTS: Record<string, Bubblegram[]> = {
  frutigeraero: [
    {
      id: 3001,
      user: MOCK_DIEGO,
      community: MOCK_COMMUNITIES[0],
      text: "Nova textura de vidro com aberração cromática e reflexo especular concluída para os temas da comunidade Frutiger Aero. Renderizado com traçado de raios em tempo real.",
      type: "MEDIA",
      media: [
        { id: 201, media: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80", position: 0 },
      ],
      soap_count: 58,
      published_at: "2026-11-15T17:15:00Z",
      is_suggested: false,
      suggestion_reason: null,
      can_delete: true,
    },
    {
      id: 3002,
      user: MOCK_BIANCA,
      community: MOCK_COMMUNITIES[0],
      text: "Fiz um comparativo de papéis de parede aquáticos do Windows 7 em alta resolução. O contraste entre água límpida e luz solar continua insuperável.",
      type: "MEDIA",
      media: [
        { id: 202, media: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80", position: 0 },
      ],
      soap_count: 45,
      published_at: "2026-11-14T20:00:00Z",
      is_suggested: false,
      suggestion_reason: null,
      can_delete: false,
    },
    {
      id: 3003,
      user: MOCK_GABRIEL,
      community: MOCK_COMMUNITIES[0],
      text: "Alguém já experimentou simular reflexo de bolhas usando SVG puro com gradientes radiais? Os resultados são surpreendentemente leves para o navegador.",
      type: "TEXT",
      media: [],
      soap_count: 22,
      published_at: "2026-11-13T15:30:00Z",
      is_suggested: false,
      suggestion_reason: null,
      can_delete: false,
    },
  ],
  aquatica: [
    {
      id: 3004,
      user: MOCK_CAROL,
      community: MOCK_COMMUNITIES[1],
      text: "Ensaio fotográfico subaquático em Bonito. A luz natural ao meio-dia produz reflexos em formato de prisma na rocha calcária e destaca partículas em suspensão.",
      type: "MEDIA",
      media: [
        { id: 203, media: "https://images.unsplash.com/photo-1498855926480-d98e83099315?auto=format&fit=crop&w=800&q=80", position: 0 },
      ],
      soap_count: 42,
      published_at: "2026-11-15T18:30:00Z",
      is_suggested: false,
      suggestion_reason: null,
      can_delete: false,
    },
  ],
  orkut2000: [
    {
      id: 3005,
      user: MOCK_LUCAS,
      community: MOCK_COMMUNITIES[2],
      text: "A hierarquia visual do Windows 7 e do Orkut clássico com painéis retos, densos e bem delimitados permitia encontrar qualquer informação em menos de dois cliques. Hoje em dia interfaces escondem tudo atrás de menus desnecessários.",
      type: "MEDIA",
      media: [
        { id: 204, media: "https://images.unsplash.com/photo-1520038410233-7141be7e6f97?auto=format&fit=crop&w=800&q=80", position: 0 },
      ],
      soap_count: 31,
      published_at: "2026-11-15T13:45:00Z",
      is_suggested: false,
      suggestion_reason: null,
      can_delete: false,
    },
  ],
  liquidglass: [
    {
      id: 3006,
      user: MOCK_DIEGO,
      community: MOCK_COMMUNITIES[3],
      text: "Estudos de difusão de luz com reflexos gaussianos em painéis de vidro. O segredo é manter as bordas internas com opacidade sutil de 15%.",
      type: "TEXT",
      media: [],
      soap_count: 19,
      published_at: "2026-11-14T11:00:00Z",
      is_suggested: false,
      suggestion_reason: null,
      can_delete: false,
    },
  ],
};
