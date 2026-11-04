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
