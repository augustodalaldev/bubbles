# Requirements changes

## Economy values (2026-11-03) — supersede soap-economy.md defaults
| Event | Value | EconomySettings field |
|---|---|---|
| Signup grant | +20 | `signup_grant` |
| Support (like) | donor -1, author +1 (+1 community wallet on community content) | `support_cost`, `author_credit`, `community_credit` |
| Comment | free | - |
| Publish bubblegram on profile | -10 (new) | `bubblegram_profile_cost` |
| Publish bubblegram in community | -10 (new) | `bubblegram_community_cost` |
| Publish bubblepop | -ceil(hours / 4), min 1h, max 48h (new) | `bubblepop_hours_per_soap` = 4, `bubblepop_min_hours`, `bubblepop_max_hours` |
| Found community | -300 (moves to the community wallet) | `founding_cost` |
| Passive earning | +5 soap per 5 minutes of use, capped at 15/day (3 ticks) | `default_passive_earn_rate` = 5, `passive_interval_minutes` = 5, `passive_daily_cap` = 15 |

## Field limits & Profile customizations (2026-11-04)
- **User name & description limits**: User `name` limit reduced to 50 characters (from 100), and `description` limit reduced to 250 characters (from 500). Community `name` (60) and `description` (500) remain unchanged.
- **Visual customizations (`customization_json`)**: Both `User` and `Community` include a `customization_json` field (`JSONField`, default `{}`) to store visual customization settings (background colors, profile borders, badges, etc.) purchased with soap.
- **SoapTransaction action type**: Confirmed and tested `SPEND_CUSTOMIZATION` as debit action type in `SoapTransaction` representing soap expenditures on visual customizations by users or communities.

## Pending requirements found in the review (2026-11-17) — for the owner to decide
Documented in the requirements but not available in the UI (backend exists unless noted). Not implemented as part of the integration work.
- RF002: edit profile (name, description, photo, birth date) and delete account (`PATCH`/`DELETE /users/me/`).
- Wallet statement (`GET /users/me/wallet/`).
- RF013/RF015: member moderation (silence/ban), promote/demote admins, transfer leadership, archive and edit community info/photo (`/communities/{c}/members/...`, `transfer-leadership`, `archive`).
- ~~RF014 / S4: customizing a community with the community wallet~~ — implemented (see DECISIONS: Community customization).
- RF016/RF017: reports (`POST /reports/`) and system administration (`/admin/*`) have no screens; use the Django Admin.
- Email verification and password reset (Q6, deferred).
- Scheduler for `distribute_passive_soap` and `cleanup_expired_bubblepops` (cron/CronJob/Celery).

