import pytest
from relational.dsl import restrict, join, project, extend, summarize, ensure

#
# This test demonstrates a typical example from programming literature:
# ensuring that every employee's salary is at least the minimum salary of
# the department they belong to.

def test_employee_department_constraints():
    # Dummy data: Departments with a defined minimum salary.
    Departments = [
        {"dept_id": 1, "dept_name": "Engineering", "min_salary": 60000},
        {"dept_id": 2, "dept_name": "Sales", "min_salary": 40000},
    ]
    
    # Dummy data: Employees belonging to departments.
    # In this passing example, every employee meets the department's salary requirement.
    Employees = [
        {"emp_id": 101, "name": "Alice", "dept_id": 1, "salary": 75000},
        {"emp_id": 102, "name": "Bob", "dept_id": 1, "salary": 65000},
        {"emp_id": 103, "name": "Charlie", "dept_id": 2, "salary": 45000},
        {"emp_id": 104, "name": "David", "dept_id": 2, "salary": 40000},
    ]
    
    # Join Employees and Departments on the common key 'dept_id'.
    joined_data = join(Employees, Departments)
    
    # Restrict the joined data to rows where an employee's salary is less than the department's min_salary.
    violations = restrict(joined_data, lambda row: row['salary'] < row['min_salary'])
    
    # Enforce that there are no violations.
    ensure("Every employee meets the minimum department salary requirement", len(violations) == 0)

    # Optionally, you can assert that violations is empty to ensure the test fails if the constraint is not met.
    assert len(violations) == 0, "Some employees have a salary below the department minimum!"