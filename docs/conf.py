# pylint: disable=invalid-name
"""
This file contains configuration needed to customize Sphinx input and output behavior.
"""
from datetime import date, datetime
from typing import Any

import afsm

author = "Daniele Masato"
name = "afsm"
version = ".".join(afsm.__version__.split(".")[:2])
release = afsm.__version__
project_copyright = f"2022-{date.today().year}, {author}"

github_username = "doloopuntil"
github_repository = "https://github.com/doloopuntil/dlu-afsm"

root_doc = "index"
source_suffix = {".rst": "restructuredtext"}

html_theme = "furo"
html_title = "afsm"
html_last_updated_fmt = datetime.now().isoformat()

extensions = [
    # Use autodoc to generate documentation from docstrings in a semi-automatic way.
    # See http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html.
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "attrs": ("https://www.attrs.org/en/stable/", None),
}

# Autodoc extension settings (sphinx.ext.autodoc)
# Disable type hints as ``sphinx_autodoc_typehints`` handles them instead
autodoc_typehints = "none"
autodoc_default_options = {"class-doc-from": "class", "members": False, "member-order": "bysource"}
# autodoc_type_aliases = {"afsm._fsm.Transition": "afsm.transition"}

# Typehints extension settings (sphinx_autodoc_typehints)
typehints_defaults = "comma"

# Napoleon extension settings (sphinx.ext.napoleon)
napoleon_numpy_docstring = False


def setup(*_: Any) -> None:
    """
    Setup Sphinx for thr
    """

    # The private class ``Transition`` is exposed as ``transition`` in the public API. Alias the private class name, so
    # Autodoc will generate the expected documentation, instead of a line stating ``alias of ...``
    # pylint: disable=protected-access
    afsm._fsm.Transition.__name__ = "transition"
