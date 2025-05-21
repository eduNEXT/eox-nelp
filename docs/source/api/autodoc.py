#!/usr/bin/env python
"""
Script to automatically generate API documentation for eox-nelp.
"""
import os
import sys
from pathlib import Path

from sphinx.ext.apidoc import main as sphinx_apidoc

# Get the project root directory
project_root = Path(__file__).resolve().parent.parent.parent.parent
module_path = project_root / 'eox_nelp'
output_path = project_root / 'docs' / 'source' / 'api'

def generate_api_docs():
    """Generate API documentation using sphinx-apidoc."""
    # Remove existing API docs
    for file in output_path.glob('*.rst'):
        if file.name != 'index.rst':
            file.unlink()

    # Generate new API docs
    args = [
        '--force',  # Overwrite existing files
        '--separate',  # Put documentation for each module in its own page
        '--module-first',  # Put module documentation before submodule documentation
        '--doc-project=API Reference',  # Project name in documentation
        '-o', str(output_path),  # Output directory
        str(module_path),  # Path to Python package
        str(module_path / '*/migrations'),  # Exclude migrations
        str(module_path / '*/tests'),  # Exclude tests
    ]

    sphinx_apidoc(args)

if __name__ == '__main__':
    generate_api_docs()
