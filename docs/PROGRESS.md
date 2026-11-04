# Progress

## Pillar 1 — Structural
- [x] 1.1 Initial setup (backend only; frontend setup comes in the React block)
- [x] 1.2 Models (full class diagram + economy base)
  - [x] Slice 1: User & Community models (`accounts`, `communities`)
  - [x] Slice 2: Economy base (`EconomySettings`, `Wallet`, `SoapTransaction`, services, exceptions)
  - [x] Slice 3: Content & Social models (`content`, `social`, origin links on `SoapTransaction`)
  - [x] ER diagram (`docs/ER.md`) generated
- [ ] 1.3 Users (CRUD)
- [ ] 1.4 Communities (CRUD)

## Notes
- Do NOT run `migrate` until the custom `User` exists and `AUTH_USER_MODEL` is set (first task of 1.2).