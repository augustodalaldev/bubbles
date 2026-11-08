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

## Notes
- Do NOT run `migrate` until the custom `User` exists and `AUTH_USER_MODEL` is set (first task of 1.2).