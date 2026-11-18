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

## Pillar 3 Decisions (2026-11-07)
| Decision | Reason |
|---|---|
| Split user serializers (`PublicUserSerializer` vs `UserProfileDetailSerializer`) | Prevents N+1 queries when embedding authors in lists (posts, comments, letters) while providing full stats (`followers_count`, `following_count`, `is_following`, `is_followed_by`) on profile detail |
| Strictly chronological feed with zero algorithmic ranking | Aligns with core product principle: followed personal bubblegrams + active community bubblegrams, ordered strictly by `-published_at, -id` |
| Stories tray separated from main feed | Dedicated `/api/v1/feed/bubblepops/` endpoint returns active stories from followed users without cluttering the post stream |
| Unified discovery endpoint (`/api/v1/search/?q=...`) | Fast case-insensitive search across active users (username/name) and communities (commname/name/description) |
| Bounded social recommendations in feed ("Sugerido para você") | Interweaves bounded (max 4 popular in last 24h + max 4 from 2nd-degree network) suggested posts with `is_suggested` and `suggestion_reason`; preserves strict chronological ordering (`-published_at`) and finite pagination without endless doomscrolling |

## Pillar 4 Decisions (2026-11-07)
| Decision | Reason |
|---|---|
| User presence tracking via throttled middleware + heartbeat API | `UpdateLastSeenMiddleware` throttles DB updates to at most once every 60s per user to avoid DB write hotspots on navigation; `POST /api/v1/auth/heartbeat/` provides explicit presence updates |
| Passive Soap distribution engine (`distribute_passive_soap`) | Users seen within `passive_interval_minutes` receive `default_passive_earn_rate` (5 soap), strictly capped at `passive_daily_cap` (15 soap/day); time-windowed idempotency keys prevent duplicate payouts within the same interval |
| Ephemeral content hard cleanup (`cleanup_expired_bubblepops`) | Bubblepops with `expires_at <= now` are purged from PostgreSQL along with their physical media files from Django `default_storage` |
| Django management commands for periodic maintenance | `manage.py distribute_passive_soap` and `manage.py cleanup_expired_bubblepops` can be invoked via Linux cron, Kubernetes CronJob, or Celery task wrappers without requiring an external message broker during dev |
| Singleton `EconomySettings` administration API (`/api/v1/economy/settings/`) | Read accessible to authenticated users so clients know fees/rates; `PATCH` strictly restricted to staff administrators (`IsAdminUser`) with model-level validation and actor audit tracking (`updated_by`) |

## Pillar 5 Decisions (2026-11-07)
| Decision | Reason |
|---|---|
| Modular Customization Catalog (`CustomizationItem`) | Stores extensible item types (`AVATAR_FRAME`, `PROFILE_THEME`, `CHAT_BUBBLE`, `BADGE`, `NAME_COLOR`), unique slug `code`, soap `price`, and JSON `metadata` for design tokens/CSS styles consumed directly by the frontend |
| User Inventory Model (`UserInventoryItem`) | Distinct relationship model linking users to acquired items with unique constraint `(user, item)` preventing duplicate purchases; tracks origin `SPEND_CUSTOMIZATION` transaction |
| Inventory-Gated Active Customization (`customization_json`) | `customization_json` reflects what the user is currently wearing; updating/equipping (`/api/v1/customization/equip/` or `/api/v1/users/me/`) strictly enforces that all equipped items exist in the user's inventory |
| Atomic Soap Purchase Flow (`purchase_customization_item`) | Atomic execution debits soap via `spend_customization` and registers the inventory holding; enforces item active status, unowned status, and balance sufficiency |

## Pillar 6 Decisions (2026-11-07)
| Decision | Reason |
|---|---|
| User reporting pipeline (`Report`) | Authenticated users can report inappropriate users, communities, bubblegrams, or comments (`POST /api/v1/reports/`); staff reviews and resolves reports (`PATCH /api/v1/admin/reports/{id}/`) with resolution notes |
| Administrative Audit Logging (`AuditLog`) | Centralized, append-only log capturing administrative actions (suspensions, bans, unbans, community blocks, content deletions, economy adjustments, report resolutions) with actor, target, reason, and structured metadata |
| Account suspension & ban mechanics | `User.status` (`ACTIVE`/`SUSPENDED`/`BANNED`) with `suspended_until`. Suspended accounts are barred from posting, commenting, supporting, and sending letters until the suspension expires; banned accounts are permanently deactivated (`is_active=False`) |
| Community blocking (`Community.blocked_at`) | Blocks malicious communities (`blocked_at is not None`) preventing joins, publishing, comments, and supports |
| Administrative soap adjustments (`admin_adjust_soap`) | Staff can credit or debit wallets with `ActionType.ADMIN_ADJUSTMENT`, with mandatory reason and audit entry recording before and after balances |

## Review & integration (2026-11-17) — see docs/REVIEW_PLAN.md
| Decision | Reason |
|---|---|
| Image uploads validated by `core.uploads.validate_image_upload` (Pillow-detected JPEG/PNG/WebP/GIF, image extension, max 10 MB) through `core.fields.SafeImageField` | `FILE_UPLOAD_MAX_MEMORY_SIZE` is only a memory/temp-file threshold, not a limit; arbitrary files were being stored and served from `/media/` |
| Only `ACTIVE` members can support community content; a banned member cannot `leave` | Supporting charged soap to non-members; leaving erased the ban row and allowed re-joining |
| `user` throttle raised to 10000/day | The heartbeat alone consumed 1440 of the previous 1000/day |
| Auth endpoints (`login`, `register`, `refresh`, `logout`) use no authentication classes | A stale `Authorization` header turned them into 401s; logout must clear the cookie even with an expired access token |
| Refresh rejects inactive/deleted users and is throttled (`auth` scope) | Banned/deleted users kept receiving tokens |
| Every error uses `{"error": {code, message, fields}}`, including Django `Http404`/`PermissionDenied`/`ValidationError`/`IntegrityError`, nested serializer errors (`media_files[1]`) and `/api/` 404/500 (with `DEBUG=False`); headers (`Retry-After`, `WWW-Authenticate`) are preserved | The frontend maps stable codes to pt-BR copy; unhandled cases returned HTML |
| `delete_file_on_commit` for stored files | Deleting inside `atomic()` lost files when the transaction rolled back |
| `EconomySettings` values of 0 are valid and skip the corresponding movement | They previously made signup/publishing/supports fail |
| Passive daily cap and its idempotency key use the local (America/Sao_Paulo) day | The cap reset at 21:00 local time (UTC midnight) |
| Community `customization_json` is rejected (`customization_not_available`) | Communities could be customized for free; buying with the community wallet (S4) is not implemented yet |
| Community row is locked (`select_for_update`) for membership changes; blocked communities reject leader/admin management (staff exempt) | `member_count` drifted under concurrency; service rules disagreed with the `permissions` map |
| Members list ordered LEADER, COMM_ADMIN, MEMBER, then newest | The moderation team must be on the first page |
| `GET /letters/{id}/` is a pure read; the view marks the letter read for its recipient; outsiders get 404 | Replying marked the original as read; 403 leaked the existence of letters |
| `/customization/equipped/` is an alias of `/customization/equip/` (GET reads, POST equips); the frontend uses `slots` (`item_ids` replaces every slot) | Documents an endpoint that existed but was undocumented |
| Production settings fail fast on a placeholder/short `DJANGO_SECRET_KEY` or empty `DJANGO_ALLOWED_HOSTS`; HTTPS redirect, HSTS (default 3600 s), CSRF origins and proxy header come from the environment | `check --deploy` warnings and unsafe defaults |
| Periodic commands (`distribute_passive_soap`, `cleanup_expired_bubblepops`) have no scheduler in the repo | Run them from cron/CronJob; bubblepop reads already filter by `expires_at`, so correctness does not depend on the job |
| Frontend: access token in memory + single-flight refresh through the httpOnly cookie; no Bearer on `/auth/*`; no React Router/TanStack Query (kept zustand + axios) | Matches the Pillar 1.3 decision; avoids new dependencies |
| Frontend: costs and balances come from `GET /economy/settings/` and the API responses; supports/purchases update from server data, never optimistically | Rule 6 of the project guide: the frontend never decides economics |
| Frontend: removed fake features without backend (notifications bell, forgot-password link, share link, suggested users, "popular" tab, fake counters) and `canvas-confetti` | `docs/frontend/PLAN.md` principles (100% faithful to the API, no useless animation) |

## Community customization (2026-11-17)
| Decision | Reason |
|---|---|
| `CustomizationItem.scope` (USER / COMMUNITY / BOTH, default USER); the user store lists USER+BOTH, a community store COMMUNITY+BOTH | A community and a profile need different catalogs; existing items stay user-only |
| `CommunityInventoryItem` (unique community+item, `purchased_by`, ledger link) | Ownership by the community, one purchase per item, audit of who spent the soap |
| Only the ACTIVE leader or an ACTIVE admin can buy and equip; system staff cannot spend a community's soap | RF014/S4: it is the community's money; staff keep the Django Admin |
| Purchases debit the **community wallet** (`SPEND_CUSTOMIZATION`); the buyer's personal wallet is never touched | Soap rule S4 |
| `purchase_community_item` locks the community wallet row first, re-checks ownership under the lock and keeps the unique constraint as backstop | Concurrent purchases are serialized: soap for one item never buys two, the same item is charged once |
| Blocked/archived communities cannot buy or equip | Consistent with the other management rules |
| Equipping uses `slots` (item id or null) through `POST /communities/{c}/customization/equip/`; writing `customization_json` directly stays rejected | Ownership is always validated; other slots are untouched |
| New endpoints: `POST /communities/{c}/customization/items/{id}/purchase/`, `GET /communities/{c}/customization/inventory/`, `GET|POST /communities/{c}/customization/equip/`, `GET /customization/items/?community={c}`; new `permissions.can_customize` | The frontend renders what the API reports |

## Scheduler (2026-11-17)
| Decision | Reason |
|---|---|
| `manage.py run_scheduler` (stdlib loop, `core/scheduler.py`) + `make scheduler` / `make scheduler-once`; no Celery/Redis, no new dependency | The brief asks for something lightweight; it runs identically inside and outside Docker |
| No scheduler service in `docker-compose.yml` | The compose file only runs PostgreSQL and no backend image exists (Django runs natively); a service would require a new Dockerfile. `make scheduler` or cron covers it |
| `distribute_passive_soap` every `passive_interval_minutes`, aligned to epoch multiples of the interval | Payment is idempotent per window (`floor(epoch/interval)`), so exactly one run per window |
| `cleanup_expired_bubblepops` hourly | Reads already filter `expires_at`; the job only reclaims rows and disk |
| A PostgreSQL session advisory lock (`core/locks.py`) serializes each job across processes | Two overlapping runs could both read the daily total before either paid |
| Passive soap pays each user in its own short transaction; failures are logged, not swallowed | The previous single transaction held every wallet lock and hid errors with `except Exception: pass` |
| Job failure never stops the loop; `--once` exits non-zero if a job failed | Fault tolerance in the daemon, observability for cron |

## URL navigation (2026-11-17)
| Decision | Reason |
|---|---|
| `react-router-dom` 6.x (BrowserRouter), instead of syncing the store with the History API by hand | Back/forward, reload, deep links, real `<a>` links (middle click, copy address) and route guards come for free; hand-rolled routing would re-implement them with more risk. Cost: one dependency (~20 kB gzip) |
| URLs: `/`, `/login`, `/register`, `/u/:username`, `/communities`, `/c/:commname`, `/store`, `/letters`, `/p/:id`, `*` = 404 | One URL per existing screen; no new screens. `/p/:id` reuses the post modal |
| Only the search term (`?q=`) and the letter recipient (`?to=`) live in the URL; feed filters and community tabs stay in component state | Keeps URLs meaningful without turning every toggle into history entries |
| Guard: anonymous visitors go to `/login?next=<url>` and return after login; an explicit logout does not keep `next`; an expired session does | Deep links work after signing in; logging out must not leak the last page |
| `next` accepts only same-origin app paths (no `//`, scheme, backslash or control characters, never the auth screens) | Prevents an open redirect through a crafted login link |
| Each screen is a lazy chunk (`React.lazy`) | Keeps the first bundle under 500 kB after adding the router |
| The post modal has "Copiar link" now that `/p/:id` exists | The earlier share button was removed because no URL existed |
| Servers that serve `frontend/dist` must fall back to `index.html` (README has the nginx snippet) | SPA routing; Vite dev/preview already do it |
| `VITE_API_TARGET` selects the backend the dev proxy talks to | Lets the demo backend run on another port |

## Demo data (2026-11-17)
| Decision | Reason |
|---|---|
| `config.settings.demo` (dev settings + `DEMO_DB_NAME`, default `bubbles_teste`, must differ from `POSTGRES_DB`) and `seed_demo` refuses to run unless the settings are the demo ones, `DEBUG` is on and the connected database is the demo one | The seed must never be able to touch the development database |
| The Makefile refuses `DEMO_DB` equal to the `.env` development database or `postgres` before dropping anything | `make demo-reset` drops a database |
| The seed calls the services (`register_user`, `create_community`, `create_bubblegram`, `support_*`, `send_letter`, purchases, `file_report`, ...) | Business rules, cached counters and the soap ledger stay correct and consistent |
| ORM directly only for: the customization catalog (admin-maintained table, no service), back-dated timestamps (services always stamp "now"), expired bubblepops (no service creates them), staff flag of the admin | There is no service for these; every use is commented in the code |
| Soap comes from audited `admin_adjust_soap` (admin actor) once per newly created account, and for community wallets | Mirrors how soap enters the system; running again does not give more soap |
| Ledger rows keep today's date; everything else is spread over the last 30 days | The ledger is append-only (`created_at` is not editable) |
| Randomness comes from an independent stream per user/post/community (`seed|step|key`) and DB-driven choices are ordered by pk | Re-running makes the same decisions and finds what it created: idempotent, with the same row counts |
| `--reset` uses a manifest (`backend/.demo_cache/seed_manifest.json`) of the primary keys the seed created and deletes them in dependency order, including their media files; catalog items still owned by someone else are kept | Only seed data is removed; hand-made data survives. The append-only ledger of the seed's own wallets is removed with `_raw_delete`, and only for those wallets in the demo database |
| Photos from The Cat API and Dog CEO via `urllib` (no new dependency), cached in `backend/.demo_cache/images/`, validated with the upload validator | Free, no key, downloaded once; offline falls back to the cache or no images |
| `faker` (pt_BR) as a dev dependency; Portuguese content lives in `apps/core/demo/content.py` | Natural names and texts; fixed seed keeps them reproducible |
| Accounts share the password `DemoPets2026!`; emails use `@demo.bubbles.test` | Demo credentials only; the reserved domain cannot receive mail |

## Polish 2 — Phase 1 (2026-11-17)
| Decision | Reason |
|---|---|
| `LANGUAGE_CODE = "pt-br"` | Django, DRF and simplejwt built-in messages (invalid e-mail, password validators, throttling, token errors) come out in Portuguese |
| Central catalog `apps/core/messages.py` (error code -> pt-BR text, with `{cost}`/`{balance}`/`{communities}` placeholders); the exception handler replaces `message` and the per-field messages of every `DomainError` | The 180 raise sites keep English messages for logs/tests; the UI never depends on translating messages one by one in the frontend |
| A test scans the source for every `code="..."` and fails when one is missing from the catalog | New error codes cannot ship untranslated |
| User-visible validator/serializer/upload texts written in Portuguese at the source | They are shown through field errors |
| `auth_refresh` throttle scope (120/min) separate from `auth` (20/min) | Every page load calls `/auth/refresh/`; a reload loop was exhausting login attempts |
| Anonymized accounts are named "Conta excluída" | The name appears in feeds and threads, which are in Portuguese |
| `PasswordInput` (show/hide) is the only password field component | One behavior everywhere, including future password fields |
| Customization tokens are applied only through `utils/theme.ts`: hex colors, a strict glow pattern, label text truncated to 24 chars; anything else is ignored | Tokens reach inline styles, so nothing from the API is trusted |
| `Avatar` applies the equipped frame and `UserName` the name color and badge, so every place that shows a person gets them | Customization used to apply only to the community photo and the store preview |
| Phones: the header splits into two rows, side columns stack instead of disappearing, fixed-height two-pane layouts apply only from `lg`, the profile mural lays bubbles out for its real width | At 375 px the logo and avatar shrank to 0 px and the community info column was hidden |


## Polish 2 — Phase 2 (2026-11-17)
- Letters expose `reply_to_summary` (id, sender, 140-char excerpt, sent_at) and `reply_id` (the answer, via a Subquery in the selectors). The excerpt keeps the replied-to letter visible without a second request, and neither field adds queries per row.
- The open letter is part of the URL (`/letters/:id?`, a single route so the list is not remounted). Closing goes back in history, or to `/letters` on a direct visit. An answered letter hides "Responder" (the backend rejects a second reply with `already_replied`).
- Follower/following lists are their own routes, so the counters are plain links and the own-profile tab stays highlighted on them.

## Polish 2 — Phase 3 (2026-11-17)
- Community deletion is a soft delete (`Community.deleted_at`): memberships and photos are removed, text is cleared and the handle becomes `deleted_<id>`, so the old URL is a 404 and the handle is reusable. The row, wallet and ledger stay (append-only). Posts of the community are hidden (post detail 404, excluded from suggestions). A leader of a *blocked* community cannot delete it (it would dodge moderation). Staff and admins cannot delete (leader only, D2).
- Account deletion also removes the user's bubblepops (and their images). A leader must transfer leadership or delete the community first (409 `must_transfer_leadership` lists them; the UI links to their settings).
- Password change requires the current password, ends every other session (outstanding refresh tokens blacklisted) and returns fresh tokens for the current one. E-mail change requires the password. Username stays immutable (D11).
- Photos are removed with explicit `remove_profile_photo` / `remove_community_photo` flags instead of sending `null` in multipart.
- Destructive dialogs (`ConfirmDialog`) state the consequences and require typed text (`EXCLUIR`, or the community handle); the server re-checks the handle and the password.

## Polish 2 — Phase 4 (2026-11-17)
- Users: `User.moderation_reason`. Suspension is temporary (end date + reason, expires by itself) and keeps the person able to log in and read; the existing service checks block posting, commenting, support and letters. A ban sets `is_active=False`: login fails with `account_banned` + reason, but only after the password is correct (a wrong password still gets the generic message, so a ban is not revealed to someone guessing usernames). Banned users disappear from profile, search, comments, member lists and the feed (content hidden, not deleted, so a restore brings it back).
- Communities: `Community.suspended_until` + `moderation_reason`; the existing `blocked_at` is the ban. `is_moderated` (ban or active suspension) drives every interaction check; `not_moderated_q()` drives lists, search and the feed. A moderated community is a 404 for anyone who is not staff or a non-banned member; those members get a read-only page with a banner (status, end date, reason). Leaders cannot delete a moderated community (it would dodge moderation).
- Restore: one action per target type clears suspension, ban and reason (`/admin/users/<id>/unban/`, `/admin/communities/<name>/unblock/`). Every action is written to the audit log with its reason.
- Staff UI is minimal on purpose: `/moderacao` with Users, Communities and History tabs. Reports and soap adjustments still use the API / Django Admin.

## Polish 2 — Phase 5 (2026-11-17)
- Customization security: each item type accepts only its own metadata keys (`customization/validators.py`): colors are `#rgb`/`#rrggbb`, glows follow `0 0 Npx #hex`, badge labels are 1-24 characters, wallpaper `fit` is `cover` or `tile`. Validation runs in `CustomizationItem.clean()` (Django Admin) and in the staff catalog API. `PATCH /users/me/` no longer stores the client's `customization_json`: only the item ids are read and the data is rebuilt from the catalog (ownership and slot checked), so metadata cannot be smuggled in. Free-form entries are rejected (`invalid_customization`).
- Wallpapers are images uploaded by staff only (Django Admin > Customization items, type Wallpaper, image required, same upload validation as every image). Users can only buy them. The equipped snapshot stores the image URL; the frontend only accepts same-origin `/media/...` paths as a background.
- Accent color sets `--accent` / `--accent-contrast`, read by `.btn-pink` and the panel-header underline. It and the wallpaper are applied to the viewer's own pages, and replaced by the owner's theme while viewing that person's profile.
- Badges: three slots (`badge`, `badge_2`, `badge_3`); the same badge cannot fill two slots (`duplicate_badge`). Staff grant badges by creating a user inventory row in the admin.
- Profile section: unlocked by owning a SECTION item (`section_locked` otherwise); shown only while the item is equipped and the text is non-empty; plain text rendered by React (never HTML).
- Bubble effect (D10): CSS-only look on photo posts of the profile mural (Mural and Grade): highlight, rim and glassy edge; static, with a small hover tilt only under `prefers-reduced-motion: no-preference`.
- Community banner: `banner_photo` (already supported by the API) is now shown larger above the community mural and can be set or removed from the community settings.

## Polish 2 — Phase 6 (2026-11-18)
- The demo seed places every new customization option on purpose (`_customization_showcase`) instead of drawing them at random, so each wallpaper, accent color and section item is worn by at least one profile; the older random purchase step is limited to the older item types. The staff badge (`selo_equipe`, priced out of reach) is inserted directly into the inventory, like an admin would.
- The administration showcase runs once: the deleted account and community are renamed (`deleted_<id>`), so the manifest (`special`) rather than the handle tells a later run that they exist. Moderated and deleted communities are skipped when the seed picks where to post.
- Seed report choices are keyed by position, not by database id (ids differ between runs, which made the pending/resolved mix depend on the id sequence).
- Pytest must run with the test settings: with the demo settings it would use the demo's real media folder.
