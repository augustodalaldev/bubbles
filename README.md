# Bubbles 🫧

Rede social baseada em comunidades, em que as interações são feitas com uma moeda virtual chamada **soap**.
Projeto final da disciplina de APSOO (UFMS).

- **Backend:** Django 5.2, Django REST Framework e PostgreSQL, em `backend/` (Python 3.12+, gerenciado com `uv`).
- **Frontend:** React, TypeScript, Vite e Tailwind, em `frontend/`.

## Como o sistema funciona

### Soap

O soap é a única moeda do sistema e também a única forma de reagir a uma publicação: não há curtidas. Cada usuário
recebe 20 soaps ao criar a conta e ganha mais com o uso (5 soaps a cada 5 minutos de atividade, até 15 por dia).
O saldo é gasto em publicar, apoiar, criar bubblepops, fundar comunidades (300 soaps) e comprar itens de customização.
Ao apoiar uma publicação, 1 soap sai do saldo de quem apoia e vai para o autor e, no caso de posts de comunidade,
também para a comunidade. Todos esses valores ficam em uma tabela de configuração e podem ser alterados pela administração.

### Funcionalidades

- **Bubblegrams:** publicações de texto ou foto, feitas no perfil ou em uma comunidade, com comentários e respostas.
- **Bubblepops:** fotos temporárias. O custo em soap depende de quanto tempo ficam no ar.
- **Comunidades:** têm líder, administradores e membros, além de diretrizes próprias, foto e banner.
- **Cartas:** mensagens privadas, que só podem ser enviadas a usuários que você segue. Cada carta aceita uma única resposta.
- **Loja:** molduras, temas, selos, cor do nome, papéis de parede, cor de destaque e seção de perfil, todos comprados com soap.
- **Feed:** em ordem cronológica, com algumas sugestões identificadas como tal. Não há recomendação por IA.
- **Moderação:** suspensão e banimento de usuários e comunidades, denúncias e histórico de auditoria, pela tela `/moderation`
  (apenas staff) e pelo Django Admin.

### Organização do código

O backend é dividido em camadas: models, selectors, services, serializers e views. As regras de negócio ficam nos
services. Todo movimento de soap passa por `economy.services`, que trava as carteiras envolvidas e registra a
movimentação no extrato. Os erros da API seguem sempre o mesmo formato (`{"error": {"code", "message", ...}}`) e o
frontend monta a mensagem a partir do `code`. Contas e comunidades excluídas são anonimizadas em vez de apagadas, para
que o conteúdo de outros usuários continue existindo.

## Como rodar

É preciso ter Docker (para o PostgreSQL), `uv` e Node instalados.

```bash
cp .env.example .env      # defina o DJANGO_SECRET_KEY
make up                   # PostgreSQL no Docker
cd backend && uv sync && uv run python manage.py migrate && cd ..
make run                  # API em http://localhost:8000/api/docs/

cd frontend && npm install && cd ..
make frontend-dev         # app em http://localhost:5173
```

Para acessar o Django Admin (`/admin/`), onde ficam o catálogo da loja e a moderação, crie um usuário staff com
`cd backend && uv run python manage.py createsuperuser`.

Outros comandos: `make test`, `make lint`, `make format`, `make check-migrations` e `make frontend-build`.

## Como rodar a demonstração

A demonstração usa um banco separado (`bubbles_teste`, nunca o de desenvolvimento), já populado com usuários, posts e
comunidades. Com o `.env` criado e o `make up` em execução:

```bash
make demo             # cria o banco, aplica as migrations, popula e sobe o backend em :8001
make demo-frontend    # em outro terminal: sobe o frontend apontando para o backend da demo
```

Depois é só abrir http://localhost:5173. O `make demo` mostra as contas no terminal, e todas usam a senha `DemoPets2026!`:

| Usuário | Perfil |
|---|---|
| `admin_demo` | staff; acessa o `/admin/` e a tela `/moderation` |
| `moderador_demo` | administrador de várias comunidades |
| `suspenso_demo` e `banido_demo` | contas suspensa e banida, para ver como o sistema reage |
| demais usuários | usuários comuns, com posts, cartas e compras |

Para refazer a demo do zero, use `make demo-reset`.

### O que a demonstração contém

São 16 usuários, cada um com nome, bio, foto de perfil, pets e um jeito próprio de escrever. Os temas são cachorros e
gatos. Há cerca de 135 posts, perguntas com respostas nos comentários, conversas por carta, bubblepops, 8 comunidades,
itens comprados na loja, denúncias e exemplos de moderação (conta suspensa, banida e excluída; comunidade suspensa,
banida e excluída). Os dados são criados pelos próprios services da aplicação, então saldos, contadores e extrato de
soap seguem as regras reais.

- As fotos de cachorro e gato vêm da Dog CEO e da The Cat API, que são gratuitas e não exigem chave. São baixadas uma vez
  para `backend/.demo_cache/` (fora do git) e reutilizadas. Sem internet, a demo usa o cache ou ignora as imagens.
- As fotos de perfil ficam em `backend/.demo_cache/avatars/` e também não são versionadas, porque as imagens pertencem
  aos seus donos. Se algum arquivo estiver faltando, o sistema gera uma arte no lugar.
- Rodar `make demo` novamente não duplica os dados. O comando `seed_demo --reset` remove somente o que a demo criou.
- Nunca execute o `pytest` com o `DJANGO_SETTINGS_MODULE` da demo, porque os testes apagariam o `backend/media/` dela.
  O `make test` já usa as configurações corretas.

As opções do comando (`--users`, `--communities`, `--no-images` etc.) estão em
`backend/apps/core/management/commands/seed_demo.py`.

## Agendador

O pagamento de soap por tempo de uso e a limpeza de bubblepops expirados são feitos por um agendador simples, sem
Celery nem Redis:

```bash
make scheduler        # roda continuamente (Ctrl+C para parar)
make scheduler-once   # executa cada tarefa uma vez e encerra
make demo-scheduler   # o mesmo, usando o banco da demo
```

Sem o agendador o sistema funciona, mas os usuários não recebem o soap passivo. É seguro rodar mais de uma instância,
porque as tarefas usam lock do PostgreSQL e não pagam duas vezes.

## Produção

O frontend é uma SPA, então o servidor que entregar o `frontend/dist` precisa responder com o `index.html` para
qualquer caminho que não seja um arquivo. Caso contrário, recarregar uma página como `/c/alguma_comunidade` retorna 404.
Exemplo para nginx:

```nginx
location / { root /var/www/bubbles; try_files $uri /index.html; }
location /api/ { proxy_pass http://127.0.0.1:8000; }
location /media/ { proxy_pass http://127.0.0.1:8000; }
```

## Documentação

Na pasta `docs/`: `DECISIONS.md` (decisões de projeto), `PROGRESS.md`, `ER.md` (modelo de dados),
`REQUIREMENTS_CHANGES.md` e `frontend/PLAN.md`. Os documentos do relatório (requisitos, casos de uso e diagramas de
classes) estão em `report/`.
