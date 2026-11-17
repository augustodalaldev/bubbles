# Progress

## Pillar 1 — Structural
- [x] 1.1 Initial setup (backend only; frontend setup comes in the React block)
- [x] 1.2 Models (full class diagram + economy base)
  - [x] Slice 1: User & Community models (`accounts`, `communities`)
  - [x] Slice 2: Economy base (`EconomySettings`, `Wallet`, `SoapTransaction`, services, exceptions)
  - [x] Slice 3: Content & Social models (`content`, `social`, origin links on `SoapTransaction`)
  - [x] ER diagram (`docs/ER.md`) generated
- [x] 1.3 Users (CRUD)
- [x] 1.4 Communities (CRUD)

## Pillar 2 — Content, Economy & Social Interactions
- [x] 2.1 Bubblegrams (permanent posts, personal & community, media uploads 1-4, deletion without refund)
- [x] 2.2 Comments (threaded replies, 2000 chars limit, free, parent validation)
- [x] 2.3 Soap Supports & Interactions (supports on posts/comments, atomic ledger transfers, uniqueness, counters)
- [x] 2.4 Bubblepops (ephemeral stories, duration-based pricing, auto-expiry filtering)
- [x] 2.5 Letters (asynchronous follow-gated direct mail, reply threading, read tracking)

## Pillar 3 — Social Feed & Discovery
- [x] 3.1 Follows management & profile relationships (followers/following lists, counts, relationship flags)
- [x] 3.2 Chronological Feed (personal bubblegrams from followed users + active community bubblegrams)
- [x] 3.3 Ephemeral Stories Tray (active bubblepops from followed users)
- [x] 3.4 Discovery & Global Search (unified search across users and communities)

## Pillar 4 — Passive Soap & Economy Admin
- [x] 4.1 Activity tracking (`last_seen_at`), heartbeat endpoint, passive soap distribution service & expired Bubblepops cleanup command
- [x] 4.2 EconomySettings management (GET/PATCH `/api/v1/economy/settings/` restricted to staff)

## Pillar 5 — Customization & Design Tokens
- [x] 5.1 Modular customization catalog (`CustomizationItem`), user inventory (`UserInventoryItem`), soap purchasing (`SPEND_CUSTOMIZATION`), inventory-validated profile equipping (`customization_json`) & design tokens API

## Pillar 6 — Moderation & Governance
- [x] 6.1 Content moderation, user reports (`Report`), administrative audit logging (`AuditLog`), account suspension/ban, community blocking & admin tooling

## Review & integration (see docs/REVIEW_PLAN.md)
- [x] Phase 0 — Plan registered
- [x] Phase 1 — Backend blockers: image upload validation (type + 10 MB, `images` bypass removed), banned members cannot leave, only ACTIVE members can support community content, user throttle 10000/day, auth endpoints ignore stale Bearer header (397 tests)
- [x] Phase 2 — Backend business rules: bubblepop suspension/limits/expiry, concurrent purchase, non-numeric ids, report audit, `*_username` null fields, letter read via service (404 for outsiders), community row lock + blocked checks, community customization blocked until purchases exist, logout/refresh hardening, passive cap in local time, zero-cost settings, absolute image URLs (435 tests)
- [x] Phase 3 — API contract and error handling: Http404/PermissionDenied/ValidationError/IntegrityError mapped to the envelope, nested errors flattened (`media_files[1]`), headers preserved, JSON 404/500 for `/api/` (effective with DEBUG=False), shared `StandardPagination`, `ensure_user_wallet`/`ensure_community_wallet`, `is_staff` on `/users/me/` (449 tests)
- [x] Phase 4 — Frontend foundation: in-memory access token + single-flight refresh, no Bearer on `/auth/*`, typed per-domain `services/`, pt-BR error mapping by API `code`, session bootstrap/login/register/logout, heartbeat every 5 min, session gate in `App.tsx`, real balance/avatar in the Header (mock login removed). Verified against a throwaway database (migrate from scratch + auth flow). `mockData.ts` is temporarily `@ts-nocheck` until phase 5
- [x] Phase 5 — Screen-by-screen integration: feed, post modal + threaded comments, profile (own/others, follow), communities (hub/detail/create), store (purchase/equip via `slots`), letters (inbox/sent/compose/reply), bubblepop creation form. `mockData.ts`, dead components and `canvas-confetti` removed. Verified with a 43-check script that runs the real `services/` against a throwaway backend (all passed). Backend: members list ordered leader/admins/members (450 tests)
- [x] Phase 6 — Loading / error / empty states: every data screen uses `LoadingState`/`ErrorState`/`EmptyState`; `insufficient_soap` shows cost and balance (pt-BR)
- [ ] Phase 7 — Visual polish
- [ ] Phase 8 — Repository hygiene
- [ ] Phase 9 — Docs

## Notes
- Do NOT run `migrate` until the custom `User` exists and `AUTH_USER_MODEL` is set (first task of 1.2).