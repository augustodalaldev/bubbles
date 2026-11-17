import axios from "axios";

/** Error envelope returned by every failing API call: {"error": {code, message, fields, ...extras}}. */
export interface ApiErrorBody {
  code: string;
  message: string;
  fields: Record<string, string[]> | null;
  [extra: string]: unknown;
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly fields: Record<string, string[]>;
  readonly extra: Record<string, unknown>;

  constructor(status: number, body: ApiErrorBody) {
    super(body.message);
    this.status = status;
    this.code = body.code;
    this.fields = body.fields ?? {};
    const { code: _code, message: _message, fields: _fields, ...extra } = body;
    this.extra = extra;
  }
}

/** Turns anything thrown by axios into an ApiError (network failures get code "network_error"). */
export function toApiError(err: unknown): ApiError {
  if (err instanceof ApiError) return err;
  if (axios.isAxiosError(err)) {
    const body = err.response?.data?.error as ApiErrorBody | undefined;
    if (body && typeof body.code === "string") return new ApiError(err.response!.status, body);
    if (!err.response) {
      return new ApiError(0, { code: "network_error", message: "Network error", fields: null });
    }
    return new ApiError(err.response.status, {
      code: "server_error",
      message: "Server error",
      fields: null,
    });
  }
  return new ApiError(0, { code: "unknown_error", message: String(err), fields: null });
}

/** User-facing copy (pt-BR), keyed by the stable error codes of the API. */
const MESSAGES: Record<string, string> = {
  network_error: "Não foi possível conectar ao servidor. Verifique sua conexão.",
  server_error: "Erro no servidor. Tente novamente em instantes.",
  unknown_error: "Algo deu errado. Tente novamente.",
  not_authenticated: "Sua sessão expirou. Entre novamente.",
  token_invalid: "Sua sessão expirou. Entre novamente.",
  token_not_valid: "Sua sessão expirou. Entre novamente.",
  invalid_credentials: "Usuário ou senha incorretos.",
  throttled: "Muitas tentativas. Aguarde um pouco e tente de novo.",
  permission_denied: "Você não tem permissão para fazer isso.",
  not_found: "Não encontrado.",
  validation_error: "Confira os campos destacados.",
  account_suspended: "Sua conta está suspensa e não pode realizar esta ação.",
  already_supported: "Você já apoiou este conteúdo.",
  self_support_not_allowed: "Você não pode apoiar o seu próprio conteúdo.",
  community_blocked: "Esta comunidade está bloqueada.",
  community_archived: "Esta comunidade foi arquivada e está somente para leitura.",
  member_banned: "Você foi banido desta comunidade.",
  not_following: "Você precisa seguir esta pessoa para enviar uma carta.",
  already_replied: "Esta carta já foi respondida.",
  already_owned: "Você já possui este item.",
  item_inactive: "Este item não está disponível.",
  image_too_large: "A imagem deve ter no máximo 10 MB.",
  invalid_image: "Envie uma imagem válida.",
  invalid_image_type: "Use imagens JPEG, PNG, WebP ou GIF.",
  invalid_duration: "Duração inválida para o bubblepop.",
  customization_not_available: "A customização de comunidades ainda não está disponível.",
  must_transfer_leadership: "Transfira a liderança das suas comunidades antes de continuar.",
};

export function errorMessage(err: unknown): string {
  const error = toApiError(err);
  if (error.code === "insufficient_soap") {
    const cost = Number(error.extra.cost);
    const balance = Number(error.extra.balance);
    if (Number.isFinite(cost) && Number.isFinite(balance)) {
      return `Saldo insuficiente: são necessários ${cost} soap e você tem ${balance}.`;
    }
    return "Saldo de soap insuficiente.";
  }
  if (error.code === "validation_error") {
    const first = Object.values(error.fields)[0]?.[0];
    if (first) return first;
  }
  return MESSAGES[error.code] ?? error.message ?? MESSAGES.unknown_error;
}

/** First message per field, for showing next to inputs. */
export function fieldErrors(err: unknown): Record<string, string> {
  const result: Record<string, string> = {};
  for (const [field, messages] of Object.entries(toApiError(err).fields)) {
    if (messages[0]) result[field] = messages[0];
  }
  return result;
}
