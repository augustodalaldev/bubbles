"""User-facing error messages in Brazilian Portuguese, keyed by the API's stable error codes.

The services keep raising `DomainError` with English messages (useful in logs and tests); the
exception handler replaces them with the text below, so the UI never depends on translating
messages one by one in the frontend. Messages may use the error's extra fields as `{placeholders}`.

Codes whose message is already localized by Django/DRF (password validators, throttling, ...)
are listed in PASSTHROUGH and keep the text that came with the exception.
"""

from typing import Any

MESSAGES: dict[str, str] = {
    # --- generic / transport
    "domain_error": "Não foi possível concluir a operação.",
    "api_error": "Ocorreu um erro. Tente novamente.",
    "validation_error": "Confira os campos destacados.",
    "not_found": "Não encontrado.",
    "permission_denied": "Você não tem permissão para fazer isso.",
    "conflict": "Esta operação conflita com dados já existentes.",
    "server_error": "Erro interno do servidor. Tente novamente em instantes.",
    "not_authenticated": "Entre na sua conta para continuar.",
    "token_invalid": "Sua sessão expirou. Entre novamente.",
    "token_not_valid": "Sua sessão expirou. Entre novamente.",
    "token_missing": "Sessão não encontrada. Entre novamente.",
    "invalid_credentials": "Usuário ou senha incorretos.",
    "invalid_input": "Dados inválidos.",
    "invalid_type": "Tipo inválido.",
    "invalid_status": "Status inválido.",
    "invalid_state": "Estado de membro inválido.",
    "invalid_duration": "Duração inválida: confira o limite permitido.",
    "invalid_amount": "O valor do ajuste deve ser um número inteiro diferente de zero.",
    "self_action": "Você não pode fazer isso com a sua própria conta.",
    # --- accounts
    "account_suspended": "Sua conta está suspensa e não pode realizar esta ação.",
    "user_not_found": "Usuário não encontrado.",
    "user_inactive": "Esta conta não está ativa.",
    "already_following": "Você já segue esta pessoa.",
    "cannot_follow_self": "Você não pode seguir a si mesmo.",
    "username_already_registered": "Este nome de usuário não está disponível.",
    "email_already_registered": "Este e-mail já está em uso.",
    "invalid_username": "Use de 3 a 30 caracteres: letras minúsculas, números e sublinhado.",
    "reserved_username": "Este nome de usuário não está disponível.",
    "future_birth_date": "A data de nascimento não pode estar no futuro.",
    "underage": "É necessário ter pelo menos 14 anos.",
    "invalid_birth_date": "Data de nascimento inválida.",
    "invalid_password": "Senha incorreta.",
    "invalid_name": "Nome inválido: use um nome dentro do limite de caracteres.",
    "invalid_description": "A descrição ultrapassa o limite de caracteres.",
    "description_too_long": "A descrição ultrapassa o limite de caracteres.",
    "must_transfer_leadership": (
        "Transfira a liderança das suas comunidades antes de continuar: {communities}."
    ),
    # --- communities
    "community_not_found": "Comunidade não encontrada.",
    "commname_already_registered": "Este identificador de comunidade não está disponível.",
    "invalid_commname": "Use de 3 a 21 caracteres: letras minúsculas, números e sublinhado.",
    "reserved_commname": "Este identificador de comunidade não está disponível.",
    "invalid_guidelines": "As diretrizes ultrapassam o limite de 2000 caracteres.",
    "community_archived": "Esta comunidade foi arquivada e está somente para leitura.",
    "community_blocked": "Esta comunidade está bloqueada pela administração.",
    "confirmation_mismatch": "O texto digitado não confere. Confira e tente de novo.",
    "already_archived": "Esta comunidade já está arquivada.",
    "already_member": "Você já participa desta comunidade.",
    "not_member": "Você não participa desta comunidade.",
    "banned_from_community": "Você foi banido desta comunidade.",
    "member_banned": "Você foi banido desta comunidade e não pode sair.",
    "member_not_found": "Membro não encontrado nesta comunidade.",
    "member_not_active": "Só membros ativos podem receber esta função.",
    "leader_cannot_leave": (
        "A liderança não pode sair da comunidade. Transfira a liderança ou arquive a comunidade."
    ),
    "leader_must_be_active": "A pessoa líder deve permanecer ativa e não pode ser moderada.",
    "already_leader": "Esta pessoa já é a líder da comunidade.",
    "cannot_moderate_self": "Você não pode moderar a sua própria participação.",
    "invalid_promotion": "Só membros comuns podem ser promovidos a administrador.",
    "invalid_demotion": "Só administradores da comunidade podem ser rebaixados.",
    # --- content
    "post_not_found": "Publicação não encontrada.",
    "bubblegram_not_found": "Publicação não encontrada.",
    "bubblepop_not_found": "Bubblepop não encontrado.",
    "comment_not_found": "Comentário não encontrado.",
    "invalid_parent": "O comentário respondido deve pertencer à mesma publicação.",
    "text_required": "O texto é obrigatório.",
    "text_too_long": "O texto ultrapassa o limite de caracteres.",
    "media_not_allowed": "Publicações de texto não podem ter imagens.",
    "media_required": "Publicações com mídia precisam de ao menos 1 imagem.",
    "too_many_media": "Cada publicação aceita no máximo 4 imagens.",
    "image_required": "Envie uma imagem.",
    "image_too_large": "A imagem deve ter no máximo 10 MB.",
    "invalid_image": "Envie uma imagem válida.",
    "invalid_image_type": "Use imagens JPEG, PNG, WebP ou GIF.",
    "already_supported": "Você já apoiou este conteúdo.",
    "self_support_not_allowed": "Você não pode apoiar o seu próprio conteúdo.",
    # --- letters
    "letter_not_found": "Carta não encontrada.",
    "not_following": "Você precisa seguir esta pessoa para enviar uma carta.",
    "cannot_letter_self": "Você não pode enviar uma carta para si mesmo.",
    "already_replied": "Esta carta já foi respondida.",
    "invalid_reply_recipient": "A resposta deve ser enviada ao autor da carta original.",
    # --- economy / customization
    "insufficient_soap": (
        "Saldo de soap insuficiente: são necessários {cost} soap e você tem {balance}."
    ),
    "already_owned": "Este item já foi adquirido.",
    "item_not_found": "Item não encontrado.",
    "item_not_owned": "Você não possui este item.",
    "item_inactive": "Este item não está disponível para compra.",
    "item_scope_mismatch": "Este item não pode ser comprado aqui.",
    "slot_conflict": "Só é possível equipar um item por tipo.",
    "slot_mismatch": "Este item não corresponde ao espaço escolhido.",
    "invalid_customization": "Os dados de personalização são inválidos.",
    "customization_not_available": "A personalização desta comunidade ainda não está disponível.",
    # --- moderation
    "cannot_ban_staff": "Administradores não podem ser banidos.",
    "cannot_suspend_staff": "Administradores não podem ser suspensos.",
    "self_report": "Você não pode denunciar a si mesmo.",
    "invalid_content_id": "O identificador do conteúdo deve ser um número.",
    "invalid_target_id": "O identificador do alvo deve ser um número.",
    "invalid_target_type": "Tipo de alvo inválido.",
}

# Messages Django/DRF already produce in the active language (password validators, ...).
PASSTHROUGH = {"weak_password"}


class _Missing(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def message_for(code: str, default: str = "", extra: dict[str, Any] | None = None) -> str:
    """The pt-BR message for `code`; `default` when the code is not in the catalog."""
    template = MESSAGES.get(code)
    if template is None:
        return default
    values = dict(extra or {})
    communities = values.get("communities")
    if isinstance(communities, list | tuple):
        values["communities"] = ", ".join(str(c) for c in communities)
    return template.format_map(_Missing(values))
