import pytest
from django.db import IntegrityError, transaction

from apps.accounts.tests.factories import UserFactory
from apps.communities.models import CommunityMember, MemberRole, MemberState
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory

pytestmark = pytest.mark.django_db


def test_membership_defaults_to_active_member():
    member = CommunityMemberFactory()

    assert member.role == MemberRole.MEMBER
    assert member.current_state == MemberState.ACTIVE
    assert member.joined_at is not None


def test_related_names_expose_memberships():
    community, user = CommunityFactory(), UserFactory()
    CommunityMemberFactory(community=community, user=user)

    assert community.memberships.get().user == user
    assert user.community_memberships.get().community == community


def test_user_can_belong_to_many_communities():
    user = UserFactory()

    CommunityMemberFactory(user=user)
    CommunityMemberFactory(user=user)

    assert user.community_memberships.count() == 2


def test_user_cannot_join_the_same_community_twice():
    community, user = CommunityFactory(), UserFactory()
    CommunityMemberFactory(community=community, user=user)

    with pytest.raises(IntegrityError, match="uniq_member_community_user"):
        with transaction.atomic():
            CommunityMemberFactory(community=community, user=user)


class TestOneLeaderPerCommunity:
    def test_second_leader_in_the_same_community_is_rejected(self):
        community = CommunityFactory()
        CommunityMemberFactory(community=community, role=MemberRole.LEADER)

        with pytest.raises(IntegrityError, match="uniq_one_leader_per_community"):
            with transaction.atomic():
                CommunityMemberFactory(community=community, role=MemberRole.LEADER)

    def test_promoting_a_member_to_leader_while_another_leads_is_rejected(self):
        community = CommunityFactory()
        CommunityMemberFactory(community=community, role=MemberRole.LEADER)
        member = CommunityMemberFactory(community=community)

        with pytest.raises(IntegrityError, match="uniq_one_leader_per_community"):
            with transaction.atomic():
                member.role = MemberRole.LEADER
                member.save()

    def test_each_community_can_have_its_own_leader(self):
        CommunityMemberFactory(role=MemberRole.LEADER)
        CommunityMemberFactory(role=MemberRole.LEADER)

        assert CommunityMember.objects.filter(role=MemberRole.LEADER).count() == 2

    def test_same_user_can_lead_several_communities(self):
        user = UserFactory()

        CommunityMemberFactory(user=user, role=MemberRole.LEADER)
        CommunityMemberFactory(user=user, role=MemberRole.LEADER)

        assert user.community_memberships.filter(role=MemberRole.LEADER).count() == 2

    def test_admins_and_members_are_not_limited_to_one(self):
        community = CommunityFactory()

        CommunityMemberFactory.create_batch(3, community=community, role=MemberRole.COMM_ADMIN)
        CommunityMemberFactory.create_batch(3, community=community, role=MemberRole.MEMBER)

        assert community.memberships.count() == 6

    def test_leadership_can_move_once_the_old_leader_steps_down(self):
        community = CommunityFactory()
        old = CommunityMemberFactory(community=community, role=MemberRole.LEADER)
        new = CommunityMemberFactory(community=community)

        with transaction.atomic():
            old.role = MemberRole.COMM_ADMIN
            old.save()
            new.role = MemberRole.LEADER
            new.save()

        assert community.memberships.get(role=MemberRole.LEADER) == new


class TestLeaderMustBeActive:
    @pytest.mark.parametrize("state", [MemberState.SILENCED, MemberState.BANNED])
    def test_leader_cannot_be_silenced_or_banned(self, state):
        with pytest.raises(IntegrityError, match="chk_leader_must_be_active"):
            with transaction.atomic():
                CommunityMemberFactory(role=MemberRole.LEADER, current_state=state)

    def test_active_leader_cannot_be_banned_afterwards(self):
        leader = CommunityMemberFactory(role=MemberRole.LEADER)

        with pytest.raises(IntegrityError, match="chk_leader_must_be_active"):
            with transaction.atomic():
                leader.current_state = MemberState.BANNED
                leader.save()

    @pytest.mark.parametrize("role", [MemberRole.MEMBER, MemberRole.COMM_ADMIN])
    @pytest.mark.parametrize("state", list(MemberState))
    def test_non_leaders_can_be_in_any_state(self, role, state):
        member = CommunityMemberFactory(role=role, current_state=state)

        assert member.current_state == state

    def test_banned_row_stays_so_the_person_cannot_simply_rejoin(self):
        community, user = CommunityFactory(), UserFactory()
        CommunityMemberFactory(community=community, user=user, current_state=MemberState.BANNED)

        with pytest.raises(IntegrityError, match="uniq_member_community_user"):
            with transaction.atomic():
                CommunityMemberFactory(community=community, user=user)
