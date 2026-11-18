# Observações da revisão (versão 1.1, 18/11/2026)

Nenhum arquivo do projeto nem o `.docx` foi alterado. A fonte da verdade foi o código (models, serviços, rotas, permissões, testes e telas).

## (a) Requisitos: o que mudou

### Novos
Nenhum RF ou NF novo. A busca, as listas de seguidores, as denúncias e o histórico de auditoria foram incorporados aos requisitos existentes (RF004, RF008 e RF016).

### Alterados
| Requisito | O que mudou (código como referência) |
|---|---|
| RF001 | Dados do cadastro: nome, usuário, e-mail, data de nascimento e senha. Idade mínima 14 anos. Descrição e foto são opcionais. Crédito inicial de 20 soaps. |
| RF002 | Edita nome, descrição, data de nascimento e foto; troca senha e e-mail; exclusão anonimiza e é bloqueada para líder. Customização saiu daqui (já está no RF011). |
| RF003 | Só nome e identificador são obrigatórios; descrição, diretrizes e imagem são opcionais. O investimento vai para a carteira da comunidade. |
| RF004 | Inclui busca de perfis. Banido não reingressa; líder só sai após transferir. |
| RF005 | "Permanente ou temporária" são dois tipos: publicação permanente (texto e uma imagem opcional, 10 soaps) e bubblepop (imagem, 1 a 48 h, 1 soap a cada 4 h). |
| RF006 | Só imagem (uma por publicação), sem vídeo. Bloqueada em comunidade arquivada, suspensa ou bloqueada e para membro silenciado ou banido. |
| RF007 | "Curtir" virou apoio com soap. Comentar é gratuito e aceita respostas. |
| RF008 | Amizade virou seguir/deixar de seguir, sem aprovação. |
| RF009 | Feed cronológico com sugestões limitadas e bandeja de bubblepops. |
| RF010 | Recados viraram cartas (só para quem se segue, imutáveis, uma resposta por carta). Não há mural, aprovação nem exclusão. |
| RF011 | Lista real de itens (molduras, temas, selos, cor do nome, papel de parede, cor de destaque, bolha de comentários e cartas, seção de texto). |
| RF012 | Edita nome, descrição, foto e banner; silencia e bane membros comuns; exclui publicações e comentários. |
| RF013 | Compra com a carteira da comunidade; líder ou administrador. |
| RF014 | Diretrizes, promover/rebaixar, transferir liderança, arquivar e excluir. Sem "privacidade". |
| RF015 | Suspensão com prazo e motivo, banimento e reativação, com efeitos definidos. |
| RF016 | Suspender, bloquear e reativar comunidades; denúncias; excluir conteúdo; histórico. Sem "excluir comunidade" pelo administrador do sistema. |
| RF017 | Variáveis reais da economia (com os valores padrão do código) e ajuste de saldo com motivo. Sem "taxas de expiração". |
| RF018 | Ganho passivo de 5 soaps a cada 5 minutos, até 15 por dia. Acrescentada a remoção automática de bubblepops expirados (feita pelo agendador). |
| NF003 | Também celulares (verificado em 375, 768 e 1280 px, só no Chrome). |
| NF007 | Acrescentado o histórico de soap imutável. |
| NF008 | Usuário ou e-mail, tokens de curta duração, limite de tentativas. Hash padrão do Django (PBKDF2). |
| NF009 | Exclusão anonimiza (não é definitiva). Removido "servidor de banco seguro", que o código não comprova. |
| NF010 | Só imagens JPEG, PNG, WebP e GIF, 10 MB, uma por publicação, com validação do conteúdo real. Sem vídeo e sem compressão. |
| NF012 | React 18, Vite e Tailwind (não Next.js), Python 3.12, Django 5.2 com DRF, PostgreSQL 17. |
| UC003 e UC005 | Ver `04_casos_de_uso.md`. UC003: pré-condição corrigida. UC005: fluxo principal agora é a publicação permanente; bubblepop é alternativo; sem vídeo e sem compressão. |

### Marcados `[REVISAR]` (decidir: manter, mover para "Trabalhos futuros" ou remover)
| Requisito | Motivo |
|---|---|
| NF001 Tempo de resposta | Meta nunca medida. |
| NF002 Taxa de falhas | Meta nunca medida; não há monitoramento. |
| NF005 Função de ajuda | **Não existe** no sistema. |
| NF006 Disponibilidade | Meta sem hospedagem nem medição. |
| NF011 Compatibilidade de clientes | Só foi testado no Chrome. |

### Trechos do documento antigo que o sistema não faz (removidos do texto; candidatos a "Trabalhos futuros")
Vídeo (MP4, 100 MB, 60 s) e compressão ou transcodificação de mídia; privacidade da comunidade; exclusão de comunidade pelo administrador do sistema (quem exclui é o líder); recados com mural, aprovação e resposta; amizade com solicitação; publicação com ciclo de vida escolhido na mesma postagem; "fundadores" da comunidade; "cápsulas do tempo"; "diretrizes globais"; painel de controle da economia no frontend; verificação de e-mail e recuperação de senha; votação ou fórum em comunidades (aparece só no rascunho).

### Funcionalidades que existem só pela API (sem tela)
Silenciar e banir membros, promover e rebaixar administradores, arquivar comunidade, denunciar e analisar denúncias, ajuste de saldo e alteração das configurações da economia (também pelo Django Admin) e extrato da carteira. Foram descritas como funcionalidades normais; na apresentação, citar que estão disponíveis apenas pela API. Para os prints, as telas existem apenas para: editar dados, diretrizes, transferir liderança e excluir comunidade; suspender, banir e reativar (`/moderation`).

### Detalhes a conferir
- Os requisitos dizem **1 imagem** por publicação (o que a tela faz). O modelo de dados e a regra do sistema aceitam até 4 imagens, por isso o diagrama de classes mostra `0..4` em `BubblegramMedia`. Se quiser, ajuste a multiplicidade para `0..1` no diagrama.
- Os valores citados (20, 10, 300, 1 soap, 5 soaps a cada 5 minutos, até 15 por dia) são os **padrões** definidos no código; o administrador do sistema pode alterá-los.
- Hierarquia dos atores: a estrutura (Usuário → Administrador de comunidade → Líder → Administrador do sistema; Sistema à parte) continua válida. Mudanças a refletir na **figura**: os papéis são por comunidade; o administrador do sistema não é membro, mas passa em todas as checagens de comunidade; o líder pode ser trocado por transferência; não há "fundadores".
- Caso de uso mais representativo (apenas sugestão, não criado): **RF007 Interagir em publicações e comentários (apoio com soap)**, por concentrar a ideia central da rede. O UC005 se parece com o UC003 (ambos gastam soap e enviam imagem).
- Telas para os prints estão no fim de cada UC (`/communities`, `/c/:commname`, `/`, `/u/:username`).
- Diagrama de classes: os 5 blocos Mermaid foram renderizados sem erro (Mermaid 11, Chrome). O diagrama geral é denso por causa do tamanho do modelo; os quatro por domínio são os de leitura fácil. O layout é automático e pode ser ajustado em um editor de Mermaid.

## (b) Inconsistências do documento fora do escopo (não corrigidas)
- **Índice** desatualizado: cita "Ações do Participante", "[RF004] Comprar", "[RF012] Buscar compras", títulos de NF diferentes do corpo e subseção "4.6 Hardware e Software".
- **1.3 Referências:** texto "VER REFERENCIASSSSS" e nenhuma referência listada.
- **1.5.1:** cita "RNF"; o corpo usa "NF" (mantido "NF").
- **1.5.2:** cita um glossário no "tópico 7" que não existe (o tópico 7 é o diagrama de classes) e o símbolo `*` não é usado.
- **Seção 3:** o "Rascunho" (CRUD, amizades, recados, votação ou fórum) ficou no texto.
- **Seção 2:** "Descrição Geral" ainda fala em "curtir" e a 2.1 diz que a segurança é "apenas com senha" (hoje há tokens e limite de tentativas).
- **Seções 5 a 8:** ainda trazem os textos-modelo ("Deve ser colocado aqui...", "Descrever os dois principais...", etc.); a Seção 8 está vazia.
- **Figuras e diagramas desatualizados** (fora do escopo, mas afetados): diagrama de casos de uso, diagramas de atividade de UC003 e UC005 (ainda mostram vídeo, compressão, ciclo de vida e "amigos") e figura de hierarquia dos atores.
- **Capa e histórico:** título "Manual do Sistema, Versão 1.0"; histórico sem a revisão 06; autores e comentários vazios; datas no formato "24/09/26".
- **Visão geral (1.4):** a Seção 8 aparece com ":" e a Seção 7 com ":" em vez de "–", diferente das demais.

## (c) Decisões tomadas
Decidido em 18/11/2026:
1. Os `[REVISAR]` (NF001, NF002, NF005, NF006 e NF011) ficam como estão; você remove depois o que não se adequar.
2. Uma imagem por publicação (RF005, RF006 e NF010 ajustados). No diagrama de classes, a multiplicidade de `BubblegramMedia` passou para `0..1`.
3. Os valores fixados no código aparecem nos requisitos (RF001, RF003, RF005, RF006, RF007, RF009, RF017 e RF018) e nos casos de uso.
4. A menção a denúncias no RF016 fica; na apresentação, dizer que estão disponíveis apenas pela API.
5. Trechos que o sistema não faz: parte foi para o **Escopo Negativo** (2.1) e parte para **Trabalhos Futuros** (8.2); ver `06_escopo_negativo_e_trabalhos_futuros.md`. Foi para o escopo negativo o que foi decisão de projeto não ter (recomendação por IA, chat em tempo real, cápsulas do tempo e visualização única, aprovação de amizades e recados, co-fundadores). Foi para trabalhos futuros o que seria desejável ter (enquetes, mais imagens por publicação, vídeo, mais customizações, privacidade, ajuda, verificação de e-mail e telas de administração).

Em aberto: nenhuma.
