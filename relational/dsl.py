# relational/dsl.py

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
    """
    return [dict(row, **{new_field: func(row)}) for row in rel]


def summarize(rel, group_fields, aggregates):
    """
    Group the relation by the list of group_fields and then apply aggregate
    functions on each group.
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
    raise an AssertionError or print a success message.
    """
    if not condition:
        raise AssertionError(f"Constraint failed: {description}")
    else:
        print(f"Constraint passed: {description}")