"""Community permissions are not DRF permission classes.

They are enforced in `services.py` (`_check_admin_or_leader_permission`, `_check_leader_permission`)
from the member's role and state, and exposed to the UI through
`selectors.compute_community_permissions` (the `permissions` map of the detail endpoint).
"""
