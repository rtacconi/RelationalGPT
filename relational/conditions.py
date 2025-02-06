#!/usr/bin/env python3
"""
relational/conditions.py

A Python DSL for expressing relational constraints (ported from a Clojure DSL).
"""

# -----------------------------------------------------------------------------
# DSL Implementation: Relational Algebra Helpers
# -----------------------------------------------------------------------------

def restrict(rel, predicate):
    """Return all rows in rel that satisfy the predicate."""
    return [row for row in rel if predicate(row)]


def join(rel1, rel2):
    """
    Perform a natural join on two relations (lists of dictionaries).
    Here we simply join on all common keys.
    """
    if not rel1 or not rel2:
        return []
    common_keys = set(rel1[0].keys()).intersection(rel2[0].keys())
    result = []
    for row1 in rel1:
        for row2 in rel2:
            if all(row1.get(k) == row2.get(k) for k in common_keys):
                combined = row1.copy()
                combined.update(row2)
                result.append(combined)
    return result


def project(rel, *fields):
    """Project the relation to only include the given fields."""
    return [{field: row.get(field) for field in fields} for row in rel]


def extend(rel, new_field, func):
    """
    Extend each row in the relation by adding a new field computed by func.
    func is a function that receives the row (a dict) and returns the new value.
    """
    return [dict(row, **{new_field: func(row)}) for row in rel]


def summarize(rel, group_fields, aggregates):
    """
    Group the relation by the list of group_fields and then apply aggregate
    functions on each group. The aggregates argument is a dict mapping the name
    of the new field to a function that, given the list of rows in the group,
    returns an aggregate value.
    """
    groups = {}
    for row in rel:
        key = tuple(row.get(field) for field in group_fields)
        groups.setdefault(key, []).append(row)
    result = []
    for key, rows in groups.items():
        summary = {field: value for field, value in zip(group_fields, key)}
        for agg_name, agg_func in aggregates.items():
            summary[agg_name] = agg_func(rows)
        result.append(summary)
    return result


def ensure(description, condition):
    """
    Evaluate a condition (which should be a boolean expression) and either
    print a success message or raise an AssertionError.
    """
    if not condition:
        raise AssertionError(f"Constraint failed: {description}")
    else:
        print(f"Constraint passed: {description}")


# -----------------------------------------------------------------------------
# Dummy Data and Helper Functions
# -----------------------------------------------------------------------------

def price_to_price_band(price):
    """
    A simple function to map a price to a price band.
    You can replace this with a more sophisticated mapping.
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
    {"id": 2, "num_rooms": 1, "price": 150000},  # Changed from 0 to 1
    {"id": 3, "num_rooms": 2, "price": 100000},
]


Offer = [
    {"id": 101, "address": "123 Main St", "bidder_name": "Alice",
     "bidder_address": "456 Elm St", "offer_date": 20200101},
    {"id": 102, "address": "123 Main St", "bidder_name": "Bob",
     "bidder_address": "789 Maple Ave", "offer_date": 20200102},  # Changed bidder_address
    {"id": 103, "address": "789 Oak Ave", "bidder_name": "Charlie",
     "bidder_address": "321 Cedar Blvd", "offer_date": 20200103},  # Changed bidder_address
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
    # Join Offer with a projection of Acceptance (on address and decision_date)
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


def main():
    """
    Main entry point for the relational DSL.
    This function is called when you run:
        poetry run relational
    """
    try:
        run_constraints()
        print("All constraints evaluated successfully.")
    except AssertionError as e:
        print(str(e))


if __name__ == '__main__':
    main()
