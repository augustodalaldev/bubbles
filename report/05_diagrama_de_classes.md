# 7 Diagrama de Classes

Os diagramas abaixo foram gerados a partir dos models do sistema (Django). Para manter a leitura simples, há um diagrama geral, só com as classes e suas relações, e quatro diagramas por domínio, com os atributos principais. Foram omitidos campos técnicos (chaves de idempotência, ativação interna da conta, grupos e permissões do framework). Os nomes das classes e dos atributos seguem o código.

## 7.1 Diagrama geral

```mermaid
classDiagram
    direction TB

    User "1" -- "0..*" UserConnection : segue
    User "1" -- "0..*" UserConnection : é seguido
    User "1" -- "0..*" CommunityMember : participa
    Community "1" -- "1..*" CommunityMember : possui

    User "1" -- "0..*" Bubblegram : publica
    Community "0..1" -- "0..*" Bubblegram : contém
    Bubblegram "1" *-- "0..1" BubblegramMedia : tem imagens
    User "1" -- "0..*" Bubblepop : publica
    Bubblegram "1" -- "0..*" Comment : recebe
    User "1" -- "0..*" Comment : escreve
    Comment "0..1" -- "0..*" Comment : resposta a

    Bubblegram "1" -- "0..*" BubblegramSupport : recebe apoio
    Comment "1" -- "0..*" CommentSupport : recebe apoio
    User "1" -- "0..*" BubblegramSupport : apoia
    User "1" -- "0..*" CommentSupport : apoia

    User "1" -- "0..*" Letter : envia
    User "1" -- "0..*" Letter : recebe
    Letter "0..1" -- "0..1" Letter : resposta a

    User "0..1" -- "0..1" Wallet : possui
    Community "0..1" -- "0..1" Wallet : possui
    Wallet "1" -- "0..*" SoapTransaction : registra
    BubblegramSupport "0..1" -- "0..*" SoapTransaction : origem
    CommentSupport "0..1" -- "0..*" SoapTransaction : origem
    User "0..1" -- "0..*" EconomySettings : atualiza

    CustomizationItem "1" -- "0..*" UserInventoryItem : item
    User "1" -- "0..*" UserInventoryItem : adquire
    CustomizationItem "1" -- "0..*" CommunityInventoryItem : item
    Community "1" -- "0..*" CommunityInventoryItem : adquire
    User "0..1" -- "0..*" CommunityInventoryItem : comprado por
    SoapTransaction "0..1" -- "0..*" UserInventoryItem : pagamento
    SoapTransaction "0..1" -- "0..*" CommunityInventoryItem : pagamento

    User "1" -- "0..*" Report : denuncia
    User "0..1" -- "0..*" Report : analisa
    User "0..1" -- "0..*" AuditLog : executa
```

## 7.2 Contas e comunidades

```mermaid
classDiagram
    direction LR

    class User {
        +username: String
        +email: String
        +password: String
        +name: String
        +birth_date: Date
        +description: String
        +profile_photo: Image
        +section_title: String
        +section_text: String
        +customization_json: Json
        +status: UserStatus
        +suspended_until: DateTime
        +moderation_reason: String
        +is_staff: Boolean
        +created_at: DateTime
        +last_seen_at: DateTime
        +deleted_at: DateTime
    }

    class UserConnection {
        +created_at: DateTime
    }

    class Community {
        +commname: String
        +name: String
        +description: String
        +guidelines: String
        +community_photo: Image
        +banner_photo: Image
        +customization_json: Json
        +member_count: Integer
        +created_at: DateTime
        +archived_at: DateTime
        +suspended_until: DateTime
        +blocked_at: DateTime
        +deleted_at: DateTime
        +moderation_reason: String
    }

    class CommunityMember {
        +role: MemberRole
        +current_state: MemberState
        +joined_at: DateTime
    }

    class UserStatus {
        <<enumeration>>
        ACTIVE
        SUSPENDED
        BANNED
    }

    class MemberRole {
        <<enumeration>>
        MEMBER
        COMM_ADMIN
        LEADER
    }

    class MemberState {
        <<enumeration>>
        ACTIVE
        SILENCED
        BANNED
    }

    User "1" -- "0..*" UserConnection : follower
    User "1" -- "0..*" UserConnection : followed
    User "1" -- "0..*" CommunityMember : participa
    Community "1" -- "1..*" CommunityMember : possui
    User ..> UserStatus
    CommunityMember ..> MemberRole
    CommunityMember ..> MemberState
```

## 7.3 Conteúdo e cartas

```mermaid
classDiagram
    direction LR

    class User
    class Community

    class Bubblegram {
        +text: String
        +type: BubblegramType
        +soap_count: Integer
        +published_at: DateTime
    }

    class BubblegramMedia {
        +media: Image
        +position: Integer
    }

    class Bubblepop {
        +image: Image
        +description: String
        +created_at: DateTime
        +expires_at: DateTime
    }

    class Comment {
        +text: String
        +soap_count: Integer
        +published_at: DateTime
    }

    class BubblegramSupport {
        +created_at: DateTime
    }

    class CommentSupport {
        +created_at: DateTime
    }

    class Letter {
        +text: String
        +image: Image
        +sent_at: DateTime
        +read_at: DateTime
    }

    class BubblegramType {
        <<enumeration>>
        TEXT
        MEDIA
    }

    User "1" -- "0..*" Bubblegram : publica
    Community "0..1" -- "0..*" Bubblegram : contém
    Bubblegram "1" *-- "0..1" BubblegramMedia : tem imagens
    User "1" -- "0..*" Bubblepop : publica
    Bubblegram "1" -- "0..*" Comment : recebe
    User "1" -- "0..*" Comment : escreve
    Comment "0..1" -- "0..*" Comment : resposta a
    Bubblegram "1" -- "0..*" BubblegramSupport : recebe apoio
    Comment "1" -- "0..*" CommentSupport : recebe apoio
    User "1" -- "0..*" BubblegramSupport : apoia
    User "1" -- "0..*" CommentSupport : apoia
    User "1" -- "0..*" Letter : envia
    User "1" -- "0..*" Letter : recebe
    Letter "0..1" -- "0..1" Letter : resposta a
    Bubblegram ..> BubblegramType
```

## 7.4 Economia e personalização

```mermaid
classDiagram
    direction LR

    class User
    class Community
    class BubblegramSupport
    class CommentSupport

    class EconomySettings {
        +signup_grant: Integer
        +support_cost: Integer
        +author_credit: Integer
        +community_credit: Integer
        +bubblegram_profile_cost: Integer
        +bubblegram_community_cost: Integer
        +bubblepop_hours_per_soap: Integer
        +bubblepop_min_hours: Integer
        +bubblepop_max_hours: Integer
        +founding_cost: Integer
        +default_passive_earn_rate: Integer
        +passive_interval_minutes: Integer
        +passive_daily_cap: Integer
        +updated_at: DateTime
    }

    class Wallet {
        +soap_balance: Integer
        +passive_earn_rate: Integer
        +created_at: DateTime
    }

    class SoapTransaction {
        +amount: Integer
        +action_type: ActionType
        +balance_after: Integer
        +created_at: DateTime
    }

    class CustomizationItem {
        +name: String
        +code: String
        +item_type: CustomizationType
        +scope: CustomizationScope
        +description: String
        +price: Integer
        +metadata: Json
        +image: Image
        +is_active: Boolean
    }

    class UserInventoryItem {
        +acquired_at: DateTime
    }

    class CommunityInventoryItem {
        +acquired_at: DateTime
    }

    class ActionType {
        <<enumeration>>
        SIGNUP_GRANT
        DEBIT_INTERACTION
        CREDIT_AUTHOR
        CREDIT_COMMUNITY
        PASSIVE_EARN
        DEBIT_FOUNDING
        CREDIT_FOUNDING
        DEBIT_BUBBLEGRAM
        DEBIT_BUBBLEPOP
        SPEND_CUSTOMIZATION
        ADMIN_ADJUSTMENT
    }

    class CustomizationType {
        <<enumeration>>
        AVATAR_FRAME
        PROFILE_THEME
        CHAT_BUBBLE
        BADGE
        NAME_COLOR
        WALLPAPER
        ACCENT_COLOR
        SECTION
    }

    class CustomizationScope {
        <<enumeration>>
        USER
        COMMUNITY
        BOTH
    }

    User "0..1" -- "0..1" Wallet : possui
    Community "0..1" -- "0..1" Wallet : possui
    Wallet "1" -- "0..*" SoapTransaction : registra
    BubblegramSupport "0..1" -- "0..*" SoapTransaction : origem
    CommentSupport "0..1" -- "0..*" SoapTransaction : origem
    User "0..1" -- "0..*" EconomySettings : atualiza

    CustomizationItem "1" -- "0..*" UserInventoryItem : item
    User "1" -- "0..*" UserInventoryItem : adquire
    CustomizationItem "1" -- "0..*" CommunityInventoryItem : item
    Community "1" -- "0..*" CommunityInventoryItem : adquire
    User "0..1" -- "0..*" CommunityInventoryItem : comprado por
    SoapTransaction "0..1" -- "0..*" UserInventoryItem : pagamento
    SoapTransaction "0..1" -- "0..*" CommunityInventoryItem : pagamento

    SoapTransaction ..> ActionType
    CustomizationItem ..> CustomizationType
    CustomizationItem ..> CustomizationScope
```

## 7.5 Moderação

```mermaid
classDiagram
    direction LR

    class User

    class Report {
        +target_type: ReportTargetType
        +target_id: String
        +reason: ReportReason
        +description: String
        +status: ReportStatus
        +resolution_notes: String
        +reviewed_at: DateTime
        +created_at: DateTime
    }

    class AuditLog {
        +action: AuditAction
        +target_type: String
        +target_id: String
        +reason: String
        +metadata: Json
        +created_at: DateTime
    }

    class ReportTargetType {
        <<enumeration>>
        USER
        COMMUNITY
        BUBBLEGRAM
        COMMENT
    }

    class ReportReason {
        <<enumeration>>
        SPAM
        HARASSMENT
        HATE_SPEECH
        INAPPROPRIATE_CONTENT
        OTHER
    }

    class ReportStatus {
        <<enumeration>>
        PENDING
        INVESTIGATING
        RESOLVED
        DISMISSED
    }

    class AuditAction {
        <<enumeration>>
        USER_SUSPEND
        USER_BAN
        USER_UNBAN
        COMMUNITY_SUSPEND
        COMMUNITY_BLOCK
        COMMUNITY_UNBLOCK
        CONTENT_DELETE
        ECONOMY_ADJUSTMENT
        REPORT_RESOLVE
        REPORT_DISMISS
    }

    User "1" -- "0..*" Report : denuncia
    User "0..1" -- "0..*" Report : analisa
    User "0..1" -- "0..*" AuditLog : executa
    Report ..> ReportTargetType
    Report ..> ReportReason
    Report ..> ReportStatus
    AuditLog ..> AuditAction
```

A denúncia (`Report`) identifica o alvo pelo tipo e pelo identificador (`target_type` e `target_id`), sem chave estrangeira, porque o alvo pode ser um usuário, uma comunidade, uma publicação ou um comentário. O mesmo vale para o registro de auditoria.

## Legenda

| Notação | Significado |
|---|---|
| `A "1" -- "0..*" B` | Associação: um A se relaciona com nenhum ou vários B |
| `A "1" *-- "0..1" B` | Composição: B só existe junto de A (a imagem de uma publicação) |
| `A ..> E` | A usa a enumeração E em um de seus atributos |
| `0..1`, `1`, `1..*`, `0..*` | Multiplicidade: opcional, exatamente um, um ou mais, zero ou mais |
| `<<enumeration>>` | Lista fixa de valores permitidos |

Observações de leitura:
- Uma `Wallet` pertence a exatamente um dono: um usuário **ou** uma comunidade.
- Em `UserConnection`, `follower` é quem segue e `followed` é quem é seguido.
- Em `Comment` e em `Letter`, a associação "resposta a" aponta para o comentário ou a carta respondida. Cada carta tem no máximo uma resposta.
- Datas opcionais (por exemplo `suspended_until`, `blocked_at`, `deleted_at` e `archived_at`) ficam vazias enquanto o estado correspondente não ocorre.

| Classe | Nome no documento |
|---|---|
| User | Usuário |
| UserConnection | Conexão (seguidor) |
| Community / CommunityMember | Comunidade / Membro da comunidade |
| Bubblegram / BubblegramMedia | Publicação permanente / Imagem da publicação |
| Bubblepop | Publicação temporária |
| Comment | Comentário |
| BubblegramSupport / CommentSupport | Apoio em publicação / Apoio em comentário |
| Letter | Carta |
| Wallet / SoapTransaction | Carteira / Movimentação de soap |
| EconomySettings | Configuração da economia |
| CustomizationItem | Item de customização |
| UserInventoryItem / CommunityInventoryItem | Item do usuário / Item da comunidade |
| Report / AuditLog | Denúncia / Registro de auditoria |
