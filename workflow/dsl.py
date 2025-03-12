# workflow/dsl.py
"""
workflow/dsl.py

This module defines a Python DSL for describing a web application's workflow.
The DSL is intended to be used by the framework's workflow layer.
It allows one to specify pages, sections, flows, and validations in a
declarative style.

Example usage (a DVD Rental Web App workflow):

    dvd_workflow = Workflow("DVD Rental Web App")
    dvd_workflow.add_page(
        Page("Home", route="/")
            .set_description("Landing page with a search bar, a genre list, popular movies, and navigation links.")
            .add_section(Section("Search Bar", "A text field to search for movies."))
            .add_section(Section("Genres", "A list of genres from the Category table."))
            .add_section(Section("Popular Movies", "Display the top 5 popular movies."))
            .add_flow(Flow("Click on a movie", "Movie Details"))
            .add_flow(Flow("Click on a genre", "Search"))
    )
    # ... add more pages as needed ...
"""

# ---------------------------------------------------------------------------
# DSL Core Classes
# ---------------------------------------------------------------------------

class Workflow:
    def __init__(self, name):
        self.name = name
        self.pages = []

    def add_page(self, page):
        self.pages.append(page)
        return self

    def __str__(self):
        lines = [f"Workflow: {self.name}"]
        for page in self.pages:
            lines.append(str(page))
        return "\n".join(lines)


class Page:
    def __init__(self, name, route=None):
        self.name = name
        self.route = route if route is not None else self._generate_route(name)
        self.description = ""
        self.sections = []
        self.flows = []
        self.validations = []

    def _generate_route(self, name):
        # A simple route generator: lowercase and replace spaces with hyphens.
        # Special pages with parameters (like movie details) should be explicitly set.
        return "/" + name.lower().replace(" ", "-")

    def set_description(self, desc):
        self.description = desc
        return self

    def add_section(self, section):
        self.sections.append(section)
        return self

    def add_flow(self, flow):
        self.flows.append(flow)
        return self

    def add_validation(self, validation):
        self.validations.append(validation)
        return self

    def __str__(self):
        lines = [f"Page: {self.name} (route: {self.route})"]
        if self.description:
            lines.append(f"  Description: {self.description}")
        if self.sections:
            lines.append("  Sections:")
            for sec in self.sections:
                lines.append(f"    - {sec.title}: {sec.description}")
        if self.flows:
            lines.append("  Flows:")
            for flow in self.flows:
                lines.append(f"    - On '{flow.trigger}' go to '{flow.target}'")
        if self.validations:
            lines.append("  Validations:")
            for val in self.validations:
                lines.append(f"    - {val.message}")
        return "\n".join(lines)


class Section:
    def __init__(self, title, description=""):
        self.title = title
        self.description = description

    def __str__(self):
        return f"Section: {self.title} - {self.description}"


class Flow:
    def __init__(self, trigger, target):
        self.trigger = trigger
        self.target = target

    def __str__(self):
        return f"Flow: on '{self.trigger}' -> '{self.target}'"


class Validation:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"Validation: {self.message}"