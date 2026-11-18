# 3 Requisitos Funcionais

Esta seção apresenta em detalhes os requisitos funcionais do sistema.

## Ações do Usuário

*[RF001] Cadastrar usuário*

Requisito básico para permitir que pessoas entrem no sistema e criem sua conta. Tendo como entrada nome, nome de usuário, e-mail, data de nascimento e senha, o sistema deve exigir idade mínima de 14 anos e creditar 20 soaps na carteira do novo usuário. Vários usuários poderão se cadastrar simultaneamente.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF002] Gerenciar perfil pessoal (Atualizar/Excluir)*

Permite que o usuário edite seu nome, descrição, data de nascimento e foto, altere sua senha e seu e-mail (confirmando a senha atual) e exclua sua conta. O nome de usuário não pode ser alterado. A exclusão exige a senha, anonimiza os dados pessoais e não é permitida enquanto o usuário for líder de alguma comunidade.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF003] Criar comunidade*

Permite que um usuário funde uma nova comunidade (bolha temática), elevando-se ao papel de Líder. O sistema deve exigir a definição de nome e de um identificador único, permitindo informar também descrição, diretrizes e imagem, e um investimento inicial de 300 soaps, debitado do fundador e transferido para a carteira da comunidade.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF004] Ingressar e sair de comunidades*

Permite que o usuário busque comunidades e perfis, visualize e entre nas comunidades de seu interesse para consumir e publicar conteúdo, bem como saia daquelas que não deseja mais acompanhar. Membros banidos de uma comunidade não podem voltar a ingressar nela, e o líder só pode sair após transferir a liderança.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF005] Publicar no perfil pessoal*

Permite que o usuário crie publicações em sua própria bolha. O sistema deve oferecer dois tipos: a publicação permanente (texto e uma imagem opcional), com custo de 10 soaps, e o bubblepop (imagem com descrição), que expira após um tempo de 1 a 48 horas escolhido pelo autor, com custo de 1 soap a cada 4 horas de duração (arredondado para cima).

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF006] Publicar em comunidade*

Permite que membros ativos de uma comunidade criem publicações dentro daquela bolha, com texto e uma imagem opcional, mediante o pagamento de 10 soaps. A publicação não é permitida em comunidades arquivadas, suspensas ou bloqueadas, nem a membros silenciados ou banidos.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF007] Interagir em publicações e comentários*

Permite que o usuário apoie com soap e comente publicações (no feed, em comunidades ou no perfil de outro usuário), inclusive respondendo a outros comentários. O apoio debita 1 soap do usuário e credita 1 soap ao autor do conteúdo (e 1 soap à comunidade, quando o conteúdo é de comunidade); cada conteúdo só pode ser apoiado uma vez por usuário e não pelo próprio autor. Comentar não tem custo.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF008] Gerenciar conexões (Seguidores)*

Permite que o usuário siga e deixe de seguir outros usuários, sem necessidade de aprovação, e consulte as listas de seguidores e de seguidos de qualquer perfil.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF009] Visualizar feed de atualizações*

O sistema deve gerar e exibir uma linha do tempo (feed) em ordem cronológica, agregando as publicações recentes dos usuários seguidos, as do próprio usuário e as das comunidades das quais ele faz parte, além de um número limitado de sugestões (até 4 publicações populares nas últimas 24 horas e até 4 de pessoas da sua rede). Os bubblepops ativos dos usuários seguidos aparecem em uma bandeja à parte, que permite percorrê-los em sequência.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF010] Enviar e responder cartas*

Permite que o usuário envie cartas (mensagens privadas com texto e imagem opcional) a quem ele segue, consulte suas caixas de entrada e de enviadas e responda às cartas recebidas. A carta não pode ser editada nem excluída, e cada carta pode ter uma única resposta.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF011] Customizar perfil*

Permite que o usuário customize o perfil a partir da compra, com soap, de itens pré-definidos pelo sistema: molduras do avatar, temas, selos (até três exibidos), cor do nome, papel de parede (cadastrado pelo administrador do sistema), cor de destaque, bolha de comentários e cartas, e uma seção de texto livre. O usuário pode a qualquer momento equipar e desequipar esses itens.

**Prioridade:** ◻ Essencial 🗹 Importante ◻ Desejável

## Ações do Administrador de Comunidade

*[RF012] Gerenciar comunidade*

Permite que administradores editem as informações da comunidade (nome, descrição, foto e banner), silenciem ou banam membros comuns e excluam publicações e comentários feitos na comunidade.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF013] Customizar comunidade*

Permite que um administrador customize a comunidade a partir da compra de itens pré-definidos pelo sistema (como molduras, temas e selos) com o soap da carteira da comunidade. O administrador pode a qualquer momento equipar e desequipar esses itens.

**Prioridade:** ◻ Essencial 🗹 Importante ◻ Desejável

## Ações do Líder de Comunidade

*[RF014] Gerenciar configurações da comunidade (Nível Estrutural)*

Permite que o líder defina as diretrizes da comunidade, promova membros a administradores ou os rebaixe, transfira a liderança a outro membro ativo, arquive a comunidade (que passa a ser somente leitura) e a exclua. A exclusão exige que o líder digite o nome da comunidade e remove os membros e a página da comunidade.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

## Ações do Administrador do Sistema

*[RF015] Gerenciar contas globais (Moderação Superior)*

Permite que o administrador do sistema suspenda temporariamente (com prazo e motivo), bana ou reative contas de usuários que violem as diretrizes globais da plataforma. A conta suspensa continua entrando e lendo, mas não publica, comenta, apoia nem envia cartas; a conta banida não consegue entrar e seu conteúdo deixa de ser exibido.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF016] Gerenciar comunidades globais (Moderação Superior)*

Permite que o administrador do sistema suspenda temporariamente, bloqueie ou reative comunidades que infrinjam regras legais, de direitos autorais ou diretrizes críticas da rede, a partir de denúncias de usuários ou de sua própria auditoria. A comunidade suspensa ou bloqueada deixa de aparecer nas listas e passa a ser somente leitura para seus membros. O administrador também analisa as denúncias, exclui publicações e comentários e consulta o histórico de todas as ações administrativas, registradas com o motivo.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

*[RF017] Regular economia de Soap*

Permite que o administrador do sistema ajuste as variáveis econômicas, como o valor inicial do cadastro, os custos de publicação e de fundação, o valor do apoio, o ganho passivo, o limite diário e a duração mínima e máxima dos bubblepops, além de creditar ou debitar o saldo de uma carteira com o motivo registrado. Os valores padrão são: 20 soaps no cadastro, 10 soaps por publicação, 300 soaps para fundar uma comunidade, 1 soap por apoio (com 1 soap para o autor e 1 para a comunidade), 1 soap a cada 4 horas de bubblepop (de 1 a 48 horas), e ganho passivo de 5 soaps a cada 5 minutos, até 15 soaps por dia.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável

## Ações do Sistema

*[RF018] Distribuir soap passivamente e expirar bubblepops*

O sistema deve rastrear de forma autônoma a presença do usuário e depositar automaticamente a moeda "soap" em sua carteira a cada 5 minutos de uso (5 soaps por intervalo), respeitando um limite de 15 soaps por dia. O sistema também deve remover automaticamente os bubblepops cujo prazo terminou.

**Prioridade:** 🗹 Essencial ◻ Importante ◻ Desejável
