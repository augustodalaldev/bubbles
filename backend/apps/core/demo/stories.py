"""What the demo people write: posts (with the conversations under them) and letters.

`photo(pet, text, n, community)`: n pictures of that pet. `post(text, community, thread)`: text only.
A thread is a list of `(username, text)` or `(username, text, parent_index)`; the parent is the
position of another comment in the same list. Entries are in order of importance: running the
seed with few posts per person keeps the first ones.
"""

G, C, A, F, L, M, P, V = (
    "gatos_de_apartamento",
    "caes_de_grande_porte",
    "adocao_responsavel",
    "fotos_engracadas",
    "filhotes_fofos",
    "pets_da_melhor_idade",
    "passeios_e_trilhas",
    "veterinario_responde",
)


def photo(pet, text, n=1, community=None):
    return {"pet": pet, "text": text, "photos": n, "community": community, "thread": []}


def post(text, community=None, thread=()):
    return {"pet": None, "text": text, "photos": 0, "community": community, "thread": list(thread)}


STORIES = {
    "moderador_demo": [
        photo(
            "mingau",
            "O Mingau decidiu que a caixa de sapato é dele. O sapato, coitado, ficou sem casa.",
            1,
            G,
        ),
        post(
            "Dica de quem tem seis gatos: uma caixa de areia por gato, mais uma extra. Parece exagero, mas evita muita briga e muita confusão.",
            G,
            [
                (
                    "nat_cardume",
                    "Concordo! A regra é número de gatos mais um, em locais separados. Ajuda muito no estresse.",
                ),
                (
                    "fred_sardinha",
                    "Fiz isso aqui em casa e acabaram as 'surpresas' no tapete. Funciona mesmo.",
                ),
                ("gabriel_caracol", "Miau."),
            ],
        ),
        photo(
            "biscoito",
            "O Biscoito aprendeu a abrir a porta do armário. Agora a gente guarda a ração com cadeado. Sim, cadeado.",
        ),
        photo(
            "tapioca",
            "Sol da tarde e a Tapioca em modo estátua. Já são 40 minutos sem mexer um bigode.",
            2,
        ),
        post(
            "Para quem está pensando em adotar um gato: ele não é 'independente' como dizem. Precisa de brincadeira diária, de caixa limpa e de colo quando pede. Dá trabalho, e vale cada minuto.",
            A,
            [
                (
                    "tomas_peixoto",
                    "Obrigado, Marlene. Estou com cachorro, mas penso em um gato mais para frente. Vou lembrar disso.",
                ),
                ("taina_tilapia", "Perfeito! Posso usar essa frase na nossa feira de adoção?"),
                ("moderador_demo", "Fique à vontade, Tainá.", 1),
            ],
        ),
        photo(
            "mingau",
            "O Mingau acordou animado e resolveu 'ajudar' a arrumar a cama. A cama perdeu.",
        ),
        post(
            "Lembrete com carinho: nada de compra e venda de animais e muito respeito entre tutores. Obrigada por manterem este lugar tranquilo.",
            G,
        ),
    ],
    "marcos_esponja": [
        photo("bolinha", "Bom dia, mundo!! O Bolinha já está pronto para o passeio da manhã!!"),
        photo(
            "bolinha",
            "O Bolinha descobriu a mangueira do jardim. Ele ficou feliz. O jardim ficou lama. Eu fiquei encharcado. Dia perfeito!!",
            2,
            F,
        ),
        post(
            "Quem aí também tem golden e não aguenta mais pelo na roupa? Escova diária salva vidas, ou pelo menos o sofá. Alguma dica de escova boa?",
            C,
            [
                (
                    "sandra_esquilo",
                    "Escova de cerdas de aço com ponta arredondada funciona bem. E banho a cada 3 ou 4 semanas.",
                ),
                (
                    "nat_cardume",
                    "E ração de boa qualidade ajuda no pelo. Se a queda aumentar de repente, vale ver com o veterinário.",
                ),
                ("marcos_esponja", "Obrigado, gente!! Vou testar a escova esta semana!!", 0),
            ],
        ),
        photo(
            "bolinha",
            "O Bolinha descobriu o gelo derretendo no congelador e latiu para ele por dez minutos!!",
        ),
        photo(
            "bolinha",
            "Trilha de domingo com a Sandra e a Fagulha!! O Bolinha caiu no riacho duas vezes. Duas!!",
            2,
            P,
        ),
        post(
            "Lembrete, pessoal!! A gente combinou de recolher o cocô no parque. O Bolinha deixa um cartão de visita todo dia, e eu recolho todo dia!!",
            C,
            [
                ("seu_eugenio", "Boa! E o saquinho reutilizável sai mais em conta."),
                ("otavio_atum", "Ótimo exemplo. Bom para a vizinhança e para a imagem dos cães."),
            ],
        ),
        photo(
            "bolinha",
            "Bolinha dormindo de barriga para cima depois do banho. Cheiro de shampoo e felicidade!!",
        ),
        post(
            "Alguém quer marcar um passeio coletivo no parque no sábado de manhã? Levamos água e bolinhas!!",
            P,
            [
                ("patricio_estrela", "Eu vou! Qual parque?"),
                ("marcos_esponja", "O de sempre, Patrício!!", 0),
                ("sandra_esquilo", "Combinado. Levo a Fagulha e uma tigela de água."),
                ("plinio_plancton", "A Karen estará lá. Com um plano."),
            ],
        ),
    ],
    "patricio_estrela": [
        post(
            "Meu cachorro olhou para a parede por 40 minutos hoje. Isso é normal? Ele estava bem, só parado olhando.",
            V,
            [
                (
                    "nat_cardume",
                    "Patrício, se ele estava bem, comendo e brincando, geralmente é só cachorro sendo cachorro. Se virar rotina ou ele parecer perdido, vale conversar com o veterinário.",
                ),
                ("moderador_demo", "Concordo. Às vezes eles ouvem algo que a gente não escuta."),
                ("patricio_estrela", "Entendi. Eu achei que ele estava meditando.", 0),
            ],
        ),
        post(
            "Dei um pedacinho de chocolate para o Pedra porque ele pediu com os olhos. Tudo bem?",
            V,
            [
                (
                    "nat_cardume",
                    "NÃO. Chocolate é tóxico para cachorro. Leve agora ao veterinário e leve a embalagem.",
                ),
                ("otavio_atum", "Vai agora, Patrício. Não espere sintoma aparecer."),
                (
                    "patricio_estrela",
                    "Corri aqui e ele está bem, o vet fez lavagem e liberou. Nunca mais.",
                    0,
                ),
                ("nat_cardume", "Que alívio! E obrigada por voltar para contar.", 2),
                ("seu_eugenio", "Chocolate é caro e perigoso. Aprendam com o Patrício."),
            ],
        ),
        photo("pedra", "Tentei ensinar o Pedra a sentar. Ele deitou. Considero um sucesso."),
        photo(
            "pedra",
            "Comprei uma casinha de cachorro gigante. O Pedra ficou com a caixa em que ela veio.",
            1,
            F,
        ),
        post(
            "Alguém sabe se cachorro pode tomar banho de mar? O Pedra viu o mar numa foto e ficou muito empolgado.",
            V,
            [
                (
                    "sandra_esquilo",
                    "Pode, mas com cuidado: não deixe beber a água salgada, enxágue com água doce depois e evite o sol forte.",
                ),
                ("marcos_esponja", "O Bolinha ama o mar!! Só leve água fresca para ele beber!!"),
                (
                    "nat_cardume",
                    "Complementando: cuidado com anzol e vidro na areia, e observe a pele depois.",
                    0,
                ),
            ],
        ),
        photo(
            "pedra",
            "O Pedra cheirou o mesmo poste por 15 minutos. Fiquei do lado dele esperando. Aprendi muito sobre paciência.",
        ),
        post(
            "Acho que o Pedra está me ensinando mais do que eu a ele. Ontem ele me ensinou que o chinelo é para morder.",
            F,
            [
                ("lucas_molusco", "Entendo. Meu gato já me ensinou que o vaso é para derrubar."),
                ("gabriel_caracol", "Miau."),
            ],
        ),
        photo("pedra", "O Pedra dorme com a pata no meu rosto. Não sei se é carinho ou protesto."),
    ],
    "lucas_molusco": [
        photo(
            "mozart",
            "O Mozart derrubou meu clarinete da estante. De novo. Eu sei que foi de propósito.",
            1,
            G,
        ),
        post(
            "Todos os meus vizinhos têm cachorro que late. O meu gato me ignora com elegância. Prefiro assim.",
            None,
            [("gabriel_caracol", "Miau."), ("lucas_molusco", "Obrigado, Gabriel.", 0)],
        ),
        photo(
            "mozart", "Quinta-feira. O gato dormiu em cima da partitura. Eu toquei por cima.", 1, F
        ),
        photo("mozart", "Ele olhou para mim às 4h da manhã. Não disse nada. Eu entendi tudo."),
        post(
            "Pergunto sem esperança: alguém tem dica para gato que acorda o dono às 4h?",
            G,
            [
                (
                    "moderador_demo",
                    "Lucas, brinque com ele à noite até cansar e dê a última refeição mais tarde. E ignore o escândalo por uma semana. Funciona.",
                ),
                ("fred_sardinha", "Confirmo. Aqui eu uso um brinquedo de pescar antes de dormir."),
                ("lucas_molusco", "Vou tentar. Sem esperança, mas vou.", 0),
            ],
        ),
        photo("mozart", "Hoje ele deixou eu fazer carinho por quatro segundos. Dia histórico."),
    ],
    "seu_eugenio": [
        post(
            "Fiz a conta: ração a granel sai 18% mais barata por quilo que a embalada. Compartilhem se acharem preços melhores.",
            V,
            [
                (
                    "nat_cardume",
                    "Cuidado com o armazenamento: ração a granel precisa ficar em recipiente fechado e longe do calor, senão estraga.",
                ),
                ("seu_eugenio", "Anotado. Guardo em pote com tampa e etiqueta com a data.", 0),
                ("marcos_esponja", "Boa dica!!"),
            ],
        ),
        photo(
            "moeda",
            "O Moeda ganhou um osso de brinquedo da promoção. Valor de mercado: baixo. Valor sentimental: altíssimo.",
        ),
        post(
            "Cobraram R$ 90 num banho e tosa. Aprendi a dar banho em casa. O Moeda reclama, mas aceita. Economia de R$ 80 por mês.",
            None,
            [
                (
                    "perola_baleia",
                    "Pai, você só vai economizar se o Moeda não destruir o banheiro de novo.",
                ),
                ("seu_eugenio", "Foi um incidente isolado, Pérola.", 0),
            ],
        ),
        photo(
            "moeda", "Moeda esperando a hora do jantar. Já esperou 3 horas. Faltam 4 minutos.", 1, C
        ),
        post(
            "Pergunta séria: vale a pena plano de saúde para cachorro? Estou fazendo a conta e não sei se compensa.",
            V,
            [
                (
                    "nat_cardume",
                    "Depende do histórico e da idade. Para filhote e idoso costuma compensar. Compare a mensalidade com o que você gastaria em consultas e vacinas por ano.",
                ),
                (
                    "taina_tilapia",
                    "Na ONG a gente separa uma reserva mensal para imprevistos. Pode ser alternativa.",
                ),
                ("seu_eugenio", "Reserva é uma ideia que me agrada. Obrigado.", 1),
            ],
        ),
        photo(
            "moeda",
            "O Moeda aprendeu a pedir comida de um jeito que me custa caro. Vai ter que trabalhar mais.",
        ),
    ],
    "plinio_plancton": [
        photo(
            "karen",
            "A Karen latiu para um dogue alemão hoje. Ele fugiu. Estamos no controle.",
            1,
            F,
        ),
        post(
            "Dia 4 do plano de dominação do parque: a Karen já conquistou o banco perto da fonte. Amanhã, a fonte.",
            P,
            [
                ("sandra_esquilo", "A Karen merece o banco, mas a Fagulha reivindica a fonte."),
                ("plinio_plancton", "Declaração de guerra aceita.", 0),
                ("marcos_esponja", "Vai ser épico!!"),
            ],
        ),
        photo("karen", "Karen de casaquinho. Está com frio? Não. Está elegante."),
        photo(
            "karen",
            "Foto oficial da Karen para o jornal do bairro. Ela ainda não sabe, mas já é conhecida.",
        ),
        post(
            "Aviso: cães pequenos exigem respeito. Uma chihuahua de 2 kg já derrubou um aspirador de pó.",
            None,
            [
                ("seu_eugenio", "O aspirador custa caro, Plínio."),
                ("plinio_plancton", "A Karen não paga conta, Eugênio.", 0),
            ],
        ),
        photo("karen", "Karen dormindo debaixo do cobertor. Planejando o próximo passo."),
    ],
    "sandra_esquilo": [
        photo(
            "fagulha",
            "Trilha de 12 km hoje. A Fagulha voltou querendo mais. Eu voltei querendo cama.",
            2,
            P,
        ),
        post(
            "Dica de dia quente: passeio só antes das 8h ou depois das 18h. O asfalto queima a patinha. Encoste a palma da mão no chão por 7 segundos: se não aguenta, o cachorro também não.",
            P,
            [
                ("patricio_estrela", "Como assim, a palma da mão?"),
                (
                    "sandra_esquilo",
                    "Encosta a mão no chão por 7 segundos. Se for desconfortável para você, queima a patinha.",
                    0,
                ),
                ("patricio_estrela", "Ah, entendi. Vou testar!", 1),
                (
                    "nat_cardume",
                    "Ótima dica! E se notar bolha ou vermelhidão na almofadinha, procure o veterinário.",
                ),
            ],
        ),
        photo("fagulha", "A Fagulha tentando pastorear os patos do lago. Eles não colaboraram."),
        post(
            "Domingo, 7h, trilha leve de 5 km no parque. Aberto a todos os cães que aceitam outros cães. Levem água e saquinho.",
            P,
            [
                ("marcos_esponja", "Eu vou!! Com o Bolinha!!"),
                ("otavio_atum", "Levo o Trovão. Ele está bem em treino de guia."),
                ("plinio_plancton", "A Karen irá avaliar o terreno."),
                ("sandra_esquilo", "Fechado, pessoal. Vai ser divertido.", 0),
            ],
        ),
        photo(
            "fagulha",
            "Depois do treino, a Fagulha capotou no tapete. Em 2 minutos estava dormindo.",
        ),
        photo(
            "fagulha",
            "Fagulha e o Bolinha dividindo a sombra depois da trilha. Amizade de verdade.",
            1,
            C,
        ),
    ],
    "perola_baleia": [
        photo("gabi", "A Gabi ganhou um laço novo e já se acha influenciadora.", 1, L),
        photo(
            "gabi",
            "Meu pai comprou o casaquinho da Gabi. Só custou 60 reais e ele ainda reclamou. Mas comprou!",
        ),
        post(
            "Gente, a Gabi comeu um pedaço de pizza e agora está com uma cara de culpa que eu não aguento.",
            F,
            [
                (
                    "nat_cardume",
                    "Pizza tem muita gordura e cebola ou alho, que fazem mal. Observe se vomita ou fica molinha e fale com o vet se piorar.",
                ),
                ("seu_eugenio", "Pérola, eu avisei sobre a pizza."),
                ("perola_baleia", "Pai, você comeu primeiro!", 1),
            ],
        ),
        photo("gabi", "A Gabi no banho de espuma. Parece uma nuvem brava.", 1, F),
        photo("gabi", "Passeio antes da aula, de vestido e tudo. A Gabi virou assunto da rua."),
        post(
            "Alguém tem dica de tosa para poodle toy? Quero um corte fofo, mas que não dê muito trabalho.",
            L,
            [
                (
                    "bianca_bagre",
                    "A tosa 'ursinho' é fofa e fácil de manter. Peça para deixarem o pelo do rosto arredondado.",
                ),
                ("taina_tilapia", "E escovar a cada dois dias evita nós."),
            ],
        ),
    ],
    "gabriel_caracol": [
        photo("concha", "Concha.", 1, G),
        photo("espiral", "Espiral, às 3h da manhã."),
        post("Hoje não.", None, [("lucas_molusco", "Entendo.")]),
        photo("concha", "Concha de novo.", 1, F),
        photo("espiral", "Espiral também.", 2),
        photo("concha", "Janela."),
        post(
            "Miau.",
            G,
            [("moderador_demo", "Concordo, Gabriel."), ("lucas_molusco", "Concordo também.")],
        ),
    ],
    "tomas_peixoto": [
        post(
            "Primeira semana com a Linguiça. Alguém me ensina a ler o rabo dela? Ela balança de um jeito que eu não entendo.",
            V,
            [
                (
                    "otavio_atum",
                    "Rabo solto e balançando de lado geralmente é alegria. Rabo baixo e rápido pode ser nervosismo. Observe o corpo todo, não só o rabo.",
                ),
                (
                    "nat_cardume",
                    "E orelhas, olhos e postura ajudam a entender. Em pouco tempo você aprende.",
                ),
                ("tomas_peixoto", "Obrigado! Vou observar mais.", 0),
            ],
        ),
        photo(
            "linguica",
            "A Linguiça escavando o sofá. Acho que ela estava procurando alguma coisa. Ou só gosta de cavar.",
            1,
            L,
        ),
        photo("linguica", "Primeiro passeio sem puxar a guia! Foram 8 minutos de glória."),
        post(
            "Para quem adotou recentemente: como vocês lidaram com os primeiros dias? A Linguiça chora de noite e eu não sei se deixo dormir comigo.",
            A,
            [
                (
                    "taina_tilapia",
                    "Os primeiros dias são de adaptação. Uma caminha perto de você, uma roupa com o seu cheiro e rotina ajudam bastante.",
                ),
                ("moderador_demo", "Paciência, Tomás. Em uma ou duas semanas melhora muito."),
                (
                    "fred_sardinha",
                    "Aqui foi assim com os três. Hoje dormem onde querem, que é o nosso lugar.",
                ),
            ],
        ),
        photo("linguica", "A Linguiça dormiu no meu travesseiro. Sobrou um cantinho para mim."),
        photo(
            "linguica", "Foto do dia em que a Linguiça chegou: assustada. Hoje: dona da casa.", 1, A
        ),
    ],
    "fred_sardinha": [
        photo(
            "tico",
            "O Tico dormindo dentro da caixa de papelão que era para o Teco. Os dois brigam, mas é amizade.",
            1,
            G,
        ),
        photo("nina", "A Nina chegou aqui com 3 meses, assustada. Hoje manda em tudo.", 1, L),
        post(
            "Resgatei três gatos em momentos diferentes. Dica para quem vai juntar gatos: apresentação gradual, cheiro primeiro, depois contato. Dá trabalho, mas funciona.",
            A,
            [
                (
                    "moderador_demo",
                    "Muito certo, Fred. Troca de cheiro com manta é um ótimo começo.",
                ),
                ("taina_tilapia", "Posso usar essa dica na nossa conversa com adotantes?"),
                ("fred_sardinha", "Fique à vontade.", 1),
            ],
        ),
        photo("teco", "O Teco tentando entender o que é um fio de luz de Natal. Perdeu.", 1, G),
        post(
            "A Nina está espirrando bastante. Já viram algo parecido com os de vocês?",
            None,
            [
                (
                    "moderador_demo",
                    "Espirro pontual é comum, mas se tiver secreção, apatia ou perda de apetite, leve ao veterinário. Mantenha a caixa limpa e observe.",
                ),
                (
                    "nat_cardume",
                    "Complemento: poeira da areia pode irritar. Vale testar uma areia sem perfume.",
                ),
            ],
        ),
        photo("tico", "Tico e Teco dividindo o sol. Hoje não tem briga."),
        photo("nina", "A Nina inspecionando a cozinha como se fosse inspetora sanitária.", 1, G),
    ],
    "nat_cardume": [
        post(
            "Calendário básico de vacinas para filhotes: V8 ou V10 em 3 doses a partir de 6 a 8 semanas, raiva a partir de 12 semanas e reforço anual. Confirme sempre com o seu veterinário.",
            V,
            [
                (
                    "tomas_peixoto",
                    "Obrigado, Nat! A Linguiça já tomou duas doses. Vou ver quando é a terceira.",
                ),
                ("patricio_estrela", "E o Pedra? Esqueci de perguntar ao veterinário."),
                (
                    "nat_cardume",
                    "Patrício, leve a carteirinha na próxima consulta. O vet vai te ajudar.",
                    1,
                ),
            ],
        ),
        post(
            "Sinais de alerta em cães e gatos: vômito repetido, apatia por mais de um dia, recusa de água, dificuldade para respirar ou urinar. Se aparecer, procure uma clínica sem esperar.",
            V,
            [
                (
                    "moderador_demo",
                    "Muito importante. Gato que força a ida à caixa sem urinar é emergência.",
                ),
                ("haroldo_linguado", "Anotado. Com idoso a gente nunca espera."),
            ],
        ),
        photo(
            "zeca",
            "O Zeca descobriu que a mangueira dá água. Ainda não entendeu que é a mesma mangueira de sempre.",
        ),
        post(
            "Mitos que eu ouço na faculdade e na vida: cachorro não precisa escovar os dentes (precisa), banho de leite deixa o pelo mais bonito (não), e 'comida de gente' sempre faz mal (depende, mas muita coisa faz).",
            V,
            [
                ("patricio_estrela", "Eu achava que comida de gente era melhor!"),
                (
                    "nat_cardume",
                    "Algumas coisas podem, outras são perigosas. Chocolate, cebola, uva e xilitol, por exemplo, não.",
                    0,
                ),
                ("seu_eugenio", "Escovar os dentes custa menos que tratar tártaro."),
            ],
        ),
        photo(
            "zeca",
            "Plantão de estudo: o Zeca ouvindo sobre farmacologia. Ele entendeu menos que eu.",
        ),
        photo(
            "zeca", "Domingo de sol com o Zeca. Descanso merecido depois de semana de prova.", 1, C
        ),
    ],
    "haroldo_linguado": [
        photo(
            "duque",
            "O Duque fez 14 anos esta semana. Bolo de ração, vela de mentira e muito carinho.",
            2,
            M,
        ),
        post(
            "Cachorro idoso precisa de: consulta a cada 6 meses, cama macia, comida ajustada e muita paciência. Compartilhem o que funciona aí com os seus.",
            M,
            [
                (
                    "nat_cardume",
                    "Acrescento: exames de sangue e atenção aos dentes. E rampa em vez de escada, se tiver.",
                ),
                ("moderador_demo", "Concordo. Um tapete antiderrapante ajuda muito."),
                ("haroldo_linguado", "Obrigado a todos. O Duque agradece."),
            ],
        ),
        photo(
            "duque",
            "Manhã de sol, um passeio de 10 minutos e olho fechado na grama. Duque feliz.",
            1,
            M,
        ),
        photo("duque", "Hora da soneca. O Duque dorme mais, mas acorda sempre para uma lambida."),
        post(
            "O Duque tem subido pouco as escadas. É da idade ou devo me preocupar?",
            V,
            [
                (
                    "nat_cardume",
                    "Pode ser artrose, comum nessa idade. Vale uma consulta com raio-x e conversar sobre suplemento e rampa.",
                ),
                (
                    "moderador_demo",
                    "Concordo com a Nat. Quanto antes tratar, melhor o conforto dele.",
                ),
                ("haroldo_linguado", "Vou marcar essa semana. Obrigado.", 0),
            ],
        ),
        photo("duque", "O Duque e o cobertor velho de que ele não abre mão."),
    ],
    "taina_tilapia": [
        photo(
            "bidu",
            "O Bidu está para adoção! Beagle, 3 anos, castrado, vacinado e muito carinhoso. Feira de adoção sábado, às 9h, na praça.",
            2,
            A,
        ),
        post(
            "Lembrete para quem quer adotar: pense na rotina, no espaço, nos custos e em quem cuida quando você viaja. Adoção é compromisso por 10 a 15 anos.",
            A,
            [
                (
                    "tomas_peixoto",
                    "Obrigado pelo aviso, Tainá. Isso me ajudou a refletir antes de adotar.",
                ),
                ("moderador_demo", "Muito certo. Gostaria que mais gente lesse isso."),
                ("fred_sardinha", "Concordo. Amor e planejamento andam juntos."),
            ],
        ),
        photo(
            "fiona",
            "A Fiona chegou à ONG esta semana. Dócil, curiosa e muito sociável. Procura um lar.",
            1,
            A,
        ),
        photo(
            "bidu",
            "O Bidu na entrada do abrigo. Todo dia ele espera os voluntários com o rabo balançando.",
        ),
        post(
            "Precisamos de cobertores e ração para o abrigo. Quem puder ajudar, escreva uma carta aqui. Obrigada!",
            A,
            [
                ("marcos_esponja", "Eu levo cobertores!! Quantos precisa??"),
                ("taina_tilapia", "Cerca de 15. Já ajuda muito!", 0),
                ("otavio_atum", "Posso levar uma saca de ração do meu estoque de adestrador."),
            ],
        ),
        photo("fiona", "A Fiona dorme assim, esticada. Quem quer um coração desses?"),
    ],
    "otavio_atum": [
        post(
            "Dica de treino: ensine um comando por vez, em sessões de 5 minutos, com petisco pequeno. Cachorro cansa e perde o foco depois disso.",
            V,
            [
                ("patricio_estrela", "Qual comando eu ensino primeiro? Só sei 'vem'."),
                (
                    "otavio_atum",
                    "'Senta' é um ótimo começo. Segure o petisco acima do nariz dele e espere.",
                    0,
                ),
                ("marcos_esponja", "O Bolinha aprendeu assim!!"),
            ],
        ),
        photo(
            "trovao",
            "O Trovão em treino do 'fica'. Ele aguentou 30 segundos. Para um husky, é conquista.",
            1,
            C,
        ),
        post(
            "Husky não é difícil, é inteligente demais. Se não tiver exercício e desafio, ele inventa trabalho. Geralmente destruindo o seu sofá.",
            C,
            [
                ("marcos_esponja", "Hahaha, o Bolinha faz isso com almofadas!!"),
                ("sandra_esquilo", "Com a Fagulha também. Exercício resolve."),
            ],
        ),
        photo(
            "trovao", "O Trovão uivando. Ele acha que está cantando. Os vizinhos acham outra coisa."
        ),
        post(
            "Passeio sem puxar a guia: pare quando ele puxar e volte a andar quando a guia ficar frouxa. Parece lento, mas é a técnica que mais funciona.",
            P,
            [
                ("tomas_peixoto", "Vou tentar com a Linguiça. Obrigado!"),
                ("seu_eugenio", "E nada de coleira cara. Peitoral simples resolve."),
            ],
        ),
        photo("trovao", "Treino de manhã com o Trovão e o sol nascendo. Dia perfeito.", 1, P),
    ],
    "bianca_bagre": [
        post(
            "Dica de foto: agache até a altura dos olhos do pet. A foto muda completamente. Luz natural de janela resolve 80% do resto.",
            F,
            [
                ("perola_baleia", "Vou testar com a Gabi!!"),
                ("tomas_peixoto", "Obrigado. A Linguiça é difícil de fotografar, mas vou tentar."),
                ("bianca_bagre", "Paciência e um petisco ajudam.", 1),
            ],
        ),
        photo("pipa", "A Pipa na luz da manhã. Samoieda é sorriso sem esforço.", 2, F),
        photo("pipa", "Ensaio da Pipa no campo de flores. Ela adorou. As abelhas, nem tanto."),
        post(
            "Segunda-feira de edição de fotos. Se alguém quiser um ensaio gratuito do pet para o meu portfólio, me mande uma carta aqui.",
            F,
            [
                ("marcos_esponja", "Eu quero!! O Bolinha topa!!"),
                ("bianca_bagre", "Combinado, Marcos! Sábado de manhã.", 0),
                ("fred_sardinha", "Os três gatos topam, se não estiverem dormindo."),
            ],
        ),
        photo("pipa", "A Pipa descobriu a sombra da árvore e decidiu morar nela.", 1, F),
        photo("pipa", "Retrato simples, luz de janela e um pet que não sai do lugar. Dá certo."),
    ],
}

# (sender, recipient, text, reply). Every pair follows each other (see personas.FOLLOWS).
LETTERS = [
    (
        "patricio_estrela",
        "nat_cardume",
        "Oi, Nat! O Pedra comeu um pedaço de sabonete. Ele está bem? Estou na dúvida se é grave.",
        "Patrício, fique calmo. Sabonete costuma dar só enjoo e espuma. Observe vômito ou diarreia por 24h e, se piorar, leve ao vet. E guarde o sabonete!",
    ),
    (
        "marcos_esponja",
        "patricio_estrela",
        "Patrício! Vamos levar o Bolinha e o Pedra ao parque no sábado? Eu levo a bolinha, você leva o Pedra.",
        "Levo o Pedra! Esqueci qual dos dois é o Pedra, mas levo um deles.",
    ),
    (
        "lucas_molusco",
        "moderador_demo",
        "Dona Marlene, o Mozart anda me acordando às 4h. A senhora que entende de gatos: o que eu faço?",
        "Lucas, gato adulto acorda no horário em que o dono se mexe. Brinque com ele à noite, dê a refeição mais tarde e ignore o escândalo das 4h por uma semana. Funciona.",
    ),
    (
        "seu_eugenio",
        "perola_baleia",
        "Pérola, o casaquinho da Gabi custou 60 reais. Vamos conversar sobre orçamento.",
        "Pai, ela estava com frio. E eu paguei com a minha mesada. Você me paga um sorvete?",
    ),
    (
        "plinio_plancton",
        "sandra_esquilo",
        "Sandra, a Karen quer desafiar a sua border collie para uma corrida. Ela perderia, mas com dignidade.",
        "Plínio, a Fagulha topa, mas a Karen sai com 50 metros de vantagem. Sábado, 7h, no parque.",
    ),
    (
        "tomas_peixoto",
        "taina_tilapia",
        "Tainá, vi a feira de adoção de sábado. Adotei a Linguiça faz uma semana e ainda estou aprendendo. Posso ir conversar com os voluntários?",
        "Claro, Tomás! Passe lá sábado às 9h, tem gente ótima para ajudar. Leve a Linguiça.",
    ),
    (
        "haroldo_linguado",
        "nat_cardume",
        "Nat, o Duque tem 14 anos e anda subindo pouco as escadas. Isso é da idade?",
        "Haroldo, pode ser artrose, comum nessa idade. Vale uma consulta com raio-x e conversar sobre suplemento e uma rampa no lugar da escada.",
    ),
    (
        "bianca_bagre",
        "marcos_esponja",
        "Marcos, quero fazer um ensaio do Bolinha na luz da manhã. Topa no sábado? É de graça, quero portfólio.",
        "Topo!! Ele só não promete ficar parado!!",
    ),
    (
        "otavio_atum",
        "patricio_estrela",
        "Patrício, vi o seu post sobre o 'senta'. Posso te dar uma aula grátis no parque? Ele precisa de um comando de cada vez.",
        "Aceito! Qual comando é o primeiro? Eu só sei 'vem'.",
    ),
    (
        "fred_sardinha",
        "moderador_demo",
        "Dona Marlene, a Nina está espirrando muito. Já deu algo parecido com os seus?",
        "Fred, espirro pontual é comum, mas se tiver secreção ou apatia, procure o veterinário. Mantenha a caixa limpa e observe.",
    ),
    ("gabriel_caracol", "lucas_molusco", "Miau.", "Entendo."),
]

# More everyday photos, so a profile's mural is not empty (community posts live on the community page).
_EXTRAS = {
    "moderador_demo": [
        photo(
            "biscoito",
            "O Biscoito e o novelo de lã. O novelo perdeu a dignidade e metade do comprimento.",
        ),
        photo(
            "tapioca",
            "A Tapioca descobriu que a cadeira da sala é mais confortável que a caminha de 80 reais. Tudo bem, a cadeira é dela.",
        ),
    ],
    "marcos_esponja": [
        photo(
            "bolinha",
            "O Bolinha acha que o aspirador é um bicho. Latiu, rosnou e depois fez as pazes. Dia de aprendizado!!",
        ),
        photo(
            "bolinha",
            "Domingo no parque com a galera!! O Bolinha conheceu dois cachorros novos e já se sente famoso!!",
            2,
        ),
    ],
    "patricio_estrela": [
        photo(
            "pedra",
            "O Pedra enterrou o brinquedo no jardim. Depois ficou procurando. Eu ajudei. Acho que não ajudou.",
        ),
        photo(
            "pedra",
            "Hoje o Pedra me olhou com a cabeça inclinada. Juro que ele entendeu o que eu disse. Eu mesmo não entendi.",
        ),
    ],
    "lucas_molusco": [
        photo(
            "mozart",
            "O Mozart sentou exatamente no meio do corredor. Eu contornei. Ele sabe que eu contorno.",
        ),
        photo("mozart", "Ensaio de clarinete. Plateia: um gato. Crítica: um bocejo."),
    ],
    "seu_eugenio": [
        photo(
            "moeda",
            "Moeda deitado em cima do saco de ração. Seguro de que ninguém leva. Segurança de graça, afinal.",
        ),
        photo(
            "moeda",
            "O Moeda tentou subir no sofá com a bola na boca. Subiu. A bola ficou no sofá. O sofá, com baba.",
        ),
    ],
    "plinio_plancton": [
        photo("karen", "Karen observando o portão. Ninguém entra sem a aprovação dela."),
        photo("karen", "Karen com o laço novo. Segundo ela, o laço é de comandante.", 2),
    ],
    "sandra_esquilo": [
        photo("fagulha", "Alongamento pós-corrida. A Fagulha faz também, do jeito dela: capota."),
        photo(
            "fagulha",
            "A Fagulha e o graveto favorito. Já é o terceiro do dia. Todos 'insubstituíveis'.",
        ),
    ],
    "perola_baleia": [
        photo(
            "gabi",
            "A Gabi no meu colo durante a maratona de série. Perdeu o episódio, ganhou o carinho.",
        ),
        photo("gabi", "Dia de tosa! A Gabi saiu da loja se achando a rainha do bairro."),
    ],
    "gabriel_caracol": [photo("concha", "Almoço."), photo("espiral", "Espiral olhando.")],
    "tomas_peixoto": [
        photo(
            "linguica",
            "A Linguiça descobriu que passa por baixo da cama. Eu descobri que ela não consegue voltar. Resgate feito.",
        ),
        photo(
            "linguica",
            "Quatro semanas de Linguiça. Já aprendi a ler o rabo: balançando de lado é felicidade.",
        ),
    ],
    "fred_sardinha": [
        photo("nina", "A Nina dormindo no teclado. Hoje o relatório vai atrasar."),
        photo("teco", "O Teco encontrou uma meia e agora vive em outro mundo."),
    ],
    "nat_cardume": [
        photo(
            "zeca",
            "Dia de prova! O Zeca fez companhia durante as 4 horas. Contribuição acadêmica: zero. Apoio emocional: máximo.",
        ),
        photo("zeca", "Passeio rápido entre as aulas. O Zeca nunca me julga pelo cansaço."),
    ],
    "haroldo_linguado": [
        photo("duque", "O Duque e a poltrona. Ele considera que a poltrona é dele desde 2013."),
        photo(
            "duque",
            "Hoje de manhã o Duque deu uma corridinha atrás da bola. Curta, mas ele estava feliz demais.",
        ),
    ],
    "taina_tilapia": [
        photo("bidu", "O Bidu aprendeu a dar a pata para quem chega. Já é o recepcionista da ONG."),
        photo(
            "fiona",
            "A Fiona adora a luz da janela do abrigo. Quem for adotar já sabe onde colocar a caminha.",
        ),
    ],
    "otavio_atum": [
        photo(
            "trovao",
            "O Trovão aprendeu a esperar na porta até eu liberar. Só levou três semanas e uns quarenta petiscos.",
        ),
        photo(
            "trovao",
            "Fim de treino e uma soneca merecida. O Trovão dorme como se tivesse carregado o mundo.",
        ),
    ],
    "bianca_bagre": [
        photo("pipa", "Pipa de perfil. Quando a luz bate certo no pelo, nem precisa de filtro."),
        photo(
            "pipa",
            "Teste de lente nova. A Pipa, como sempre, foi a modelo mais paciente que já tive.",
        ),
    ],
}


def _finish() -> None:
    for username, extras in _EXTRAS.items():
        STORIES[username].extend(extras)
    # A person tags only their first photo for a community; the rest stay on their own profile.
    for entries in STORIES.values():
        tagged = False
        for entry in entries:
            if entry["pet"] and entry["community"]:
                if tagged:
                    entry["community"] = None
                tagged = True


_finish()
