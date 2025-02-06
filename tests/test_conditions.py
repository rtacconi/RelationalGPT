# tests/test_conditions.py
import pytest
from relational.dsl import restrict, join, project, extend, summarize, ensure

# -----------------------------------------------------------------------------
# Dummy Data and Helper Functions (for testing the DSL conditions)
# -----------------------------------------------------------------------------

def price_to_price_band(price):
    """
    A simple function to map a price to a price band.
    """
    if price >= 300000:
        return 'premium'
    elif price >= 150000:
        return 'mid'
    else:
        return 'economy'


# Example relations represented as lists of dictionaries.
PropertyInfo = [
    {"id": 1, "num_rooms": 3, "price": 200000},
    {"id": 2, "num_rooms": 1, "price": 150000},  # Adjusted to pass constraint.
    {"id": 3, "num_rooms": 2, "price": 100000},
]

Offer = [
    {"id": 101, "address": "123 Main St", "bidder_name": "Alice",
     "bidder_address": "456 Elm St", "offer_date": 20200101},
    {"id": 102, "address": "123 Main St", "bidder_name": "Bob",
     "bidder_address": "789 Maple Ave", "offer_date": 20200102},
    {"id": 103, "address": "789 Oak Ave", "bidder_name": "Charlie",
     "bidder_address": "321 Cedar Blvd", "offer_date": 20200103},
]

Acceptance = [
    {"id": 201, "address": "123 Main St", "decision_date": 20200105},
    {"id": 202, "address": "789 Oak Ave", "decision_date": 20200104},
]

PropertyForWebSite = [
    {"id": 1, "price": 350000},
    {"id": 2, "price": 150000},
    {"id": 3, "price": 80000},
]


# -----------------------------------------------------------------------------
# DSL Conditions (Ported from Clojure DSL)
# -----------------------------------------------------------------------------

def run_constraints():
    # 1. No properties with no rooms.
    ensure(
        "No properties with no rooms",
        len(restrict(PropertyInfo, lambda row: row['num_rooms'] < 1)) == 0
    )

    # 2. No bidders bidding on their own property.
    ensure(
        "No bidders bidding on their own property",
        len(restrict(Offer, lambda row: row['bidder_address'] == row['address'])) == 0
    )

    # 3. No offers on sold properties.
    joined_offers = join(Offer, project(Acceptance, 'address', 'decision_date'))
    ensure(
        "No offers on sold properties",
        len(restrict(joined_offers, lambda row: row['offer_date'] > row['decision_date'])) == 0
    )

    # 4. No more than 50 premium price band properties on website.
    extended_properties = extend(PropertyForWebSite, 'price_band', lambda row: price_to_price_band(row['price']))
    ensure(
        "No more than 50 premium price band properties on website",
        len(restrict(extended_properties, lambda row: row['price_band'] == 'premium')) < 50
    )

    # 5. No more than 10 offers by a single bidder on a single property.
    summarized_offers = summarize(
        Offer,
        ['address', 'bidder_name', 'bidder_address'],
        {'num_offers': lambda rows: len(rows)}
    )
    ensure(
        "No more than 10 offers by a single bidder on a single property",
        len(restrict(summarized_offers, lambda row: row['num_offers'] > 10)) == 0
    )


# -----------------------------------------------------------------------------
# Pytest Test Function
# -----------------------------------------------------------------------------

def test_run_constraints():
    """
    This test executes the DSL constraints.
    If any constraint fails (i.e. ensure() raises an AssertionError),
    this test will fail.
    """
    run_constraints()
