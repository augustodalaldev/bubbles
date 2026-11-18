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
- [x] Phase 7 — Visual polish: no all-caps labels (sentence case), only bubble shapes are rounded, no emojis/continuous animations, real avatars with initial fallback, bundle 488 kB (no >500 kB warning); official SVGs in `public/` verified identical to `references/`
- [x] Phase 8 — Repository hygiene: `__init__.py~` renamed to `__init__.py` + `*~` ignored, `DEBUG=False` in base, env-driven prod hardening (rejects placeholder secret, HTTPS redirect, HSTS, CSRF origins, proxy header) with tests, files deleted only on commit (`delete_file_on_commit`), tests use a temp `MEDIA_ROOT`, exact lookups for lowercase usernames/commnames, dead permission code removed, AuditLog read-only in admin (457 tests)
- [x] Phase 9 — Docs: ER (Comment 2000, media 1..4), DECISIONS, frontend PLAN facts, REQUIREMENTS_CHANGES pending list, README

## Review after polish 2 (2026-11-18)
- [x] Heartbeat fixed (200 instead of 401); demo shows popular suggestions; `/account`, `/moderation`, `/c/:commname/settings`; moderated-community leaders can transfer and members can leave (and see it under "Minhas"); chat bubble applied to comments and letters; store previews validated; banner first on phones; tests protect the real media folder; REQUIREMENTS_CHANGES updated. 637 tests

## Demo by people and badges under the name (2026-11-18)
- [x] `UserName` compact/full: the name is never pushed out by badges (below it, most expensive badge + "+N" in lists, all badges in the profile header)
- [x] Demo rewritten around 16 people with character avatars, own pets, ~135 posts, threads, letters and bubblepops; breed-matched photos with no repeats; personal sections; 45 days of history. 648 tests

## Notes
- Do NOT run `migrate` until the custom `User` exists and `AUTH_USER_MODEL` is set (first task of 1.2).

## Batch 2 (customization, scheduler, URLs, cleanup, demo)
- [x] Phase 1 — Community customization paid by the community wallet: `scope` on items, `CommunityInventoryItem`, purchase/equip services (wallet lock, ledger on the community wallet), endpoints, `can_customize`, community "Personalização" tab with real cost/balance; tests for success, insufficient soap, roles, missing/owned items, scopes, blocked/archived and concurrency
- [x] Phase 2 — Scheduler: `run_scheduler` command + Makefile targets, advisory locks, idempotent and concurrency-safe passive soap and cleanup, per-user transactions and logged failures; tests with fake clock, `--once`, failures, overlapping runs (mutation-checked: they fail without the lock) (508 tests)
- [x] Phase 3 — URL navigation (3 commits): router + routes, real `<Link>`s, `next` return, 404, `/p/:id`, copy link, lazy chunks (main 374 kB), `VITE_API_TARGET`. Checked in a real Chrome (38 checks: guard, return URL, F5, back/forward, 404, deep links, `?q=`, `?to=`, logout, open-redirect attempt)
- [x] Phase 4 — Automated gate green (508 tests, check, migrations, ruff, build); in-browser validation is done manually by the owner. Extra: navigation was also exercised in a real Chrome via DevTools Protocol (38 checks). Manual checklist: register, login, feed, own/other profile, follow, support, comments, letters, community (create, join, post, Personalização tab), store; at each step check the URL, the back button and F5
- [x] Phase 5 — Cleanup (owner confirmed, no backup): databases `bubbles` and `bubbles_teste` dropped, recreated and migrated (30 tables, empty); `backend/media` emptied (1 file removed, folders kept); verified that pytest leaves `backend/media` untouched (temporary MEDIA_ROOT) and does not write to the dev databases
- [x] Phase 6 — Demo data and demo server: `seed_demo` (services-first, pt-BR pet content, cat/dog photos cached, idempotent, `--reset` by manifest, refuses outside demo settings/DB), `config.settings.demo`, `make demo` / `demo-reset` / `demo-frontend` / `demo-scheduler` with a guard against the dev database; 17 tests offline. Verified: seeded twice with identical row counts, reset removes only seeded data and files, demo API serves the data on :8001, dev DB untouched

## Batch 3 — polish 2 (see docs/POLISH_PLAN.md)
- [x] Phase 1 — Quick fixes: password show/hide, register without description, Portuguese messages everywhere (catalog + `pt-br`, 538 tests), responsive header/community/profile mural/natural scrolling on phones, publish button on the own profile, equipped frame/name color/badge/theme applied on profiles, feed, comments and members. Checked in Chrome at 375/768/1280 px
- [x] Phase 2 — Social and letters: `/u/:username/followers` and `/following` (paginated lists, linked from the profile, feed sidebar and "Seguidores" block); `/letters/:id` opens the detail modal from the URL (back/F5 work, 404 message); a reply shows the replied-to letter (`reply_to_summary`, clickable) and the original shows "Respondida · ver resposta" (`reply_id`, no N+1); 543 tests. Checked in Chrome at 375/768/1280 px (23 checks)
- [x] Phase 3 — Edit/delete account and community: `/account` (profile edit with photo removal, password change, e-mail change, account deletion with typed "EXCLUIR" + password + warnings), `/c/:commname/settings` (edit data/photo, transfer leadership, delete community with typed handle); `Community.deleted_at` soft delete (migration 0005); 565 tests. Checked in Chrome at 375/768/1280 px (35 checks, throwaway database)
- [x] Phase 4 — Administration: staff-only `/moderation` (users, communities, audit history; search, status filter, suspend with hours + reason, ban, restore) plus shortcuts on profiles/communities and a header icon; user suspension banner (date + reason; read-only: no posts, comments, support, letters), ban blocks login and shows the reason only after a correct password and hides profile/content; community suspension (`suspended_until`) and ban hide it from lists/search/feed and make it read-only with a banner for members, 404 for others; migrations accounts 0006, communities 0006, moderation 0002; 580 tests. Checked in Chrome at 375/768/1280 px (31 checks, throwaway database)
- [x] Phase 5 — Expanded customization and bubble effect: staff-uploaded wallpapers (`CustomizationItem.image`, bought with soap), accent color, customizable profile section (`/customization/section/`, plain text ≤40/≤500, `User.section_title/section_text`), up to 3 badges (`badge`, `badge_2`, `badge_3`; staff can grant by adding inventory in the admin), strict per-type metadata validation (hex colors, no CSS/HTML), profile PATCH rebuilds `customization_json` from the catalog; frontend: wallpaper + accent applied to the app and to the profile being viewed (CSS variables), store categories/previews, section panel, bubble-look filter on mural and grid photos (static, hover tilt only without `prefers-reduced-motion`); community banner shown larger on the community mural and editable in its settings; migrations accounts 0007, customization 0004; 625 tests. Checked in Chrome at 375/768/1280 px (35 checks, throwaway database)
- [x] Phase 6 — Final validation, demo seed and docs: `seed_demo` now creates 4 wallpapers (drawn with Pillow, one tiled), 3 accent colors, 2 profile sections, extra badges (3 per profile on 6 profiles, one staff-granted), banners for every community, a suspended user, a banned user, a deleted user, a suspended, a banned and a deleted community; reports get a stable pending/investigating/resolved mix; reset also removes catalog images. 629 tests. Validated on the real demo database in Chrome (27 checks, 375/768/1280 px, no 5xx in the server log); README and DECISIONS updated

