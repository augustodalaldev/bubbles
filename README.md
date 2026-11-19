# Bubbles 🫧

Uma rede social de comunidades onde ninguém curte nada: quem quer apoiar alguém paga em **soap** (sabão).
Trabalho final de APSOO (UFMS).

- **Backend:** Django 5.2 + DRF + PostgreSQL, em `backend/` (Python 3.12+, gerenciado com `uv`).
- **Frontend:** React + TypeScript + Vite + Tailwind, em `frontend/`.

## Como o sistema funciona

A ideia é uma rede pequena e calma, com cara de web dos anos 2000 (Orkut), sem algoritmo decidindo o que você vê.

**Soap é a única moeda e a única forma de reação.** Não existe curtida nem coração. Você ganha 20 soaps ao criar a
conta, mais um pouco por usar o sistema (5 a cada 5 minutos de uso, até 15 por dia), e gasta quando faz algo que
custa: publicar, apoiar, criar um bubblepop, fundar uma comunidade (300), comprar customização. Quando você apoia
uma publicação, 1 soap sai do seu saldo e vai para o autor (e para a comunidade, se for um post de comunidade).
Todos os valores ficam em uma tabela de configuração e podem ser mudados pela administração.

**O que dá para fazer:**
- **Bubblegrams:** as publicações (texto ou foto), no seu perfil ou dentro de uma comunidade. Têm comentários e respostas.
- **Bubblepops:** fotos temporárias, tipo stories. Quanto mais tempo no ar, mais soap custa.
- **Comunidades:** têm líder, administradores e membros, diretrizes próprias e regras de entrada e saída.
- **Cartas:** mensagens privadas, só para quem você segue, e cada carta só pode ser respondida uma vez.
- **Loja:** molduras, temas, selos, cor do nome, papéis de parede e seção de perfil. Tudo comprado com soap.
- **Feed:** cronológico, com algumas sugestões marcadas como sugestão. Nada de recomendação por IA.
- **Moderação:** suspensão, banimento e denúncias, com histórico de auditoria. Fica na tela `/moderation` (só staff)
  e no Django Admin.

**Como o código está organizado.** O backend é em camadas (models, selectors, services, serializers, views). A regra de
negócio mora nos services, e soap só se mexe por `economy.services`, que trava as carteiras em ordem e registra
cada movimentação em um extrato. Os erros da API sempre saem no mesmo formato (`{"error": {"code", "message", ...}}`)
e o frontend traduz pelo `code`. Contas e comunidades excluídas são anonimizadas em vez de apagadas, para o conteúdo
dos outros não sumir junto.

## Rodando

Precisa de Docker (para o PostgreSQL), `uv` e Node.

```bash
cp .env.example .env      # defina o DJANGO_SECRET_KEY
make up                   # PostgreSQL no Docker
cd backend && uv sync && uv run python manage.py migrate && cd ..
make run                  # API em http://localhost:8000/api/docs/

cd frontend && npm install && cd ..
make frontend-dev         # app em http://localhost:5173
```

Para usar o Django Admin (`/admin/`), onde ficam o catálogo da loja e a moderação, crie um usuário staff:
`cd backend && uv run python manage.py createsuperuser`.

Outros comandos: `make test` · `make lint` · `make format` · `make check-migrations` · `make frontend-build`.

## Rodando a demonstração

A demo usa um banco separado (`bubbles_teste`, nunca o de desenvolvimento) já cheio de gente, posts e comunidades,
para dar para explorar o sistema sem montar tudo na mão. Com o `.env` criado e o `make up` rodando:

```bash
make demo             # cria o banco, migra, popula e sobe o backend em :8001
make demo-frontend    # em outro terminal: frontend apontando para o backend da demo
```

Depois é só abrir http://localhost:5173. O `make demo` imprime as contas, e todas usam a senha `DemoPets2026!`:

| Usuário | Para quê |
|---|---|
| `admin_demo` | staff: abre o `/admin/` e a tela `/moderation` |
| `moderador_demo` | administra várias comunidades |
| `suspenso_demo` / `banido_demo` | ver como ficam uma conta suspensa e uma banida |
| os demais | usuários comuns, com pets, posts, cartas e compras |

Se quiser recomeçar do zero: `make demo-reset`.

**O que a demo cria.** 16 pessoas que parecem vizinhos de verdade (cada nome tem uma piscadela para um personagem de
desenho, com o personagem como foto de perfil), todas falando dos próprios cachorros e gatos. São cerca de 135 posts
escritos à mão, threads de dúvidas com respostas, cartas, bubblepops, 8 comunidades, itens da loja com compras feitas,
denúncias e alguns estados de moderação (conta suspensa, banida e excluída; comunidade suspensa, banida e excluída).
Tudo é criado pelos próprios services da aplicação, então saldo, contadores e extrato de soap são reais.

Detalhes que vale saber:
- As fotos de cachorro e gato vêm da Dog CEO e da The Cat API (grátis, sem chave). Elas são baixadas uma vez para
  `backend/.demo_cache/` (fora do git) e reaproveitadas. Sem internet, a demo usa o cache ou pula as imagens.
- As fotos de perfil dos personagens ficam em `backend/.demo_cache/avatars/` e não vão para o git, porque as imagens
  pertencem aos donos. Se algum arquivo faltar, entra uma arte gerada no lugar.
- Rodar `make demo` de novo não duplica nada. O `seed_demo --reset` apaga só o que a própria demo criou.
- **Nunca rode o `pytest` com o `DJANGO_SETTINGS_MODULE` da demo**, porque os testes apagariam o `backend/media/` dela.
  O `make test` já usa as configurações certas.

As opções do comando (`--users`, `--communities`, `--no-images` etc.) estão em `backend/apps/core/management/commands/seed_demo.py`.

## Ganho passivo de soap

O soap por tempo de uso e a limpeza de bubblepops vencidos rodam por um agendador simples, sem Celery nem Redis:

```bash
make scheduler        # fica rodando; Ctrl+C para parar
make scheduler-once   # roda cada tarefa uma vez e sai
make demo-scheduler   # o mesmo, contra o banco da demo
```

Sem ele nada quebra, mas ninguém recebe o soap passivo. Dá para rodar duas instâncias ao mesmo tempo sem pagar em dobro,
porque as tarefas usam lock do PostgreSQL.

## Em produção

O frontend é uma SPA: quem servir o `frontend/dist` precisa devolver o `index.html` para qualquer caminho que não seja
arquivo, senão recarregar `/c/alguma_comunidade` dá 404. No nginx:

```nginx
location / { root /var/www/bubbles; try_files $uri /index.html; }
location /api/ { proxy_pass http://127.0.0.1:8000; }
location /media/ { proxy_pass http://127.0.0.1:8000; }
```

## Mais documentação

Em `docs/`: `DECISIONS.md` (por que cada coisa é do jeito que é), `PROGRESS.md`, `ER.md` (modelo de dados),
`REQUIREMENTS_CHANGES.md` e `frontend/PLAN.md`. O material do relatório (requisitos, casos de uso e diagramas de classes)
está em `report/`.
