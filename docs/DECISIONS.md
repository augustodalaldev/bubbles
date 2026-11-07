# Decisions

## Taken in step 1.1 (2026-11-02)
| Decision | Reason |
|---|---|
| Monorepo (`backend/`, later `frontend/`, `docs/`) | Single repo, simple to run and version |
| uv + Python 3.12; `uv.lock` committed | Reproducible environment |
| Django 5.2 LTS; other libs unpinned in pyproject, frozen by `uv.lock` | Long support window, latest compatible libs |
| PostgreSQL 17 in Docker; Django/Vite run natively | Fast feedback; PG 18 changed the data volume path |
| Single root `.env` read by Compose and Django; DB built from `POSTGRES_*` | No duplicated config |
| Split settings (base/dev/test/prod); tests also on PostgreSQL | Constraints and row locks depend on PG |
| Celery/Redis, SIMPLE_JWT config and token blacklist deferred | Introduced in the step/pillar that needs them |
| `AUTH_USER_MODEL` deferred to start of 1.2 | Must be set before the first `migrate` |

## Settled by the project brief
- S1: Bubblegram (permanent) and bubblepop (ephemeral); `community = NULL` means personal profile.
- S2: Messaging is letters (follow-gated, immutable, replies via `reply_to`), not chat.
- S3: Soap is an integer. Support costs the donor 1; author +1; community content also gives the community +1.
- S4/S5: Soap buys customization (user or community wallet); users earn soap passively.
- S6/S10: One support per donor per target; `soap_count`/`member_count` are cached counters.
- S8/S9: Roles LEADER/COMM_ADMIN/MEMBER; states ACTIVE/SILENCED/BANNED; a wallet belongs to exactly one of user/community.
- S13/S14: Prototype scope (reductions recorded); code and docs in English, UI copy in pt-BR.

## Open (Pillar 1 questions, pending answers)
Q2 login identifier · Q3 signup grant · Q4 founding cost · Q5 birth_date rule · Q6 email verification · Q7 profile visibility · Q8 image storage · Q9 UserConnection PK · Q10 Comment.parent composite FK

## Answers to Pillar 1 questions (2026-11-03)
| # | Decision |
|---|---|
| Q1 | Confirmed. Code fully in English, comments only where they add value |
| Q2 | Login by username (unique, case-insensitive). Email + code login is a stretch goal |
| Q5 | `birth_date` required, minimum age 14 |
| Q6 | Email verification and password reset: later |
| Q7 | Profiles and personal bubblegrams visible to any logged-in user |
| Q8 | Local MEDIA through Django's storage API (`STORAGES`), so S3 can be swapped in later; upload UI in the frontend |
| Q9 | `UserConnection` with surrogate id + unique constraint |
| Q10 | `Comment.parent` validated in the service; DB-level composite FK is a stretch in Pillar 2 |
| - | pre-commit removed; ruff runs manually (`make lint` / `make format`) |

## Step 1.2 — slice 1 (2026-11-03)
| Decision | Reason |
|---|---|
| Login by username or email; an identifier containing "@" is treated as email | Username format forbids "@" (enforced by `chk_user_username_format`) |
| `email` kept: required, unique case-insensitive (`uniq_user_email_ci`) | Email login / code confirmation stays possible without a migration |
| Username case-insensitivity via lowercase-only CHECK + `unique=True` | No redundant `Lower()` constraint |
| `deleted_` username prefix reserved | Anonymized accounts become `deleted_<id>` |
| `UserConnection` with surrogate id + unique (Q9) | Simplest option |
| `UploadTo` + Django `STORAGES` for uploads | Local now, S3 later with no model changes |

## Step 1.2 — slice 2: Economy base (2026-11-04)
| Decision | Reason |
|---|---|
| `DomainError` in `apps.core.exceptions`, `InsufficientSoap` in `apps.economy.exceptions` | Decouples domain rule violations from HTTP/DRF and allows rich context (`cost`, `balance`) |
| `EconomySettings` singleton enforced by DB constraint (`chk_economy_settings_singleton`) and short cache | Avoids magic numbers, tunable via admin panel without redeployment |
| `Wallet` with strict owner XOR constraint (`chk_wallet_exactly_one_owner`) | Wallets belong to either a User or a Community, never both or neither |
| `SoapTransaction` append-only enforcement in DB + model | Ledger integrity: rows cannot be edited or deleted; amount signs match action types |
| Row-locking with ascending PK order in `apply_movements` | Prevents deadlocks during concurrent multi-wallet movements inside `transaction.atomic()` |

## Step 1.2 — slice 3: Content, Social & Ledger Origins (2026-11-04)
| Decision | Reason |
|---|---|
| `Bubblegram` personal vs community via nullable `community` FK | Clean single model; personal bubblegrams have `community = NULL` |
| `Bubblegram` text required if `type == TEXT` | Prevents empty text posts at both model validation and DB check constraint levels |
| `Bubblepop` expiration constraint `chk_pop_expires_after_created` | Enforces `expires_at > created_at` in the database |
| `Comment.parent` validated in `clean()` | Ensures reply belongs to the exact same bubblegram; self-parenting blocked by DB constraint |
| `Letter` immutability in model `save()` | Letters are postal mail, not chat; content cannot be edited once sent, only `read_at` is settable |
| `Letter.reply_to` unique constraint `uniq_one_reply_per_letter` | Enforces at most one direct reply letter per original letter |
| `SoapTransaction` origin foreign keys with `chk_tx_single_origin` | Connects ledger rows to supports with `SET_NULL` cascade and at most one origin FK |

## Pre-1.3 Adjustments: Profile Customizations & User Limits (2026-11-04)
| Decision | Reason |
|---|---|
| User name max 50 chars, description max 250 chars | Tighter constraints for concise user profiles; community limits remain at 60 and 500 |
| `customization_json` on `User` and `Community` (`JSONField`, default `dict`) | Flexible JSON configuration storing visual customizations (background colors, profile borders, etc.) |
| `SPEND_CUSTOMIZATION` action type & `spend_customization` service helper | Explicit ledger tracking for soap spent on visual customizations by user or community wallets |

## Step 1.3 — Users CRUD & Authentication (2026-11-04)
| Decision | Reason |
|---|---|
| `UsernameOrEmailBackend` for login authentication | Supports unambiguous login via username or email; rejects inactive and deleted accounts |
| Rotating refresh token with blacklist in `httpOnly` cookie (`Path=/api/v1/auth/`) | Secure against XSS; short-lived access token in body, rotating refresh with simplejwt blacklist |
| Uniform error responses via `custom_exception_handler` (`{"error": {"code", "message", "fields"}}`) | Decouples HTTP representation and gives predictable structure for frontend consumption |
| User registration inside `@transaction.atomic` with initial wallet & signup grant | Guarantees atomic integrity: if credit or wallet creation fails, user is rolled back |
| Soft delete with anonymization (`delete_account`) | LGPD compliant; preserves economic ledger and post history while removing personal data; blocks deletion if user is leader of active communities |
| Scoped rate throttling on auth endpoints (`20/minute`) | Prevents brute-force credential stuffing and registration spam |
| `PublicUserSerializer` strictly excludes private data (`email`, `birth_date`, `wallet`) | Invariant: personal bubbles must never leak private user details |

## Step 1.4 — Communities CRUD, Membership & Moderation (2026-11-05)
| Decision | Reason |
|---|---|
| Atomic founding with 300 soap transfer (`founding_cost`) | Creator wallet debited 300, community wallet credited 300; creator becomes LEADER with member_count=1; fails atomically with `insufficient_soap` |
| Cached `member_count` synchronization | Increments on join/unban and decrements on leave/ban using `F()` expressions inside `@transaction.atomic` |
| Moderation permissions hierarchy | `COMM_ADMIN` can only moderate regular members (`MEMBER`); only `LEADER` can manage admins, guidelines, transfer leadership, or archive |
| Safe leadership transfer sequence | Demotes current leader to `COMM_ADMIN` before promoting target member to `LEADER` inside `@transaction.atomic` to prevent partial unique constraint violation (`uniq_one_leader_per_community`) |
| Community detail capabilities payload | `GET /communities/{commname}/` returns `my_membership` and a boolean `permissions` map so the frontend does not re-implement access rules |
| Community wallet read access restricted | `GET /communities/{commname}/wallet/` strictly requires active `LEADER` or `COMM_ADMIN` (or system admin) |

## Pillar 2 Decisions (2026-11-07)
| Decision | Reason |
|---|---|
| Max text length: 2,000 chars for posts and comments | Unified upper bound keeping interactions focused and manageable |
| Immutability for posts and comments | Reflects product philosophy ("think before you interact"); content cannot be edited, only deleted |
| Post deletion does NOT refund supports | Supports are final; deleting content preserves economic history and balances (ledger rows use `SET_NULL` cascade) |
| Text optional for posts with media | Users can publish image posts without descriptions; `TEXT` type still requires text |
| Local media storage behind Django `STORAGES` + `UploadTo` abstraction | Zero-model-change migration path to S3/cloud storage in the future |
| Free threaded comments with active community member gating | Comments require 0 soap; posting in a community requires active membership and non-archived status |
| Supports: 1 soap donor debit, +1 author credit (+1 community wallet on community content) | Atomic ledger transfers via `apply_movements(..., origin=support)`; supports are non-refundable; self-support and duplicate support blocked |
| Bubblepops duration-based pricing: `ceil(hours / 4)` | Ephemeral stories (1 to 48 hours) costing between 1 and 12 soap; auto-filtered on read by `expires_at > now` |
| Follow-gated direct mail (Letters) | Starting a thread requires following the recipient; replies are follow-exempt via `reply_to` (max 1 reply per letter); immutable on send |





