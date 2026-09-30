import pytest
from api.controllers import Delivery
from django_mock_queries.query import MockSet, MockModel

#Each case: (quantities of each line item in the order, delivery distance, expected fee).
#Tiers: > 10 items AND > 5 distance -> 7.50; > 5 items AND > 3 distance -> 5; otherwise the 3.50 default.
@pytest.mark.parametrize("quantities, delivery_distance, expected", [
  #Top tier
  pytest.param([5, 5, 5], 6, 7.5, id="LotsOfItems"),
  #Middle tier
  pytest.param([2, 2, 2], 4, 5, id="MiddleOfTheRoadItems"),
  #Enough items for the top tier, but distance stays in the middle tier: "and" is required.
  pytest.param([11], 4, 5, id="LotsOfItemsShortDistance"),
  #Exactly 10 items and 5 distance sit on the boundary (strict >), so this falls to the middle tier.
  pytest.param([10], 5, 5, id="TopTierItemBoundaryNotExceeded"),
  #One item over the boundary, distance still on the boundary.
  pytest.param([11], 5, 5, id="TopTierItemBoundaryExceeded"),
  #Default fee
  pytest.param([3, 1], 2, 3.5, id="LittleItems"),
  #A long distance alone shouldn't trigger a higher tier without enough items.
  pytest.param([2], 10, 3.5, id="LongDistanceFewItems"),
  #Exactly 5 items should not reach the middle tier's item threshold.
  pytest.param([5], 4, 3.5, id="MiddleTierItemBoundaryNotExceeded"),
  #Enough items for the middle tier, but distance sits exactly on its boundary.
  pytest.param([6], 3, 3.5, id="MiddleTierDistanceBoundaryNotExceeded"),
  #No items in the order at all.
  pytest.param([], 10, 3.5, id="EmptyOrder"),
])
def test_DeliveryCost(quantities, delivery_distance, expected):
  #Arrange
  order = MockSet()
  for quantity in quantities:
    order.add(MockModel(quantity=quantity))
  #Act
  cost = Delivery.calculate(order, delivery_distance)
  #Assert
  assert cost == expected
