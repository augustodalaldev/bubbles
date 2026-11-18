# Plano "polish 2" (branch `feature/polish-2`)

Lote de pendências encontradas nos testes manuais. Cada fase termina com pytest, `manage.py check`,
`makemigrations --check`, ruff, build do frontend, validação em navegador real (375/768/1280 px, URL, voltar, F5)
e um commit.

## Itens
A (cadastro): 1 mostrar/ocultar senha · 2 sem descrição no cadastro · 3 mensagens em português.
B (conta/comunidade): 4 editar/excluir conta · 5 editar/excluir comunidade · 6 suspender/banir perfis e comunidades.
C (social): 7 listas de seguidores/seguindo · 8 carta-resposta com link para a original.
D (layout): 9 imagens sumindo no celular · 10 botão "+" no perfil · 11 customização aplicada nos perfis.
E (personalização): 12 wallpapers, cor dos elementos, seção personalizável e selos · 13 efeito de bolha no mural.

## Fases
1. Correções rápidas: 1, 2, 3, 9, 10, 11 (+ nome "Conta excluída", throttle próprio do refresh, mural responsivo, rolagem natural no celular).
2. Social e cartas: 7 e 8, com URLs próprias.
3. Editar e excluir conta e comunidade: 4 e 5 (migration: `Community.deleted_at`).
4. Administração: 6 (migration: `Community.suspended_until`; tela `/moderacao`).
5. Personalização expandida e efeito de bolha: 12 e 13 (migration: `CustomizationItem.image` e novos tipos).
6. Validação final, seed de demonstração e documentação.

Status: todas as 6 fases concluídas (ver `docs/PROGRESS.md`, bloco "Batch 3").

## Decisões aprovadas
- D1 exclusão de conta: lógica com anonimização; conteúdo permanece como "Conta excluída"; bubblepops, foto, vínculos e participações removidos; soap perdido com aviso; líder precisa transferir a liderança ou excluir a comunidade antes; exige senha e digitar "EXCLUIR".
- D2 exclusão de comunidade: só o líder, digitando o nome; exclusão lógica (some de tudo, URL 404, membros removidos); carteira e itens perdidos, com aviso.
- D3 suspensão (temporária, com fim e motivo) vs. banimento (permanente até restaurar) para usuários e comunidades; auditoria e motivo visível ao afetado.
- D4 a descrição do perfil continua editável na edição de perfil.
- D5 wallpapers: apenas a equipe envia (catálogo), usuários compram com soap.
- D6 cor dos elementos: presets do catálogo com cor hex validada.
- D7 "perfil privado" = o próprio perfil; customização aplicada em todos os perfis.
- D8 selos: compra ou concessão pela equipe (Django Admin); até 3 visíveis.
- D9 seção personalizável: item `SECTION` comprado libera título e texto puro.
- D10 efeito de bolha: filtro visual que dá aspecto de bolha à foto do post no mural do perfil.
- D11 troca de senha e e-mail entram (com senha atual); username é imutável.
- D12 transferir liderança na tela da comunidade.
- Demo: duas a três variações de cada nova opção de personalização.
