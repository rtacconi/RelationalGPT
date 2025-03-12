# relational_gpt/cli.py
"""
Command Line Interface for RelationalGPT

This module provides a CLI for the RelationalGPT framework, allowing users to:
1. Parse LLM-generated DSL
2. Validate constraints
3. Generate and run web applications
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from relational_gpt.framework import RelationalGPTFramework
from relational_gpt.parser import DSLParser


def create_argparser() -> argparse.ArgumentParser:
    """Create argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="RelationalGPT: A framework for LLM-generated relational-functional programming"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse LLM-generated DSL")
    parse_parser.add_argument(
        "input_file", type=str, help="Path to file containing LLM-generated DSL"
    )
    parse_parser.add_argument(
        "-o", "--output", type=str, help="Output Python file path", default="generated_dsl.py"
    )
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate DSL constraints")
    validate_parser.add_argument(
        "dsl_file", type=str, help="Path to parsed DSL Python file"
    )
    validate_parser.add_argument(
        "-d", "--db", type=str, help="Database path", default=":memory:"
    )
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate web application")
    generate_parser.add_argument(
        "dsl_file", type=str, help="Path to parsed DSL Python file"
    )
    generate_parser.add_argument(
        "-o", "--output-dir", type=str, help="Output directory", default="generated_app"
    )
    generate_parser.add_argument(
        "-d", "--db", type=str, help="Database path", default="app.db"
    )
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run generated web application")
    run_parser.add_argument(
        "app_dir", type=str, help="Directory containing generated web application"
    )
    
    return parser


def parse_dsl(input_file: str, output_file: str) -> None:
    """
    Parse LLM-generated DSL and write it to a Python file.
    
    Args:
        input_file: Path to file containing LLM-generated DSL.
        output_file: Output Python file path.
    """
    print(f"Parsing DSL from {input_file}...")
    
    # Read the input file
    with open(input_file, "r") as f:
        llm_output = f.read()
    
    # Parse the DSL
    parser = DSLParser()
    parsed_code = parser.parse_llm_output(llm_output)
    formatted_code = parser.format_as_python_file(parsed_code)
    
    # Write the output file
    with open(output_file, "w") as f:
        f.write(formatted_code)
    
    print(f"DSL successfully parsed and written to {output_file}")


def validate_constraints(dsl_file: str, db_path: str) -> None:
    """
    Validate constraints in a DSL file.
    
    Args:
        dsl_file: Path to parsed DSL Python file.
        db_path: Database path.
    """
    print(f"Validating constraints in {dsl_file}...")
    
    # Initialize the framework
    framework = RelationalGPTFramework(db_path)
    
    # Read the DSL file
    with open(dsl_file, "r") as f:
        dsl_code = f.read()
    
    # Load the DSL
    framework.load_dsl_from_string(dsl_code)
    
    # Create database schema
    framework.create_database_schema()
    
    # Validate constraints
    errors = framework.validate_constraints()
    
    if errors:
        print("Constraint validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("All constraints validated successfully!")
    
    # Close the framework
    framework.close()


def generate_web_app(dsl_file: str, output_dir: str, db_path: str) -> None:
    """
    Generate a web application from a DSL file.
    
    Args:
        dsl_file: Path to parsed DSL Python file.
        output_dir: Output directory for the generated application.
        db_path: Database path.
    """
    print(f"Generating web application from {dsl_file}...")
    
    # Initialize the framework
    framework = RelationalGPTFramework(db_path)
    
    # Read the DSL file
    with open(dsl_file, "r") as f:
        dsl_code = f.read()
    
    # Load the DSL
    framework.load_dsl_from_string(dsl_code)
    
    # Create database schema
    framework.create_database_schema()
    
    # Generate web application
    framework.generate_web_app(output_dir)
    
    print(f"Web application successfully generated in {output_dir}")
    print(f"To run the application, execute: python -m relational_gpt.cli run {output_dir}")
    
    # Close the framework
    framework.close()


def run_web_app(app_dir: str) -> None:
    """
    Run a generated web application.
    
    Args:
        app_dir: Directory containing the generated web application.
    """
    app_file = os.path.join(app_dir, "app.py")
    
    if not os.path.exists(app_file):
        print(f"Error: app.py not found in {app_dir}")
        sys.exit(1)
    
    print(f"Running web application from {app_dir}...")
    
    # Change to the app directory
    original_dir = os.getcwd()
    os.chdir(app_dir)
    
    try:
        # Import and run the app
        sys.path.insert(0, app_dir)
        from app import app
        app.run(debug=True)
    finally:
        # Restore original directory
        os.chdir(original_dir)


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_argparser()
    args = parser.parse_args()
    
    if args.command == "parse":
        parse_dsl(args.input_file, args.output)
    elif args.command == "validate":
        validate_constraints(args.dsl_file, args.db)
    elif args.command == "generate":
        generate_web_app(args.dsl_file, args.output_dir, args.db)
    elif args.command == "run":
        run_web_app(args.app_dir)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()