"""Portuguese demo content: pet communities, captions, comments, letters and the item catalog."""

# species: which photos fit the community ("cat", "dog" or "both")
COMMUNITY_THEMES = [
    {
        "commname": "gatos_de_apartamento",
        "name": "Gatos de apartamento",
        "species": "cat",
        "description": "Dicas, fotos e histórias de quem divide o apartamento com um (ou vários) gatos.",
        "guidelines": "Respeite todos os tutores. Nada de compra e venda de animais. Fotos engraçadas são bem-vindas.",
    },
    {
        "commname": "caes_de_grande_porte",
        "name": "Cães de grande porte",
        "species": "dog",
        "description": "Labradores, pastores, São Bernardos e todos os gigantes de coração mole.",
        "guidelines": "Compartilhe rotina de passeios e cuidados. Sem agressividade contra outros tutores.",
    },
    {
        "commname": "adocao_responsavel",
        "name": "Adoção responsável",
        "species": "both",
        "description": "Divulgação de animais para adoção e orientação para quem está começando.",
        "guidelines": "Informe sempre cidade, idade e castração. Adoção exige termo de responsabilidade.",
    },
    {
        "commname": "fotos_engracadas",
        "name": "Fotos engraçadas de pets",
        "species": "both",
        "description": "O espaço das caretas, dos tombos e dos pets que não entendem espelhos.",
        "guidelines": "Humor sim, maus-tratos nunca. Marque o pet, não o tutor.",
    },
    {
        "commname": "filhotes_fofos",
        "name": "Filhotes fofos",
        "species": "both",
        "description": "Só filhotes, só fofura, só alegria.",
        "guidelines": "Informe a idade do filhote. Evite postar filhotes menores de 8 semanas longe da mãe.",
    },
    {
        "commname": "pets_da_melhor_idade",
        "name": "Pets da melhor idade",
        "species": "both",
        "description": "Cuidados, carinho e qualidade de vida para cães e gatos idosos.",
        "guidelines": "Compartilhe experiências com saúde e conforto. Consulte sempre um veterinário.",
    },
    {
        "commname": "passeios_e_trilhas",
        "name": "Passeios e trilhas com cães",
        "species": "dog",
        "description": "Parques, trilhas e lugares pet friendly para explorar com o seu melhor amigo.",
        "guidelines": "Indique se o local aceita cães sem guia. Recolha sempre o cocô.",
    },
    {
        "commname": "veterinario_responde",
        "name": "Veterinário responde",
        "species": "both",
        "description": "Dúvidas do dia a dia sobre alimentação, vacinas e comportamento.",
        "guidelines": "As respostas não substituem uma consulta. Em emergência, procure uma clínica.",
    },
]

BIOS = [
    "Tutora de dois gatos e uma planta que ainda sobrevive.",
    "Cachorro é a melhor parte do meu dia.",
    "Resgatei três vira-latas e nunca mais fui o mesmo.",
    "Fotógrafo amador de pets alheios.",
    "Mãe de pet em tempo integral.",
    "Trilhas, café e um labrador impossível.",
    "Voluntária em feiras de adoção aos sábados.",
    "Meu gato acha que eu moro na casa dele.",
    "Aprendendo a respeitar a hora da ração.",
    "Doguinho, gatinho e muita roupa peluda.",
]

CAPTIONS = [
    "Acordei e ele já estava me encarando. Hora da ração, aparentemente.",
    "Hoje o passeio foi de quase duas horas e ela ainda quer mais.",
    "Descobri que a caixa de papelão é melhor que a cama nova de R$ 200.",
    "Primeira vez no veterinário depois da adoção. Foi um campeão!",
    "Quem mais tem um pet que só dorme em cima do teclado?",
    "Este aqui acha que o sofá é dele. E é.",
    "Domingo de sol, parque e muita água.",
    "Meu gato resolveu aprender a abrir a porta do armário.",
    "Um ano de adoção! Obrigado por escolher a gente.",
    "Ele ouviu a palavra 'passeio' de outro cômodo e já estava na porta.",
    "Cochilo da tarde, versão peluda.",
    "Treino de sentar finalmente funcionando (com muito petisco).",
    "Quem consegue resistir a essa carinha?",
    "A janela virou a TV oficial da casa.",
    "Banho tomado e a cara de quem foi traído.",
    "Meu cão acha que toda poça d'água é um convite.",
    "Chegou a hora do soninho, mas o brinquedo continua na boca.",
    "Novo membro da família! Ainda está tímido, mas já ganhou o coração de todos.",
    "Dica: brinquedo com petisco escondido distrai por horas.",
    "A vizinhança toda já conhece esse passeador de gravatinha.",
    "Quem tem gato sabe: nenhum objeto na mesa está seguro.",
    "Trilha de domingo concluída, patas cansadas e coração cheio.",
    "Ele não gosta de chuva, mas adora a poça depois dela.",
    "Mais um resgatado a caminho de um lar. Compartilhem!",
    "Pet idoso, mas com energia de filhote quando ouve o saquinho de petisco.",
    "Foto do dia: bigodes em primeiro plano.",
    "Aprendeu a dar a pata. Agora só dá quando quer.",
    "Fim de tarde na varanda com o meu parceiro de quatro patas.",
    "Hoje tem festa de aniversário com direito a bolo de ração.",
    "Adotar mudou a minha rotina e a minha vida.",
    "Ela fez uma amizade improvável com o gato da vizinha.",
    "Cuidado: este rosto pede petisco e consegue.",
    "Primeiro banho de mangueira do verão aprovado.",
    "Quem mais tem um pet que come grama e depois se arrepende?",
    "Pista de corrida improvisada na sala às 3 da manhã.",
    "Missão cumprida: unhas aparadas sem drama!",
    "Não é bagunça, é a casa dele.",
    "Mais uma tarde de sol, mais um soneca no tapete.",
    "Pelo bonito é pelo escovado: rotina de domingo.",
    "Voltei do trabalho e fui recebido como se tivesse voltado da guerra.",
]

COMMENTS = [
    "Que lindo! Quantos anos tem?",
    "Fiquei apaixonada, parabéns pela adoção!",
    "O meu faz exatamente a mesma coisa.",
    "Hahaha a cara dele é tudo.",
    "Que dica boa, vou testar aqui em casa.",
    "Que olhar! Ganhou meu dia.",
    "Parabéns pelo carinho com ele.",
    "Os meus também são assim, impossível resistir.",
    "Qual é a raça? Está lindo demais!",
    "Obrigada por compartilhar, precisava disso hoje.",
    "Um abraço nesse peludo!",
    "Que energia boa, adorei a foto.",
    "Também tenho um desses aqui, é uma sina.",
    "Vou levar o meu nesse parque no fim de semana.",
    "Tão fofo que dá vontade de apertar!",
    "Concordo totalmente, adotar é a melhor decisão.",
    "Pode contar comigo para ajudar na divulgação.",
    "Que sorte a dele de ter você.",
    "Ri demais com essa legenda.",
    "Beijo na patinha!",
]

REPLIES = [
    "Obrigado! Ele tem 3 anos.",
    "Valeu! Pode testar, funcionou muito aqui.",
    "É vira-lata caramelo, a melhor raça do mundo.",
    "Pode ir, eles adoram esse lugar.",
    "Hahaha, nem me fale!",
    "Muito obrigada pelo carinho!",
]

LETTERS = [
    "Oi! Vi suas fotos e queria saber onde você comprou aquela caminha. Meu gato adoraria uma igual.",
    "Olá, tudo bem? Estou organizando um passeio com os cães do bairro no sábado. Topa participar?",
    "Muito obrigado pela dica sobre a ração. Funcionou perfeitamente!",
    "Pensei em você porque tem um filhote que precisa de lar. Posso te passar mais informações?",
    "Adorei o seu último post. Quer trocar dicas de adestramento?",
    "Queria agradecer por toda a ajuda com a adoção. Ele já está adaptado e muito feliz.",
    "Você conhece algum veterinário de confiança na região? O meu mudou de cidade.",
    "Que tal marcarmos um encontro dos pets no parque no domingo de manhã?",
]

LETTER_REPLIES = [
    "Claro! Mando o link da loja por aqui.",
    "Topo sim! Me avisa o horário.",
    "Fico feliz que tenha dado certo!",
    "Pode me passar sim, vou ver com a família.",
    "Combinado, nos vemos lá!",
]

REPORT_NOTES = [
    "Publicação parece divulgar venda de animais.",
    "Comentário com linguagem ofensiva.",
    "Conteúdo repetido em várias comunidades.",
    "Perfil usa fotos de outra pessoa.",
]

BUBBLEPOP_NOTES = [
    "Passeio de hoje",
    "Olha o que ele aprontou",
    "Hora do banho",
    "Cochilando no sol",
    "Novo brinquedo aprovado",
]

# Customization catalog. `scope` decides who can buy: USER, COMMUNITY or BOTH.
CATALOG = [
    ("frame_rosa", "Moldura rosa", "AVATAR_FRAME", "BOTH", 20, {"border_color": "#F465AC"}),
    (
        "frame_roxa",
        "Moldura roxa com brilho",
        "AVATAR_FRAME",
        "BOTH",
        40,
        {"border_color": "#7B63FF", "glow": "0 0 12px #7B63FF"},
    ),
    (
        "frame_dourada",
        "Moldura dourada",
        "AVATAR_FRAME",
        "BOTH",
        70,
        {"border_color": "#F5B301", "glow": "0 0 14px #F5B301"},
    ),
    ("frame_verde", "Moldura verde-limão", "AVATAR_FRAME", "USER", 25, {"border_color": "#4BF521"}),
    (
        "tema_algodao",
        "Tema algodão-doce",
        "PROFILE_THEME",
        "BOTH",
        50,
        {"primary": "#F465AC", "secondary": "#7B63FF"},
    ),
    (
        "tema_oceano",
        "Tema oceano",
        "PROFILE_THEME",
        "BOTH",
        60,
        {"primary": "#38BDF8", "secondary": "#7B63FF"},
    ),
    (
        "tema_pomar",
        "Tema pomar",
        "PROFILE_THEME",
        "COMMUNITY",
        55,
        {"primary": "#4BF521", "secondary": "#F5B301"},
    ),
    ("balao_pata", "Balão com patinha", "CHAT_BUBBLE", "USER", 30, {"tint": "#FCE7F3"}),
    ("balao_nuvem", "Balão nuvem", "CHAT_BUBBLE", "USER", 35, {"tint": "#EDE9FE"}),
    ("selo_tutor", "Selo tutor dedicado", "BADGE", "BOTH", 15, {"label": "Tutor dedicado"}),
    ("selo_resgate", "Selo de resgate", "BADGE", "BOTH", 45, {"label": "Resgate"}),
    (
        "selo_comunidade",
        "Selo de comunidade ativa",
        "BADGE",
        "COMMUNITY",
        30,
        {"label": "Comunidade ativa"},
    ),
    ("cor_rosa", "Nome rosa", "NAME_COLOR", "USER", 10, {"color": "#DB2777"}),
    ("cor_roxo", "Nome roxo", "NAME_COLOR", "USER", 10, {"color": "#6949F5"}),
    ("cor_azul", "Nome azul", "NAME_COLOR", "USER", 10, {"color": "#2563EB"}),
    # More badges (a profile shows up to three). The team badge is priced out of reach on
    # purpose: it is granted by staff through the admin, never bought.
    (
        "selo_veterano",
        "Selo veterano",
        "BADGE",
        "USER",
        25,
        {"label": "Veterano", "badge_color": "#F97316"},
    ),
    (
        "selo_equipe",
        "Selo da equipe",
        "BADGE",
        "USER",
        9999,
        {"label": "Equipe", "badge_color": "#0F172A"},
    ),
    # Accent colors: the highlight of buttons and panel headers.
    ("destaque_framboesa", "Destaque framboesa", "ACCENT_COLOR", "USER", 20, {"color": "#DB2777"}),
    ("destaque_azul", "Destaque azul-céu", "ACCENT_COLOR", "USER", 20, {"color": "#2563EB"}),
    ("destaque_verde", "Destaque verde-folha", "ACCENT_COLOR", "USER", 20, {"color": "#16A34A"}),
    # Profile section: unlocks a free-text block on the profile.
    ("secao_sobre", "Seção: sobre mim", "SECTION", "USER", 40, {}),
    ("secao_rotina", "Seção: rotina do pet", "SECTION", "USER", 55, {}),
]

TEAM_BADGE_CODE = "selo_equipe"  # granted by staff, never bought

# Wallpapers need an uploaded image, so they are drawn by `images.wallpaper_image`.
# (code, name, price, fit, (top color, bottom color))
WALLPAPERS = [
    ("papel_ceu", "Papel céu de algodão", 35, "cover", ("#BAE6FD", "#F5D0FE")),
    ("papel_gramado", "Papel gramado", 30, "cover", ("#BBF7D0", "#FEF9C3")),
    ("papel_por_do_sol", "Papel pôr do sol", 40, "cover", ("#FED7AA", "#FBCFE8")),
    ("papel_bolinhas", "Papel bolinhas (repetido)", 25, "tile", ("#E0E7FF", "#FCE7F3")),
]

# Community banners drawn offline, used when a community has none.
BANNER_COLORS = [("#FBCFE8", "#C7D2FE"), ("#BAE6FD", "#BBF7D0"), ("#FED7AA", "#FDE68A")]

# Text for the profile sections ((title, text)).
SECTION_TEXTS = [
    ("Sobre mim", "Tutora de dois gatos e uma cachorra. Fotografo tudo, principalmente cochilos."),
    ("Rotina do pet", "Passeio às 7h, petisco às 15h e muito carinho depois do jantar."),
    (
        "Meus bichos",
        "Mel (labradora), Pipoca (gato laranja) e Nuvem (gata cinza que manda na casa).",
    ),
    ("Dicas rápidas", "Água fresca sempre, consulta anual e muita paciência com adoções difíceis."),
]

# Accounts and communities that show the administration states of the app.
SHOWCASE_USERS = {
    "suspended": ("suspenso_demo", "Sofia Suspensa"),
    "banned": ("banido_demo", "Bento Banido"),
    "deleted": ("excluido_demo", "Elis Excluída"),
}
SHOWCASE_COMMUNITIES = [
    (
        "pets_suspensa",
        "Pets em pausa",
        "suspend",
        "Comunidade suspensa pela equipe (demonstração).",
    ),
    ("pets_banida", "Pets fora das regras", "ban", "Comunidade banida pela equipe (demonstração)."),
    (
        "pets_excluida",
        "Pets que partiram",
        "delete",
        "Comunidade excluída pela líder (demonstração).",
    ),
]

# First posts of the administration showcase (every post of the demo is different).
SHOWCASE_USER_POSTS = {
    "suspended": "Ração em promoção, corram! Link no meu perfil, link no meu perfil, link no meu perfil.",
    "banned": "Quem não concorda comigo sobre ração deveria sair desta comunidade.",
    "deleted": "Foi bom enquanto durou. Cuidem bem dos seus pets e deem um abraço neles por mim.",
}
SHOWCASE_COMMUNITY_POSTS = {
    "suspend": "Bem-vindos! Aqui a conversa ficou acalorada e a equipe pediu uma pausa.",
    "ban": "Primeira publicação desta comunidade, antes de a equipe revisar as regras.",
    "delete": "Encerrando esta comunidade. Obrigada a quem passou por aqui e cuidou dos seus bichinhos.",
}

# Each person who unlocks the profile section writes their own.
SECTION_BY_USER = {
    "moderador_demo": (
        "Meus seis gatos",
        "Mingau, Biscoito, Tapioca e mais três que fingem ser independentes. Visitas são bem-vindas, com pelos.",
    ),
    "marcos_esponja": (
        "Rotina do Bolinha",
        "Passeio às 7h, petisco às 15h e muito carinho depois do jantar. Ele só falha na parte de ficar parado.",
    ),
    "patricio_estrela": (
        "Lista de dúvidas",
        "1. Por que ele olha para a parede? 2. O que ele pensa? 3. Posso comer isso? (Já aprendi que não.)",
    ),
    "lucas_molusco": (
        "Sobre mim",
        "Clarinetista de fim de semana, tutor do Mozart por vontade do Mozart. Silêncio é bem-vindo.",
    ),
    "seu_eugenio": (
        "Dicas de economia",
        "Compre a granel, dê o banho em casa e brinque de graça. O Moeda aprova só a última.",
    ),
    "plinio_plancton": (
        "Plano do dia",
        "1. Dominar o banco. 2. Dominar a fonte. 3. Voltar para casa antes do jantar da Karen.",
    ),
}
