# 5.1 Descrição de Casos de Uso

## UC003 – Criar comunidade

**Breve Descritivo:** Este caso de uso descreve o processo de criação de uma nova comunidade por um usuário, elevando-o ao papel de Líder de Comunidade.

**Pré-condições:** Usuário autenticado no sistema informa sua intenção de criar uma nova comunidade.

**Atores:** Usuário, Sistema.

**Cenários Principais:**

1 – Solicita a opção de criação de uma nova comunidade – Usuário.

2 – Consulta o saldo atual de soap da carteira do usuário, verifica se há no mínimo 300 soaps disponíveis e exibe o formulário de criação, com o saldo e o investimento inicial – Sistema.

3 – Informa os seguintes dados obrigatórios da comunidade: Nome e Identificador (@) – Usuário.

4 – Informa opcionalmente a Descrição, as Diretrizes e uma imagem para o ícone da comunidade (formatos JPEG, PNG, WebP ou GIF, com tamanho máximo de 10 MB) e confirma a criação da comunidade com o investimento inicial de 300 soaps – Usuário.

5 – Valida o preenchimento dos campos obrigatórios, o formato e a disponibilidade do identificador, a suficiência de saldo e as restrições de formato e tamanho da imagem (caso anexada) – Sistema.

6 – Debita 300 soaps da carteira do usuário e os transfere para a carteira da nova comunidade, registra a nova comunidade (bolha temática), eleva o usuário ao papel de Líder de Comunidade e exibe a página da nova comunidade – Sistema.

**Cenários Alternativos:**

2.1 – Caso o usuário possua saldo inferior a 300 soaps em sua carteira, a situação de saldo insuficiente deve ser informada ao usuário, com o valor que falta, e o fluxo de criação é encerrado sem abrir o formulário – Sistema.

4.1 – Caso o usuário opte por não informar descrição, diretrizes ou imagem, o fluxo prossegue normalmente – Usuário.

5.1 – Caso o nome ou o identificador não tenham sido preenchidos, o identificador não respeite o formato aceito (3 a 21 caracteres: letras minúsculas, números e sublinhado) ou já esteja em uso por outra comunidade, a inconsistência deve ser informada ao usuário e solicitada a devida correção antes de efetivar a criação – Sistema.

5.2 – Caso o arquivo de imagem anexado como ícone não esteja nos formatos aceitos (JPEG, PNG, WebP ou GIF) ou ultrapasse o tamanho máximo de 10 MB, a invalidade do arquivo deve ser informada ao usuário e solicitado o envio de uma imagem válida ou a remoção do anexo – Sistema.

**Analista de Negócios:** Augusto Cesar Dalal Miranda, Luís Fernando dos Santos Favoreto

**Requisitos Associados:** [RF003], [NF007], [NF010]

**Data:** 18/11/2026

**Versão:** 1.1

**Telas/rotas relacionadas:**
- `/communities`: lista de comunidades, com o botão "Criar comunidade", que abre o formulário de criação ou, sem saldo suficiente, exibe o aviso do cenário 2.1 (passos 1 a 5 e cenários 2.1, 4.1, 5.1 e 5.2).
- `/c/:commname`: página da comunidade criada (passo 6).

---

## UC005 – Publicar no perfil pessoal

**Breve Descritivo:** Este caso de uso descreve o processo de criação de uma nova publicação no perfil de um usuário, que pode ser permanente (bubblegram) ou temporária (bubblepop), debitando o custo correspondente em soap.

**Pré-condições:** Usuário autenticado no sistema informa sua intenção de criar uma nova publicação.

**Atores:** Usuário, Sistema.

**Cenários Principais:**

1 – Solicita a opção de criação de uma nova publicação para seu perfil pessoal – Usuário.

2 – Exibe o editor de publicação, o saldo atual de soap da carteira do usuário e o custo da publicação – Sistema.

3 – Preenche o texto da publicação – Usuário.

4 – Anexa opcionalmente uma imagem (formatos JPEG, PNG, WebP ou GIF, com tamanho máximo de 10 MB) – Usuário.

5 – Confirma o envio da publicação como permanente – Usuário.

6 – Valida o preenchimento do texto (obrigatório quando não há imagem), as restrições da imagem (caso anexada) e a suficiência de saldo na carteira do usuário – Sistema.

7 – Debita o custo de 10 soaps da carteira do usuário, registra a publicação vinculada à bolha pessoal, disponibiliza a publicação no feed de atualizações dos seguidores e a exibe no perfil pessoal – Sistema.

**Cenários Alternativos:**

4.1 – Caso o usuário opte por não anexar uma imagem, o fluxo prossegue normalmente com uma publicação apenas de texto – Usuário.

5.1 – Caso o usuário opte pela publicação temporária (bubblepop), deve informar uma imagem, uma descrição opcional e a duração de 1 a 48 horas; o custo passa a ser de 1 soap a cada 4 horas de duração, arredondado para cima, e o bubblepop fica disponível na bandeja do feed dos seguidores e no perfil até expirar, quando o sistema o remove – Usuário, Sistema.

6.1 – Caso o texto não tenha sido preenchido (publicação sem imagem) ou o usuário possua saldo de soap insuficiente para cobrir o custo, a inconsistência ou falta de saldo deve ser informada ao usuário e solicitada a correção dos dados antes de efetivar a publicação – Sistema.

6.2 – Caso o arquivo de imagem anexado não esteja nos formatos aceitos (JPEG, PNG, WebP ou GIF) ou ultrapasse o tamanho limite de 10 MB, a invalidade do arquivo deve ser informada ao usuário e solicitado o envio de uma imagem válida ou a remoção do anexo – Sistema.

6.3 – Caso a conta do usuário esteja suspensa, a publicação é recusada e o usuário é informado da situação – Sistema.

**Analista de Negócios:** Augusto Cesar Dalal Miranda, Luís Fernando dos Santos Favoreto

**Requisitos Associados:** [RF005], [RF009], [NF007], [NF008], [NF010]

**Data:** 18/11/2026

**Versão:** 1.1

**Telas/rotas relacionadas:**
- `/`: feed, com o botão "+" no canto inferior direito, que abre o painel de publicação com as abas Texto, Foto (publicação permanente) e Bubblepop (cenário 5.1).
- `/u/:username`: perfil do próprio usuário, com o mesmo botão "+"; a publicação aparece no mural e o bubblepop, na área de bubblepops.
