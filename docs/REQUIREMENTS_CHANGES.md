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
