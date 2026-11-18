from concurrent.futures import ThreadPoolExecutor

import pytest
from django.db import connection

from apps.accounts.tests.factories import UserFactory
from apps.communities.models import MemberRole
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.core.exceptions import DomainError
from apps.customization.models import CommunityInventoryItem, CustomizationScope
from apps.customization.services import purchase_community_item
from apps.customization.tests.factories import CustomizationItemFactory
from apps.economy.exceptions import InsufficientSoap
from apps.economy.models import ActionType, SoapTransaction, Wallet

pytestmark = pytest.mark.django_db(transaction=True)


def setup_community(balance):
    community = CommunityFactory()
    Wallet.objects.create(community=community, soap_balance=balance)
    leader = UserFactory()
    admin = UserFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    CommunityMemberFactory(community=community, user=admin, role=MemberRole.COMM_ADMIN)
    return community, leader, admin


def run_parallel(calls):
    def attempt(call):
        connection.close()  # one DB connection per thread
        try:
            call()
            return "ok"
        except InsufficientSoap:
            return "insufficient"
        except DomainError as exc:
            return exc.code
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=len(calls)) as pool:
        return [f.result() for f in [pool.submit(attempt, c) for c in calls]]


def test_two_different_items_with_soap_for_one_only_one_succeeds():
    community, leader, admin = setup_community(balance=30)
    a = CustomizationItemFactory(scope=CustomizationScope.COMMUNITY, price=30)
    b = CustomizationItemFactory(scope=CustomizationScope.COMMUNITY, price=30)

    results = run_parallel(
        [
            lambda: purchase_community_item(actor=leader, community=community, item=a),
            lambda: purchase_community_item(actor=admin, community=community, item=b),
        ]
    )

    assert sorted(results) == ["insufficient", "ok"]
    assert Wallet.objects.get(community=community).soap_balance == 0
    assert CommunityInventoryItem.objects.filter(community=community).count() == 1
    spent = SoapTransaction.objects.filter(
        wallet__community=community, action_type=ActionType.SPEND_CUSTOMIZATION
    )
    assert spent.count() == 1


def test_same_item_bought_concurrently_is_charged_once():
    community, leader, admin = setup_community(balance=100)
    item = CustomizationItemFactory(scope=CustomizationScope.COMMUNITY, price=30)

    results = run_parallel(
        [
            lambda: purchase_community_item(actor=leader, community=community, item=item),
            lambda: purchase_community_item(actor=admin, community=community, item=item),
        ]
    )

    assert sorted(results) == ["already_owned", "ok"]
    assert Wallet.objects.get(community=community).soap_balance == 70
    assert CommunityInventoryItem.objects.filter(community=community).count() == 1
    assert (
        SoapTransaction.objects.filter(
            wallet__community=community, action_type=ActionType.SPEND_CUSTOMIZATION
        ).count()
        == 1
    )
