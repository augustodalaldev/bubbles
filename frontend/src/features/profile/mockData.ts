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
    community_photo: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=200&q=80",
    banner_photo: null,
    customization_json: {},
    member_count: 2480,
    created_at: "2026-02-01T00:00:00Z",
  },
  {
    id: 2,
    commname: "aquatica",
    name: "Fotografia Aquática",
    description: "Compartilhamento de fotos, reflexos e técnicas de registro sob a água.",
    community_photo: "https://images.unsplash.com/photo-1498855926480-d98e83099315?auto=format&fit=crop&w=200&q=80",
    banner_photo: null,
    customization_json: {},
    member_count: 1390,
    created_at: "2026-03-10T00:00:00Z",
  },
  {
    id: 3,
    commname: "orkut2000",
    name: "Nostalgia Anos 2000",
    description: "Recordações da estrutura da web clássica, fóruns e comunidades.",
    community_photo: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=200&q=80",
    banner_photo: null,
    customization_json: {},
    member_count: 5120,
    created_at: "2026-01-20T00:00:00Z",
  },
  {
    id: 4,
    commname: "liquidglass",
    name: "Liquid Glass Designers",
    description: "Explorações de profundidade, translucidez e sombras internas no design digital.",
    community_photo: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=200&q=80",
    banner_photo: null,
    customization_json: {},
    member_count: 870,
    created_at: "2026-04-05T00:00:00Z",
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
