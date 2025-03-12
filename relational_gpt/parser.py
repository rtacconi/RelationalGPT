# examples/real_estate/dsl.py
"""
Real Estate Application DSL

This module defines a sample real estate application using the RelationalGPT DSL.
"""

from relational.dsl import restrict, join, project, extend, summarize, ensure
from workflow.dsl import Workflow, Page, Section, Flow, Validation

# Helper functions
def price_to_price_band(price):
    """Convert a price to a price band."""
    if price >= 300000:
        return 'premium'
    elif price >= 150000:
        return 'mid'
    else:
        return 'economy'

# Define relations (data tables)
PropertyInfo = [
    {"id": 1, "address": "123 Main St", "num_rooms": 3, "price": 200000, "status": "available"},
    {"id": 2, "address": "456 Elm St", "num_rooms": 1, "price": 150000, "status": "available"},
    {"id": 3, "address": "789 Oak Ave", "num_rooms": 2, "price": 100000, "status": "available"},
    {"id": 4, "address": "321 Pine Rd", "num_rooms": 4, "price": 350000, "status": "available"},
    {"id": 5, "address": "654 Maple Dr", "num_rooms": 3, "price": 275000, "status": "sold"},
]

Offer = [
    {"id": 101, "property_id": 1, "bidder_name": "Alice", "bidder_address": "111 First St", "offer_amount": 195000, "offer_date": 20230101},
    {"id": 102, "property_id": 1, "bidder_name": "Bob", "bidder_address": "222 Second St", "offer_amount": 198000, "offer_date": 20230102},
    {"id": 103, "property_id": 3, "bidder_name": "Charlie", "bidder_address": "333 Third St", "offer_amount": 95000, "offer_date": 20230103},
    {"id": 104, "property_id": 5, "bidder_name": "David", "bidder_address": "444 Fourth St", "offer_amount": 270000, "offer_date": 20230104},
]

Acceptance = [
    {"id": 201, "property_id": 5, "offer_id": 104, "decision_date": 20230105},
]

Agent = [
    {"id": 301, "name": "John Smith", "email": "john@example.com", "phone": "555-1234"},
    {"id": 302, "name": "Jane Doe", "email": "jane@example.com", "phone": "555-5678"},
]

PropertyAgent = [
    {"property_id": 1, "agent_id": 301},
    {"property_id": 2, "agent_id": 302},
    {"property_id": 3, "agent_id": 301},
    {"property_id": 4, "agent_id": 302},
    {"property_id": 5, "agent_id": 301},
]

# Define web workflow
real_estate_workflow = Workflow("Real Estate Application")

# Home Page
real_estate_workflow.add_page(
    Page("Home", route="/")
    .set_description("Landing page with featured properties and search functionality.")
    .add_section(Section("Featured Properties", "Displays a selection of featured properties."))
    .add_section(Section("Search", "Allows users to search for properties by location, price range, and number of rooms."))
    .add_flow(Flow("View property details", "Property Details"))
    .add_flow(Flow("Search for properties", "Search Results"))
)

# Property Details Page
real_estate_workflow.add_page(
    Page("Property Details", route="/property/<property_id>")
    .set_description("Displays detailed information about a property.")
    .add_section(Section("Property Information", "Address, price, number of rooms, etc."))
    .add_section(Section("Contact Agent", "Form to contact the listing agent."))
    .add_section(Section("Make Offer", "Form to make an offer on the property."))
    .add_flow(Flow("Submit contact form", "Contact Confirmation"))
    .add_flow(Flow("Submit offer", "Offer Confirmation"))
    .add_validation(Validation("Offer amount must be a positive number."))
)

# Search Results Page
real_estate_workflow.add_page(
    Page("Search Results", route="/search")
    .set_description("Displays properties matching the search criteria.")
    .add_section(Section("Results", "List of properties matching the search criteria."))
    .add_section(Section("Filters", "Options to refine the search results."))
    .add_flow(Flow("View property details", "Property Details"))
)

# Contact Confirmation Page
real_estate_workflow.add_page(
    Page("Contact Confirmation", route="/contact-confirmation")
    .set_description("Confirms that the contact form has been submitted.")
)

# Offer Confirmation Page
real_estate_workflow.add_page(
    Page("Offer Confirmation", route="/offer-confirmation")
    .set_description("Confirms that the offer has been submitted.")
)

# Admin Page
real_estate_workflow.add_page(
    Page("Admin", route="/admin")
    .set_description("Admin dashboard for managing properties and offers.")
    .add_section(Section("Properties", "List of all properties with options to add, edit, and delete."))
    .add_section(Section("Offers", "List of all offers with options to accept or reject."))
    .add_flow(Flow("Add property", "Add Property"))
    .add_flow(Flow("Edit property", "Edit Property"))
    .add_flow(Flow("View offers for property", "Property Offers"))
)

# Add Property Page
real_estate_workflow.add_page(
    Page("Add Property", route="/admin/property/add")
    .set_description("Form to add a new property.")
    .add_validation(Validation("All required fields must be filled out."))
    .add_validation(Validation("Price must be a positive number."))
)

# Edit Property Page
real_estate_workflow.add_page(
    Page("Edit Property", route="/admin/property/<property_id>/edit")
    .set_description("Form to edit an existing property.")
    .add_validation(Validation("All required fields must be filled out."))
    .add_validation(Validation("Price must be a positive number."))
)

# Property Offers Page
real_estate_workflow.add_page(
    Page("Property Offers", route="/admin/property/<property_id>/offers")
    .set_description("List of offers for a specific property.")
    .add_flow(Flow("Accept offer", "Accept Offer"))
)

# Accept Offer Page
real_estate_workflow.add_page(
    Page("Accept Offer", route="/admin/offer/<offer_id>/accept")
    .set_description("Form to accept an offer.")
    .add_validation(Validation("Acceptance date must be provided."))
)

# Define constraints
def run_constraints():
    # No properties with no rooms
    ensure(
        "No properties with no rooms",
        len(restrict(PropertyInfo, lambda row: row['num_rooms'] < 1)) == 0
    )
    
    # No bidders bidding on their own property
    properties_with_bidders = join(
        Offer,
        project(PropertyInfo, 'id', 'address')
    )
    own_property_bids = restrict(
        properties_with_bidders,
        lambda row: row['bidder_address'] == row['address']
    )
    ensure(
        "No bidders bidding on their own property",
        len(own_property_bids) == 0
    )
    
    # No offers on sold properties
    sold_properties = restrict(PropertyInfo, lambda row: row['status'] == 'sold')
    offers_on_sold = join(
        Offer,
        project(sold_properties, 'id')
    )
    ensure(
        "No offers on already sold properties",
        len(offers_on_sold) == 0
    )
    
    # No more than 50 premium price band properties
    premium_properties = restrict(
        extend(PropertyInfo, 'price_band', lambda row: price_to_price_band(row['price'])),
        lambda row: row['price_band'] == 'premium'
    )
    ensure(
        "No more than 50 premium price band properties",
        len(premium_properties) < 50
    )
    
    # No more than 10 offers on a single property
    offers_per_property = summarize(
        Offer,
        ['property_id'],
        {'num_offers': lambda rows: len(rows)}
    )
    properties_with_many_offers = restrict(
        offers_per_property,
        lambda row: row['num_offers'] > 10
    )
    ensure(
        "No more than 10 offers on a single property",
        len(properties_with_many_offers) == 0
    )
    
    # All properties must have an agent
    properties_without_agent = restrict(
        project(PropertyInfo, 'id'),
        lambda p: len(restrict(PropertyAgent, lambda pa: pa['property_id'] == p['id'])) == 0
    )
    ensure(
        "All properties must have an agent",
        len(properties_without_agent) == 0
    )


# Run constraints if this module is executed directly
if __name__ == "__main__":
    print("Running constraints...")
    run_constraints()
    print("All constraints passed!")
    
    print("\nWorkflow:")
    print(real_estate_workflow)