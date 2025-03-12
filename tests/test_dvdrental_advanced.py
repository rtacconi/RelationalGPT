# tests/test_dvdrental_advanced.py

import pytest
from relational.dsl import restrict, join, project, extend, summarize, ensure

# =============================================================================
# Advanced DVD Rental Schema Data (Based on the PostgreSQL Sample Database)
# =============================================================================

# Country table
Country = [
    {"country_id": 1, "country": "USA", "last_update": "2023-01-01"},
    {"country_id": 2, "country": "Canada", "last_update": "2023-01-01"},
    {"country_id": 3, "country": "UK", "last_update": "2023-01-01"},
]

# City table
City = [
    {"city_id": 1, "city": "New York", "country_id": 1, "last_update": "2023-01-02"},
    {"city_id": 2, "city": "Toronto", "country_id": 2, "last_update": "2023-01-02"},
    {"city_id": 3, "city": "London", "country_id": 3, "last_update": "2023-01-02"},
]

# Address table
Address = [
    {"address_id": 1, "address": "123 Main St", "address2": "", "district": "Manhattan", "city_id": 1, "postal_code": "10001", "phone": "212-555-1234", "last_update": "2023-01-03"},
    {"address_id": 2, "address": "456 Maple Ave", "address2": "Suite 100", "district": "North York", "city_id": 2, "postal_code": "M4B1B3", "phone": "416-555-5678", "last_update": "2023-01-03"},
    {"address_id": 3, "address": "789 Baker St", "address2": "", "district": "Central", "city_id": 3, "postal_code": "SW1A 1AA", "phone": "020-555-0000", "last_update": "2023-01-03"},
]

# Language table
Language = [
    {"language_id": 1, "name": "English", "last_update": "2023-01-04"},
    {"language_id": 2, "name": "Spanish", "last_update": "2023-01-04"},
    {"language_id": 3, "name": "French", "last_update": "2023-01-04"},
]

# Category table
Category = [
    {"category_id": 1, "name": "Action", "last_update": "2023-01-05"},
    {"category_id": 2, "name": "Comedy", "last_update": "2023-01-05"},
    {"category_id": 3, "name": "Drama", "last_update": "2023-01-05"},
    {"category_id": 4, "name": "Sci-Fi", "last_update": "2023-01-05"},
]

# Film table
Film = [
    {
        "film_id": 1,
        "title": "The Matrix",
        "description": "A computer hacker learns the nature of reality.",
        "release_year": 1999,
        "language_id": 1,
        "original_language_id": None,
        "rental_duration": 3,
        "rental_rate": 2.99,
        "length": 136,
        "replacement_cost": 19.99,
        "rating": "R",
        "special_features": "Behind the scenes",
        "last_update": "2023-01-06"
    },
    {
        "film_id": 2,
        "title": "Inception",
        "description": "A thief who steals secrets through dream-sharing technology.",
        "release_year": 2010,
        "language_id": 1,
        "original_language_id": None,
        "rental_duration": 4,
        "rental_rate": 3.99,
        "length": 148,
        "replacement_cost": 24.99,
        "rating": "PG-13",
        "special_features": "Trailers",
        "last_update": "2023-01-06"
    },
    {
        "film_id": 3,
        "title": "Amélie",
        "description": "A whimsical depiction of contemporary Parisian life.",
        "release_year": 2001,
        "language_id": 3,
        "original_language_id": None,
        "rental_duration": 3,
        "rental_rate": 2.49,
        "length": 122,
        "replacement_cost": 17.99,
        "rating": "R",
        "special_features": "Commentary",
        "last_update": "2023-01-06"
    },
    {
        "film_id": 4,
        "title": "Parasite",
        "description": "A dark comedy thriller about social inequality.",
        "release_year": 2019,
        "language_id": 1,
        "original_language_id": None,
        "rental_duration": 5,
        "rental_rate": 4.99,
        "length": 132,
        "replacement_cost": 29.99,
        "rating": "R",
        "special_features": "Deleted scenes",
        "last_update": "2023-01-06"
    },
]

# Actor table
Actor = [
    {"actor_id": 1, "first_name": "Keanu", "last_name": "Reeves", "last_update": "2023-01-07"},
    {"actor_id": 2, "first_name": "Laurence", "last_name": "Fishburne", "last_update": "2023-01-07"},
    {"actor_id": 3, "first_name": "Leonardo", "last_name": "DiCaprio", "last_update": "2023-01-07"},
    {"actor_id": 4, "first_name": "Audrey", "last_name": "Tautou", "last_update": "2023-01-07"},
    {"actor_id": 5, "first_name": "Song", "last_name": "Kang-ho", "last_update": "2023-01-07"},
]

# Film_Actor table
Film_Actor = [
    {"film_id": 1, "actor_id": 1, "last_update": "2023-01-08"},  # The Matrix: Keanu Reeves
    {"film_id": 1, "actor_id": 2, "last_update": "2023-01-08"},  # The Matrix: Laurence Fishburne
    {"film_id": 2, "actor_id": 3, "last_update": "2023-01-08"},  # Inception: Leonardo DiCaprio
    {"film_id": 3, "actor_id": 4, "last_update": "2023-01-08"},  # Amélie: Audrey Tautou
    {"film_id": 4, "actor_id": 5, "last_update": "2023-01-08"},  # Parasite: Song Kang-ho
]

# Film_Category table
Film_Category = [
    {"film_id": 1, "category_id": 4, "last_update": "2023-01-09"},  # The Matrix is Sci-Fi
    {"film_id": 2, "category_id": 4, "last_update": "2023-01-09"},  # Inception is Sci-Fi
    {"film_id": 3, "category_id": 3, "last_update": "2023-01-09"},  # Amélie is Drama
    {"film_id": 4, "category_id": 3, "last_update": "2023-01-09"},  # Parasite is Drama
]

# Inventory table
Inventory = [
    {"inventory_id": 1, "film_id": 1, "store_id": 1, "last_update": "2023-01-10"},
    {"inventory_id": 2, "film_id": 2, "store_id": 1, "last_update": "2023-01-10"},
    {"inventory_id": 3, "film_id": 3, "store_id": 2, "last_update": "2023-01-10"},
    {"inventory_id": 4, "film_id": 4, "store_id": 2, "last_update": "2023-01-10"},
]

# Staff table
Staff = [
    {"staff_id": 1, "first_name": "Carol", "last_name": "White", "address_id": 1, "email": "carol@example.com", "store_id": 1, "active": True, "username": "carolw", "password": "pass", "last_update": "2023-01-11", "picture": None},
    {"staff_id": 2, "first_name": "Dave", "last_name": "Brown", "address_id": 2, "email": "dave@example.com", "store_id": 2, "active": True, "username": "daveb", "password": "pass", "last_update": "2023-01-11", "picture": None},
    {"staff_id": 3, "first_name": "Eve", "last_name": "Black", "address_id": 3, "email": "eve@example.com", "store_id": 1, "active": True, "username": "eveb", "password": "pass", "last_update": "2023-01-11", "picture": None},
]

# Store table
Store = [
    {"store_id": 1, "manager_staff_id": 1, "address_id": 1, "last_update": "2023-01-12"},
    {"store_id": 2, "manager_staff_id": 2, "address_id": 2, "last_update": "2023-01-12"},
]

# Customer table
Customer = [
    {"customer_id": 1, "store_id": 1, "first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "address_id": 1, "active": True, "create_date": "2023-01-13", "last_update": "2023-01-13"},
    {"customer_id": 2, "store_id": 2, "first_name": "Bob", "last_name": "Jones", "email": "bob@example.com", "address_id": 2, "active": True, "create_date": "2023-01-13", "last_update": "2023-01-13"},
    {"customer_id": 3, "store_id": 1, "first_name": "Charlie", "last_name": "Doe", "email": "charlie@example.com", "address_id": 1, "active": False, "create_date": "2023-01-13", "last_update": "2023-01-13"},
    {"customer_id": 4, "store_id": 1, "first_name": "Dana", "last_name": "Scully", "email": "dana@example.com", "address_id": 3, "active": True, "create_date": "2023-01-13", "last_update": "2023-01-13"},
]

# Rental table
Rental = [
    {"rental_id": 1, "rental_date": "2023-01-14 10:00:00", "inventory_id": 1, "customer_id": 1, "return_date": "2023-01-15 10:00:00", "staff_id": 1, "last_update": "2023-01-14 11:00:00"},
    {"rental_id": 2, "rental_date": "2023-01-15 12:00:00", "inventory_id": 2, "customer_id": 2, "return_date": "2023-01-16 12:00:00", "staff_id": 1, "last_update": "2023-01-15 13:00:00"},
    {"rental_id": 3, "rental_date": "2023-01-16 14:00:00", "inventory_id": 3, "customer_id": 3, "return_date": "2023-01-17 14:00:00", "staff_id": 3, "last_update": "2023-01-16 15:00:00"},
    {"rental_id": 4, "rental_date": "2023-01-17 16:00:00", "inventory_id": 4, "customer_id": 4, "return_date": "2023-01-18 16:00:00", "staff_id": 2, "last_update": "2023-01-17 17:00:00"},
]

# Payment table
Payment = [
    {"payment_id": 1, "customer_id": 1, "rental_id": 1, "amount": 2.99, "payment_date": "2023-01-15 11:00:00", "last_update": "2023-01-15 11:00:00"},
    {"payment_id": 2, "customer_id": 2, "rental_id": 2, "amount": 3.99, "payment_date": "2023-01-16 12:30:00", "last_update": "2023-01-16 12:30:00"},
    {"payment_id": 3, "customer_id": 3, "rental_id": 3, "amount": 2.49, "payment_date": "2023-01-17 14:30:00", "last_update": "2023-01-17 14:30:00"},
    {"payment_id": 4, "customer_id": 4, "rental_id": 4, "amount": 4.99, "payment_date": "2023-01-18 16:30:00", "last_update": "2023-01-18 16:30:00"},
]

# =============================================================================
# Advanced Integrity Constraints Using the DSL
# =============================================================================

def run_dvdrental_advanced_constraints():
    # (A) Every city must reference a valid country.
    city_country = join(City, Country)
    ensure("Every city must reference a valid country", len(city_country) == len(City))
    
    # (B) Every address must reference a valid city.
    addr_city = join(Address, City)
    ensure("Every address must reference a valid city", len(addr_city) == len(Address))
    
    # (C) Every customer must reference a valid store and valid address.
    cust_store = join(Customer, Store)
    ensure("Every customer must reference a valid store", len(cust_store) == len(Customer))
    cust_addr = join(Customer, Address)
    ensure("Every customer must reference a valid address", len(cust_addr) == len(Customer))
    
    # (D) Every film must reference a valid language.
    film_lang = join(Film, Language)
    ensure("Every film must reference a valid language", len(film_lang) == len(Film))
    
    # (E) If a film has an original_language_id, it must reference a valid language.
    films_with_orig = [f for f in Film if f["original_language_id"] is not None]
    if films_with_orig:
        films_orig_join = join(films_with_orig, Language)
        ensure("Films with original_language_id must reference a valid language", len(films_orig_join) == len(films_with_orig))
    
    # (F) Every inventory record must reference a valid film and store.
    inv_film = join(Inventory, Film)
    ensure("Every inventory record must reference a valid film", len(inv_film) == len(Inventory))
    inv_store = join(Inventory, Store)
    ensure("Every inventory record must reference a valid store", len(inv_store) == len(Inventory))
    
    # (G) Every rental must reference a valid inventory, customer, and staff.
    rental_inv = join(Rental, Inventory)
    ensure("Every rental must reference a valid inventory", len(rental_inv) == len(Rental))
    rental_cust = join(Rental, Customer)
    ensure("Every rental must reference a valid customer", len(rental_cust) == len(Rental))
    rental_staff = join(Rental, Staff)
    ensure("Every rental must reference a valid staff", len(rental_staff) == len(Rental))
    
    # (H) Every payment must reference a valid rental and customer.
    payment_rental = join(Payment, Rental)
    ensure("Every payment must reference a valid rental", len(payment_rental) == len(Payment))
    payment_cust = join(Payment, Customer)
    ensure("Every payment must reference a valid customer", len(payment_cust) == len(Payment))
    
    # (I) Payment amount should match the film's rental_rate.
    # Join Rental -> Inventory -> Film, then join with Payment on rental_id.
    rental_inv_join = join(Rental, Inventory)
    rental_inv_film = join(rental_inv_join, Film)
    full_payment_info = join(rental_inv_film, Payment)
    violations = restrict(full_payment_info, lambda row: abs(row.get("amount", 0) - row.get("rental_rate", 0)) > 0.001)
    ensure("Every payment amount must match the film's rental rate", len(violations) == 0)
    
    # (J) Every film_actor record must reference a valid film and actor.
    film_actor_film = join(Film_Actor, Film)
    ensure("Every film_actor record must reference a valid film", len(film_actor_film) == len(Film_Actor))
    film_actor_actor = join(Film_Actor, Actor)
    ensure("Every film_actor record must reference a valid actor", len(film_actor_actor) == len(Film_Actor))
    
    # (K) Every film_category record must reference a valid film and category.
    film_cat_film = join(Film_Category, Film)
    ensure("Every film_category record must reference a valid film", len(film_cat_film) == len(Film_Category))
    film_cat_cat = join(Film_Category, Category)
    ensure("Every film_category record must reference a valid category", len(film_cat_cat) == len(Film_Category))
    
    # (L) Every store's manager must exist in Staff and be associated with that store.
    for store in Store:
        manager = [s for s in Staff if s["staff_id"] == store["manager_staff_id"]]
        ensure("Store manager must exist", len(manager) == 1)
        ensure("Store manager must be associated with the store", manager[0]["store_id"] == store["store_id"])
    
    # (M) Every rental's return_date must be later than its rental_date.
    late_returns = restrict(Rental, lambda row: row["return_date"] <= row["rental_date"])
    ensure("Every rental's return_date must be later than its rental_date", len(late_returns) == 0)
    
    # (N) Every film's rental_rate should be less than its replacement_cost.
    rate_vs_cost = restrict(Film, lambda row: row["rental_rate"] >= row["replacement_cost"])
    ensure("Every film's rental_rate should be less than its replacement_cost", len(rate_vs_cost) == 0)
    
    # (O) Every film's length should be greater than 0.
    non_positive_length = restrict(Film, lambda row: row["length"] <= 0)
    ensure("Every film's length should be greater than 0", len(non_positive_length) == 0)
    
    # (P) Every active customer must have at least one rental.
    active_customers = [c for c in Customer if c["active"]]
    customers_with_rentals = set(r["customer_id"] for r in Rental)
    active_cust_ids = set(c["customer_id"] for c in active_customers)
    ensure("Every active customer must have at least one rental", active_cust_ids.issubset(customers_with_rentals))


# =============================================================================
# Pytest Test Function for Advanced DVD Rental Schema
# =============================================================================

def test_dvdrental_advanced_constraints():
    """
    This test executes the advanced DVD Rental integrity constraints.
    If any constraint fails, the test will fail.
    """
    run_dvdrental_advanced_constraints()
