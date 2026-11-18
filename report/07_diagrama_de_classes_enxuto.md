# 7 Diagrama de Classes (versão resumida)

Versão para apresentação, com as classes do funcionamento principal: usuários, comunidades, publicações, interações, cartas, carteira de soap e customização. Ficam de fora a moderação (denúncias e auditoria), a configuração da economia, as enumerações e as classes de apoio (conexão de seguidores, imagens da publicação e inventários), representadas por associações diretas. O diagrama completo está em `05_diagrama_de_classes.md`.

```mermaid
classDiagram
    direction TB

    class User {
        +username: String
        +email: String
        +name: String
        +birth_date: Date
        +description: String
        +profile_photo: Image
        +status: String
        +is_staff: Boolean
    }

    class Community {
        +commname: String
        +name: String
        +description: String
        +guidelines: String
        +member_count: Integer
    }

    class CommunityMember {
        +role: String
        +current_state: String
        +joined_at: DateTime
    }

    class Bubblegram {
        +text: String
        +image: Image
        +soap_count: Integer
        +published_at: DateTime
    }

    class Bubblepop {
        +image: Image
        +description: String
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

    class Wallet {
        +soap_balance: Integer
    }

    class SoapTransaction {
        +amount: Integer
        +action_type: String
        +created_at: DateTime
    }

    class CustomizationItem {
        +name: String
        +item_type: String
        +price: Integer
    }

    User "0..*" -- "0..*" User : segue
    User "1" -- "0..*" CommunityMember : participa
    Community "1" *-- "1..*" CommunityMember : possui

    User "1" o-- "0..*" Bubblegram : publica
    Community "0..1" o-- "0..*" Bubblegram : contém
    User "1" *-- "0..*" Bubblepop : publica
    Bubblegram "1" *-- "0..*" Comment : recebe
    User "1" -- "0..*" Comment : escreve
    Comment "1" *-- "0..*" Comment : respostas

    Bubblegram "1" *-- "0..*" BubblegramSupport : recebe apoio
    User "1" -- "0..*" BubblegramSupport : apoia
    Comment "1" *-- "0..*" CommentSupport : recebe apoio
    User "1" -- "0..*" CommentSupport : apoia

    User "1" -- "0..*" Letter : envia
    User "1" -- "0..*" Letter : recebe

    User "0..1" o-- "0..1" Wallet : possui
    Community "0..1" o-- "0..1" Wallet : possui
    Wallet "1" o-- "0..*" SoapTransaction : registra

    User "0..*" o-- "0..*" CustomizationItem : adquire
    Community "0..*" o-- "0..*" CustomizationItem : adquire
```

Valores dos atributos de texto:
- `User.status`: ACTIVE, SUSPENDED ou BANNED.
- `CommunityMember.role`: MEMBER, COMM_ADMIN ou LEADER. `current_state`: ACTIVE, SILENCED ou BANNED.
- `CustomizationItem.item_type`: moldura, tema, selo, cor do nome, papel de parede, cor de destaque, bolha de comentários e seção do perfil.

Tipos de relação usados:
- **Composição** (`*--`): a parte não existe sem o todo e é apagada junto com ele (membros da comunidade, comentários e apoios de uma publicação, respostas de um comentário, bubblepops do usuário).
- **Agregação** (`o--`): o todo reúne partes que continuam existindo sem ele (as publicações de um usuário ou comunidade, a carteira de seu dono, as movimentações de uma carteira, os itens que um usuário ou comunidade adquire).
- **Associação** (`--`): relação simples entre objetos independentes.
- **Generalização** (herança): o modelo de domínio não usa herança entre suas classes. Os papéis de comunidade (membro, administrador, líder) são valores de `CommunityMember.role`, e não subclasses. A única herança real está na classe `User`, mostrada no diagrama completo.

Observações: uma `Wallet` pertence a um usuário **ou** a uma comunidade. Uma `Bubblegram` com comunidade é uma publicação de comunidade; sem comunidade, é do perfil pessoal. O `Bubblepop` é a publicação temporária.
