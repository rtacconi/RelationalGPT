# relational_gpt/framework.py
"""
RelationalGPT: A framework for LLM-generated relational-functional programming

This module provides the core framework functionality, integrating the relational
operations, integrity constraints, and workflow DSL.
"""

import importlib
import inspect
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Import the relational DSL components
from relational.dsl import restrict, join, project, extend, summarize, ensure

# Import the workflow DSL components
from workflow.dsl import Workflow, Page, Section, Flow, Validation


class RelationalGPTFramework:
    """
    Main framework class that integrates all components and handles DSL parsing,
    database connections, and web application generation.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the RelationalGPT framework.
        
        Args:
            db_path: Path to the SQLite database file. If None, an in-memory database is used.
        """
        self.db_path = db_path or ":memory:"
        self.conn = self._create_db_connection()
        self.relations: Dict[str, List[Dict[str, Any]]] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.constraints: List[Tuple[str, Callable]] = []
    
    def _create_db_connection(self) -> sqlite3.Connection:
        """Create a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def load_dsl_from_string(self, dsl_code: str) -> None:
        """
        Parse and load a DSL definition from a string.
        
        Args:
            dsl_code: A string containing DSL code generated by LLM.
        """
        # Create a temporary Python module
        temp_dir = Path("./temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Write the DSL code to a temporary file
        module_path = temp_dir / "llm_generated_dsl.py"
        with open(module_path, "w") as f:
            f.write(dsl_code)
        
        # Import the temporary module
        spec = importlib.util.spec_from_file_location("llm_generated_dsl", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Extract relations, workflows, and constraints from the module
        self._extract_module_components(module)
    
    def _extract_module_components(self, module) -> None:
        """
        Extract relations, workflows, and constraints from a loaded module.
        
        Args:
            module: A Python module object containing DSL definitions.
        """
        # Extract relations (lists of dictionaries)
        for name, obj in inspect.getmembers(module):
            if isinstance(obj, list) and all(isinstance(item, dict) for item in obj):
                self.relations[name] = obj
        
        # Extract workflows
        for name, obj in inspect.getmembers(module):
            if isinstance(obj, Workflow):
                self.workflows[name] = obj
        
        # Extract constraint functions
        if hasattr(module, "run_constraints"):
            # Extract ensure calls from the run_constraints function
            source = inspect.getsource(module.run_constraints)
            ensure_pattern = r'ensure\s*\(\s*["\']([^"\']+)["\'],\s*(.+)\s*\)'
            matches = re.findall(ensure_pattern, source)
            
            for description, condition_code in matches:
                # Create a lambda function from the condition code
                # This is a simplified approach; real parsing would be more complex
                # and would need to handle the full Python syntax
                condition_lambda = eval(f"lambda: {condition_code}", 
                                        {**globals(), **self.relations})
                self.constraints.append((description, condition_lambda))
    
    def create_database_schema(self) -> None:
        """
        Create database tables based on the relations defined in the DSL.
        """
        cursor = self.conn.cursor()
        
        for relation_name, rows in self.relations.items():
            if not rows:
                continue
                
            # Extract column names and types from the first row
            first_row = rows[0]
            columns = []
            
            for col_name, value in first_row.items():
                col_type = self._infer_sql_type(value)
                columns.append(f"{col_name} {col_type}")
            
            # Create the table
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {relation_name} (
                {', '.join(columns)}
            )
            """
            cursor.execute(create_table_sql)
            
            # Insert data
            for row in rows:
                placeholders = ', '.join(['?'] * len(row))
                columns = ', '.join(row.keys())
                values = list(row.values())
                
                insert_sql = f"""
                INSERT INTO {relation_name} ({columns})
                VALUES ({placeholders})
                """
                cursor.execute(insert_sql, values)
        
        self.conn.commit()
    
    def _infer_sql_type(self, value: Any) -> str:
        """
        Infer the SQL type for a Python value.
        
        Args:
            value: A Python value to infer the SQL type for.
            
        Returns:
            A string representing the SQL type.
        """
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, str):
            return "TEXT"
        elif value is None:
            return "NULL"
        else:
            return "TEXT"  # Default to TEXT for complex types
    
    def validate_constraints(self) -> List[str]:
        """
        Validate all constraints defined in the DSL.
        
        Returns:
            A list of error messages for failed constraints.
        """
        errors = []
        
        for description, condition in self.constraints:
            try:
                if not condition():
                    errors.append(f"Constraint failed: {description}")
            except Exception as e:
                errors.append(f"Error validating constraint '{description}': {str(e)}")
        
        return errors
    
    def generate_web_app(self, output_dir: str) -> None:
        """
        Generate a Flask web application based on the workflow definitions.
        
        Args:
            output_dir: Directory to write the generated web application.
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate app.py
        app_py_path = os.path.join(output_dir, "app.py")
        with open(app_py_path, "w") as f:
            f.write(self._generate_app_py())
        
        # Generate templates
        templates_dir = os.path.join(output_dir, "templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        for workflow_name, workflow in self.workflows.items():
            self._generate_templates(workflow, templates_dir)
    
    def _generate_app_py(self) -> str:
        """
        Generate the Flask application code.
        
        Returns:
            A string containing the generated app.py code.
        """
        # This is a simplified version; a real implementation would be more sophisticated
        app_py_template = """
import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, flash, g

app = Flask(__name__)
app.config['SECRET_KEY'] = 'generated_secret_key'
DATABASE = '{db_path}'

def get_db():
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
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

{routes}

if __name__ == '__main__':
    app.run(debug=True)
"""
        
        # Generate routes for all pages in all workflows
        routes = []
        for workflow_name, workflow in self.workflows.items():
            for page in workflow.pages:
                route_code = self._generate_route_for_page(page)
                routes.append(route_code)
        
        return app_py_template.format(
            db_path=self.db_path,
            routes="\n\n".join(routes)
        )
    
    # The rest of the implementation continues...
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query on the database.
        
        Args:
            query: SQL query string.
            
        Returns:
            A list of dictionary rows.
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()