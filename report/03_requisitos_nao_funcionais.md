# 4 Requisitos Não-Funcionais

Esta seção apresenta os requisitos não-funcionais do sistema em detalhes. Todos os requisitos não-funcionais aqui apresentados são essenciais para o bom funcionamento do sistema.

## Performance

*[REVISAR] [NF001] Tempo de resposta*

O sistema deve manter o tempo de resposta de 95% das requisições de leitura de dados em no máximo 02 segundos, e das operações de gravação em até 03 segundos.

Casos de uso associados:

*[REVISAR] [NF002] Taxa de Falhas*

O sistema deve manter uma taxa de erros internos do servidor inferior a 0,1% do total de requisições diárias.

Casos de uso associados:

## Usabilidade

*[NF003] Design Responsivo*

A interface deve ser responsiva, adaptando-se automaticamente a diferentes tamanhos de tela, de celulares a computadores desktop.

Casos de uso associados:

*[NF004] Interface gráfica com o usuário*

A interface deve ser intuitiva, com funções facilmente entendíveis por usuários que não possuem muita experiência com outras redes sociais.

Casos de uso associados:

*[REVISAR] [NF005] Função de ajuda*

O sistema deve disponibilizar uma seção de ajuda acessível em todas as telas, para esclarecer eventuais dúvidas dos usuários.

Casos de uso associados:

## Confiabilidade

*[REVISAR] [NF006] Disponibilidade*

O sistema deve apresentar uma taxa de disponibilidade de no mínimo 99,5% ao mês, excluindo janelas de manutenção programadas.

Casos de uso associados:

*[NF007] Consistência dos dados*

O sistema deve retornar para um estado anterior consistente, revertendo operações incompletas, caso ocorra algum erro no processamento de uma transação, evitando comprometimento da coerência dos dados armazenados. As movimentações de soap devem ser registradas em um histórico que não pode ser alterado.

Casos de uso associados: UC003, UC005

## Segurança e privacidade

*[NF008] Autenticação e Controle de Acesso*

O sistema deve exigir autenticação via nome de usuário (ou e-mail) e senha para garantir o acesso a funcionalidades restritas a cada usuário, mantendo a sessão por meio de tokens de curta duração. As senhas devem ser armazenadas utilizando algoritmos de hash seguros e as tentativas de login devem ter limite de frequência.

Casos de uso associados: UC005

*[NF009] Proteção de Dados Pessoais*

O sistema deve garantir a privacidade dos dados dos usuários, através de um mecanismo de acesso autorizado (e-mail, data de nascimento e saldo de soap ficam visíveis apenas ao próprio usuário), também permitindo ao usuário excluir sua conta, o que anonimiza seus dados pessoais e mantém o histórico de soap sem identificação.

Casos de uso associados:

## Armazenamento e Mídia

*[NF010] Processamento de Mídia*

O sistema deve permitir o upload de imagens nos formatos JPEG, PNG, WebP e GIF, com tamanho máximo de 10 MB por arquivo e uma imagem por publicação. O sistema deve validar o conteúdo real do arquivo, rejeitando os que não forem imagens válidas.

Casos de uso associados: UC003, UC005

## Arquitetura e Requisitos Tecnológicos

*[REVISAR] [NF011] Compatibilidade de Clientes*

A aplicação web deve ser compatível com as versões recentes dos principais navegadores do mercado (Google Chrome, Mozilla Firefox, Microsoft Edge e Safari).

Casos de uso associados:

*[NF012] Ambiente Operacional*

O sistema será desenvolvido utilizando as linguagens Python e TypeScript. No backend, será empregado o framework Django 5.2 com Django REST Framework, enquanto o frontend será construído com React 18, Vite e Tailwind CSS. O gerenciamento e o armazenamento de dados serão realizados através do sistema gerenciador de banco de dados PostgreSQL 17.

Casos de uso associados:
