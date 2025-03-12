# ---------------------------------------------------------------------------
# Sample Workflow Definition for the DVD Rental Web App
# ---------------------------------------------------------------------------

dvd_workflow = Workflow("DVD Rental Web App")

# Home Page: Landing page with search and navigation.
dvd_workflow.add_page(
    Page("Home", route="/")
    .set_description(
        "Landing page featuring:\n"
        "  - A search bar for movies.\n"
        "  - A sidebar listing available genres.\n"
        "  - A section displaying the most popular movies.\n"
        "  - Navigation links: Home, Search, Login/Register, My Rentals."
    )
    .add_section(Section("Search Bar", "Text input for movie keywords."))
    .add_section(Section("Genres", "List of genres (from the Category table) to filter movies."))
    .add_section(Section("Popular Movies", "Shows the top 5 popular movies based on recent rentals."))
    .add_flow(Flow("Click on a movie", "Movie Details"))
    .add_flow(Flow("Click on a genre", "Search"))
)

# Search Page: Allows searching movies by title, genre, or release year.
dvd_workflow.add_page(
    Page("Search", route="/search")
    .set_description(
        "Search page enabling users to:\n"
        "  - Enter keywords to search for movies.\n"
        "  - Filter results by genre using a provided list.\n"
        "  - View a list of matching movies, each clickable to see details."
    )
    .add_flow(Flow("Select movie from results", "Movie Details"))
)

# Movie Details Page: Displays movie information and related actors.
dvd_workflow.add_page(
    Page("Movie Details", route="/movie/<film_id>")
    .set_description(
        "Movie Details page that shows:\n"
        "  - Full movie information (title, description, release year, rental rate, etc.).\n"
        "  - A list of actors (obtained by joining Film_Actor with Actor).\n"
        "  - Options to rent the movie or navigate to actor details."
    )
    .add_flow(Flow("Click on actor", "Actor Details"))
    .add_flow(Flow("Click on Rent", "Rent Movie"))
)

# Actor Details Page: Displays actor information and filmography.
dvd_workflow.add_page(
    Page("Actor Details", route="/actor/<actor_id>")
    .set_description(
        "Actor Details page featuring:\n"
        "  - The actor's name and biography (if available).\n"
        "  - A filmography listing all movies the actor appears in.\n"
        "  - Navigation options to return to the movie details or search page."
    )
    .add_flow(Flow("Go back", "Movie Details"))
)

# Rent Movie Workflow: A two-step process for renting a movie.
dvd_workflow.add_page(
    Page("Rent Movie", route="/rent/<film_id>")
    .set_description(
        "Rent Movie workflow:\n"
        "  - Display a form for confirming rental details (rental date, return date, payment).\n"
        "  - Validate that the return date is later than the rental date.\n"
        "  - Validate that the payment amount matches the film's rental rate."
    )
    .add_validation(Validation("Return date must be after rental date."))
    .add_validation(Validation("Payment amount must equal the film's rental rate."))
    .add_flow(Flow("Submit form", "Confirmation"))
    .add_flow(Flow("Cancel", "Movie Details"))
)

# Confirmation Page: Shows confirmation of a successful rental.
dvd_workflow.add_page(
    Page("Confirmation", route="/confirmation")
    .set_description("Displays a confirmation message after a successful rental transaction.")
)

# Admin CRUD Page for Films: Allows managing films.
dvd_workflow.add_page(
    Page("Admin Films", route="/admin/films")
    .set_description(
        "Admin interface for managing films:\n"
        "  - View a list of films.\n"
        "  - Create, update, or delete film records.\n"
        "  - Validations ensure film data integrity (e.g., rental_rate < replacement_cost)."
    )
)

# Additional pages (e.g., customer management, rental history) could be added similarly.

# ---------------------------------------------------------------------------
# For debugging: Print the defined workflow if this module is run directly.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(dvd_workflow)