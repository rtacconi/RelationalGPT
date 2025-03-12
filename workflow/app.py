import os
import sqlite3
from flask import Flask, request, render_template_string, redirect, url_for, flash, g
from workflow.dsl import dvd_workflow  # Our workflow DSL definition

# =============================================================================
# Flask Application Setup
# =============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
DATABASE = os.path.join(os.path.dirname(__file__), 'app.db')

def get_db():
    """Return a SQLite database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """Helper function to query the database."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# =============================================================================
# Generic Workflow Page Rendering
# =============================================================================

def render_workflow_page(page):
    """
    Renders a page based on its workflow DSL definition.
    For simplicity we use an inline template.
    """
    html = f"<h1>{page.name}</h1>"
    if page.description:
        html += f"<p>{page.description.replace(chr(10), '<br>')}</p>"
    if page.sections:
        html += "<h3>Sections</h3><ul>"
        for sec in page.sections:
            html += f"<li><strong>{sec.title}:</strong> {sec.description}</li>"
        html += "</ul>"
    if page.flows:
        html += "<h3>Flows</h3><ul>"
        for flow in page.flows:
            html += f"<li>On <em>{flow.trigger}</em> go to <strong>{flow.target}</strong></li>"
        html += "</ul>"
    if page.validations:
        html += "<h3>Validations</h3><ul>"
        for val in page.validations:
            html += f"<li>{val.message}</li>"
        html += "</ul>"
    return html

# =============================================================================
# Generic CRUD Endpoints for Admin Pages
# =============================================================================

def register_crud_routes(model_name):
    """
    For a given model name (e.g., 'films'), registers generic CRUD routes.
    We assume a table exists in SQLite with name model_name and columns (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT).
    """
    list_endpoint = f"list_{model_name}"
    create_endpoint = f"create_{model_name}"
    edit_endpoint = f"edit_{model_name}"
    delete_endpoint = f"delete_{model_name}"

    @app.route(f"/admin/{model_name}", endpoint=list_endpoint)
    def list_records(model=model_name):
        records = query_db(f"SELECT * FROM {model}")
        # Render a simple HTML list view
        html = f"<h1>List of {model.capitalize()}</h1>"
        html += f"<a href='{url_for(create_endpoint)}'>Create New</a><ul>"
        for r in records:
            html += (
                f"<li>{dict(r)} - "
                f"<a href='{url_for(edit_endpoint, id=r['id'])}'>Edit</a> | "
                f"<a href='{url_for(delete_endpoint, id=r['id'])}'>Delete</a></li>"
            )
        html += "</ul>"
        return html

    @app.route(f"/admin/{model_name}/create", endpoint=create_endpoint, methods=["GET", "POST"])
    def create_record(model=model_name):
        if request.method == "POST":
            # For demonstration, we assume a single field: 'name'
            name = request.form.get("name")
            db = get_db()
            db.execute(f"INSERT INTO {model} (name) VALUES (?)", (name,))
            db.commit()
            flash(f"Created new {model[:-1]}: {name}")
            return redirect(url_for(list_endpoint))
        return render_template_string(f"""
            <h1>Create New {model.capitalize()[:-1]}</h1>
            <form method="post">
              Name: <input type="text" name="name"><br>
              <input type="submit" value="Create">
            </form>
        """)

    @app.route(f"/admin/{model_name}/edit/<int:id>", endpoint=edit_endpoint, methods=["GET", "POST"])
    def edit_record(id, model=model_name):
        db = get_db()
        if request.method == "POST":
            name = request.form.get("name")
            db.execute(f"UPDATE {model} SET name = ? WHERE id = ?", (name, id))
            db.commit()
            flash(f"Updated {model[:-1]} {id}")
            return redirect(url_for(list_endpoint))
        record = query_db(f"SELECT * FROM {model} WHERE id = ?", (id,), one=True)
        if record is None:
            flash(f"{model[:-1].capitalize()} not found.")
            return redirect(url_for(list_endpoint))
        return render_template_string(f"""
            <h1>Edit {model.capitalize()[:-1]} {id}</h1>
            <form method="post">
              Name: <input type="text" name="name" value="{{{{ record['name'] }}}}"><br>
              <input type="submit" value="Update">
            </form>
        """, record=record)

    @app.route(f"/admin/{model_name}/delete/<int:id>", endpoint=delete_endpoint)
    def delete_record(id, model=model_name):
        db = get_db()
        db.execute(f"DELETE FROM {model} WHERE id = ?", (id,))
        db.commit()
        flash(f"Deleted {model[:-1]} {id}")
        return redirect(url_for(list_endpoint))

# =============================================================================
# Registering Routes Based on the Workflow DSL
# =============================================================================

workflow = dvd_workflow  # This is our workflow definition imported from workflow/dsl.py

# Iterate over all pages defined in the workflow.
for page in workflow.pages:
    # If the page is a CRUD (admin) page, assume its name starts with "Admin".
    if page.name.lower().startswith("admin"):
        # Extract the model name (e.g., "Admin Films" → "films")
        model = page.name[len("Admin "):].strip().lower()
        # Register CRUD routes for this model.
        register_crud_routes(model)
    else:
        # For other pages, register a generic route that renders the workflow page.
        def generic_page(page=page):
            return render_workflow_page(page)
        # Create a unique endpoint name from the page name.
        endpoint_name = page.name.lower().replace(" ", "_")
        app.add_url_rule(page.route, endpoint_name, generic_page)

# Also register a default index route.
@app.route("/")
def index():
    # If the workflow defines a page with route "/" use it; otherwise, show the first page.
    for page in workflow.pages:
        if page.route == "/":
            return render_workflow_page(page)
    return render_workflow_page(workflow.pages[0])

# =============================================================================
# Database Initialization (for CRUD pages)
# =============================================================================

def init_db():
    """
    Initialize the database. For every admin page in the workflow, create a table
    with a generic schema: id and name.
    """
    db = get_db()
    for page in workflow.pages:
        if page.name.lower().startswith("admin"):
            model = page.name[len("Admin "):].strip().lower()
            db.execute(f"CREATE TABLE IF NOT EXISTS {model} (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
    db.commit()

@app.before_first_request
def initialize():
    init_db()

# =============================================================================
# Run the Application
# =============================================================================

if __name__ == "__main__":
    app.run(debug=True)
