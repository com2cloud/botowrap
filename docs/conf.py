"""Configuration file for the Sphinx documentation builder."""

import os
import sys
from datetime import datetime

# Add the project root directory to the path
sys.path.insert(0, os.path.abspath(".."))

# Import project metadata
import botowrap

# Project information
project = "botowrap"
copyright = f"{datetime.now().year}, Denys Melnyk"
author = "Denys Melnyk"
version = botowrap.__version__
release = botowrap.__version__

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML output options
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "boto3": ("https://boto3.amazonaws.com/v1/documentation/api/latest/", None),
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False

# Auto-generate API documentation
autoclass_content = "both"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "undoc-members": True,
}

# Todo settings
todo_include_todos = True
