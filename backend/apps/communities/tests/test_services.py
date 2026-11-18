import pytest
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.communities.models import Community, CommunityMember, MemberRole, MemberState
from apps.communities.services import (
    archive_community,
    create_community,
    demote_member,
    join_community,
    leave_community,
    moderate_member,
    promote_member,
    transfer_leadership,
    update_community,
    update_guidelines,
)
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.core.exceptions import DomainError
from apps.economy.exceptions import InsufficientSoap
from apps.economy.models import ActionType, EconomySettings, SoapTransaction, Wallet

pytestmark = pytest.mark.django_db


def test_create_community_success():
    settings_obj = EconomySettings.load()
    creator = UserFactory()
    Wallet.objects.create(user=creator, soap_balance=settings_obj.founding_cost + 50)

    community = create_community(
        creator=creator,
        commname="bubble_crafters",
        name="Bubble Crafters",
        description="A warm place for crafting bubbles.",
        guidelines="Be polite and gentle.",
    )

    assert community.pk is not None
    assert community.commname == "bubble_crafters"
    assert community.name == "Bubble Crafters"
    assert community.member_count == 1
    assert community.is_archived is False

    # Leader membership created
    membership = CommunityMember.objects.get(community=community, user=creator)
    assert membership.role == MemberRole.LEADER
    assert membership.current_state == MemberState.ACTIVE

    # Creator wallet debited, community wallet credited
    creator.wallet.refresh_from_db()
    assert creator.wallet.soap_balance == 50

    comm_wallet = Wallet.objects.get(community=community)
    assert comm_wallet.soap_balance == settings_obj.founding_cost
    assert comm_wallet.passive_earn_rate is None

    # Ledger rows
    debit_tx = SoapTransaction.objects.get(
        wallet=creator.wallet, action_type=ActionType.DEBIT_FOUNDING
    )
    assert debit_tx.amount == -settings_obj.founding_cost
    assert debit_tx.balance_after == 50

    credit_tx = SoapTransaction.objects.get(
        wallet=comm_wallet, action_type=ActionType.CREDIT_FOUNDING
    )
    assert credit_tx.amount == settings_obj.founding_cost
    assert credit_tx.balance_after == settings_obj.founding_cost


def test_create_community_insufficient_soap():
    creator = UserFactory()
    Wallet.objects.create(user=creator, soap_balance=20)  # less than 300

    with pytest.raises(InsufficientSoap):
        create_community(
            creator=creator,
            commname="poor_founders",
            name="Poor Founders",
        )

    # Invariant: Nothing created on failure
    assert not Community.objects.filter(commname="poor_founders").exists()
    assert not Wallet.objects.filter(community__commname="poor_founders").exists()


def test_create_community_validations():
    creator = UserFactory()
    Wallet.objects.create(user=creator, soap_balance=500)

    # Format
    with pytest.raises(DomainError) as exc_info:
        create_community(creator=creator, commname="ab", name="Too Short")
    assert exc_info.value.code == "invalid_commname"

    # Reserved
    with pytest.raises(DomainError) as exc_info:
        create_community(creator=creator, commname="admin", name="Admin Comm")
    assert exc_info.value.code == "reserved_commname"

    # Duplicate
    CommunityFactory(commname="existing_comm")
    with pytest.raises(DomainError) as exc_info:
        create_community(creator=creator, commname="EXISTING_COMM", name="Duplicate")
    assert exc_info.value.code == "commname_already_registered"

    # Name too long (>60)
    with pytest.raises(DomainError) as exc_info:
        create_community(creator=creator, commname="valid_comm", name="x" * 61)
    assert exc_info.value.code == "invalid_name"


def test_update_community_success():
    leader = UserFactory()
    community = CommunityFactory(name="Old Name", description="Old Desc")
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)

    updated = update_community(
        actor=leader,
        community=community,
        name="New Name",
        description="New Desc",
    )

    community.refresh_from_db()
    assert updated.name == "New Name"
    assert updated.description == "New Desc"


def test_update_guidelines_leader_only():
    leader = UserFactory()
    admin = UserFactory()
    community = CommunityFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    CommunityMemberFactory(community=community, user=admin, role=MemberRole.COMM_ADMIN)

    # Admin cannot edit guidelines
    with pytest.raises(DomainError) as exc_info:
        update_guidelines(actor=admin, community=community, guidelines="Admin rules")
    assert exc_info.value.code == "permission_denied"

    # Leader can
    updated = update_guidelines(actor=leader, community=community, guidelines="Leader rules")
    assert updated.guidelines == "Leader rules"


def test_join_community_success_and_member_count():
    community = CommunityFactory(member_count=1)
    user = UserFactory()

    membership = join_community(user=user, community=community)
    assert membership.role == MemberRole.MEMBER
    assert membership.current_state == MemberState.ACTIVE

    community.refresh_from_db()
    assert community.member_count == 2


def test_join_community_already_member():
    community = CommunityFactory()
    user = UserFactory()
    CommunityMemberFactory(community=community, user=user, role=MemberRole.MEMBER)

    with pytest.raises(DomainError) as exc_info:
        join_community(user=user, community=community)
    assert exc_info.value.code == "already_member"


def test_join_community_banned_user():
    community = CommunityFactory()
    user = UserFactory()
    CommunityMemberFactory(
        community=community, user=user, role=MemberRole.MEMBER, current_state=MemberState.BANNED
    )

    with pytest.raises(DomainError) as exc_info:
        join_community(user=user, community=community)
    assert exc_info.value.code == "banned_from_community"


def test_leave_community_success():
    community = CommunityFactory(member_count=3)
    user = UserFactory()
    CommunityMemberFactory(community=community, user=user, role=MemberRole.MEMBER)

    leave_community(user=user, community=community)

    assert not CommunityMember.objects.filter(community=community, user=user).exists()
    community.refresh_from_db()
    assert community.member_count == 2


def test_leave_community_leader_blocked():
    community = CommunityFactory(member_count=1)
    leader = UserFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)

    with pytest.raises(DomainError) as exc_info:
        leave_community(user=leader, community=community)
    assert exc_info.value.code == "leader_cannot_leave"


def test_moderate_member_silence_unsilence():
    leader = UserFactory()
    member = UserFactory()
    community = CommunityFactory(member_count=2)
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    membership = CommunityMemberFactory(
        community=community, user=member, role=MemberRole.MEMBER, current_state=MemberState.ACTIVE
    )

    # Silence
    moderate_member(
        actor=leader,
        community=community,
        target_username=member.username,
        new_state=MemberState.SILENCED,
    )
    membership.refresh_from_db()
    assert membership.current_state == MemberState.SILENCED
    community.refresh_from_db()
    assert community.member_count == 2  # silenced still counts in member_count

    # Unsilence
    moderate_member(
        actor=leader,
        community=community,
        target_username=member.username,
        new_state=MemberState.ACTIVE,
    )
    membership.refresh_from_db()
    assert membership.current_state == MemberState.ACTIVE
    community.refresh_from_db()
    assert community.member_count == 2


def test_moderate_member_ban_unban_and_member_count():
    leader = UserFactory()
    member = UserFactory()
    community = CommunityFactory(member_count=2)
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    membership = CommunityMemberFactory(
        community=community, user=member, role=MemberRole.MEMBER, current_state=MemberState.ACTIVE
    )

    # Ban
    moderate_member(
        actor=leader,
        community=community,
        target_username=member.username,
        new_state=MemberState.BANNED,
    )
    membership.refresh_from_db()
    assert membership.current_state == MemberState.BANNED
    community.refresh_from_db()
    assert community.member_count == 1  # banned no longer counts

    # Unban
    moderate_member(
        actor=leader,
        community=community,
        target_username=member.username,
        new_state=MemberState.ACTIVE,
    )
    membership.refresh_from_db()
    assert membership.current_state == MemberState.ACTIVE
    community.refresh_from_db()
    assert community.member_count == 2


def test_moderate_member_admin_cannot_moderate_other_admin_or_leader():
    leader = UserFactory()
    admin1 = UserFactory()
    admin2 = UserFactory()
    community = CommunityFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    CommunityMemberFactory(community=community, user=admin1, role=MemberRole.COMM_ADMIN)
    CommunityMemberFactory(community=community, user=admin2, role=MemberRole.COMM_ADMIN)

    # Admin1 tries to silence Admin2
    with pytest.raises(DomainError) as exc_info:
        moderate_member(
            actor=admin1,
            community=community,
            target_username=admin2.username,
            new_state=MemberState.SILENCED,
        )
    assert exc_info.value.code == "permission_denied"

    # Admin1 tries to silence Leader
    with pytest.raises(DomainError) as exc_info:
        moderate_member(
            actor=admin1,
            community=community,
            target_username=leader.username,
            new_state=MemberState.SILENCED,
        )
    assert exc_info.value.code == "permission_denied"


def test_promote_and_demote_member():
    leader = UserFactory()
    member = UserFactory()
    community = CommunityFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    CommunityMemberFactory(
        community=community, user=member, role=MemberRole.MEMBER, current_state=MemberState.ACTIVE
    )

    # Promote to admin
    promoted = promote_member(actor=leader, community=community, target_username=member.username)
    assert promoted.role == MemberRole.COMM_ADMIN

    # Demote back to member
    demoted = demote_member(actor=leader, community=community, target_username=member.username)
    assert demoted.role == MemberRole.MEMBER


def test_transfer_leadership():
    old_leader = UserFactory()
    new_leader = UserFactory()
    community = CommunityFactory()
    old_membership = CommunityMemberFactory(
        community=community, user=old_leader, role=MemberRole.LEADER
    )
    new_membership = CommunityMemberFactory(
        community=community,
        user=new_leader,
        role=MemberRole.MEMBER,
        current_state=MemberState.ACTIVE,
    )

    transfer_leadership(
        actor=old_leader, community=community, new_leader_username=new_leader.username
    )

    old_membership.refresh_from_db()
    new_membership.refresh_from_db()

    assert new_membership.role == MemberRole.LEADER
    assert old_membership.role == MemberRole.COMM_ADMIN

    # Guarantee single leader constraint holds
    assert CommunityMember.objects.filter(community=community, role=MemberRole.LEADER).count() == 1


def test_archive_community():
    leader = UserFactory()
    community = CommunityFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)

    archived = archive_community(actor=leader, community=community)
    assert archived.is_archived is True
    assert archived.archived_at is not None

    # Actions blocked on archived community
    with pytest.raises(DomainError) as exc_info:
        update_community(actor=leader, community=community, name="Should Fail")
    assert exc_info.value.code == "community_archived"

    other_user = UserFactory()
    with pytest.raises(DomainError) as exc_info:
        join_community(user=other_user, community=community)
    assert exc_info.value.code == "community_archived"


def test_banned_member_cannot_leave_and_ban_row_stays():
    community = CommunityFactory(member_count=1)
    user = UserFactory()
    CommunityMemberFactory(community=community, user=user, current_state=MemberState.BANNED)

    with pytest.raises(DomainError) as exc:
        leave_community(user=user, community=community)

    assert exc.value.code == "member_banned"
    assert CommunityMember.objects.filter(community=community, user=user).exists()
    community.refresh_from_db()
    assert community.member_count == 1


def test_banned_member_cannot_rejoin_after_failed_leave():
    community = CommunityFactory()
    user = UserFactory()
    CommunityMemberFactory(community=community, user=user, current_state=MemberState.BANNED)
    with pytest.raises(DomainError):
        leave_community(user=user, community=community)
    with pytest.raises(DomainError):
        join_community(user=user, community=community)


def test_community_customization_json_is_rejected_until_purchases_exist():
    leader = UserFactory()
    community = CommunityFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)

    with pytest.raises(DomainError) as exc:
        update_community(
            actor=leader, community=community, customization_json={"primary": "#ff00ff"}
        )
    assert exc.value.code == "customization_not_available"

    # Clearing it is still allowed
    update_community(actor=leader, community=community, customization_json={})


def test_create_community_rejects_free_customization():
    creator = UserFactory()
    Wallet.objects.create(user=creator, soap_balance=1000)
    with pytest.raises(DomainError) as exc:
        create_community(
            creator=creator,
            commname="styled_comm",
            name="Styled",
            customization_json={"primary": "#ff00ff"},
        )
    assert exc.value.code == "customization_not_available"
    assert not Community.objects.filter(commname="styled_comm").exists()
    creator.wallet.refresh_from_db()
    assert creator.wallet.soap_balance == 1000


@pytest.mark.parametrize("operation", ["update", "guidelines", "archive", "moderate", "promote"])
def test_blocked_community_rejects_management_by_leader(operation):
    leader, member = UserFactory(), UserFactory()
    community = CommunityFactory(blocked_at=timezone.now())
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    CommunityMemberFactory(community=community, user=member)

    calls = {
        "update": lambda: update_community(actor=leader, community=community, name="x"),
        "guidelines": lambda: update_guidelines(actor=leader, community=community, guidelines="x"),
        "archive": lambda: archive_community(actor=leader, community=community),
        "moderate": lambda: moderate_member(
            actor=leader,
            community=community,
            target_username=member.username,
            new_state=MemberState.SILENCED,
        ),
        "promote": lambda: promote_member(
            actor=leader, community=community, target_username=member.username
        ),
    }
    with pytest.raises(DomainError) as exc:
        calls[operation]()
    assert exc.value.code == "community_blocked"


def test_staff_can_still_manage_a_blocked_community():
    staff = UserFactory(is_staff=True)
    community = CommunityFactory(blocked_at=timezone.now())
    updated = update_community(actor=staff, community=community, name="Renamed by staff")
    assert updated.name == "Renamed by staff"


def test_member_count_stays_consistent_across_ban_unban_cycle():
    leader, member = UserFactory(), UserFactory()
    community = CommunityFactory(member_count=2)
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    CommunityMemberFactory(community=community, user=member)

    for state in (MemberState.BANNED, MemberState.BANNED, MemberState.ACTIVE):
        moderate_member(
            actor=leader,
            community=community,
            target_username=member.username,
            new_state=state,
        )
    community.refresh_from_db()
    assert community.member_count == 2
