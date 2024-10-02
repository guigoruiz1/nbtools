#! /usr/bin/env python3

# -*- coding: utf-8 -*-


import nbformat as nbf
import json
import re
import argparse
import os


def add_cells_to_notebook(notebook, cells, replace_pairs=None):
    """Adds cells to the notebook with optional replacements."""
    replace_pairs = replace_pairs or {}

    for cell in cells:
        source = cell["source"]
        for old, new in replace_pairs.items():
            source = re.sub(
                rf"(?<![a-zA-Z0-9]){re.escape(old)}(?![a-zA-Z0-9])", new, source
            )

        if cell["cell_type"] == "code":
            notebook["cells"].append(nbf.v4.new_code_cell(source))
        elif cell["cell_type"] == "markdown":
            notebook["cells"].append(nbf.v4.new_markdown_cell(source))


def find_section(template_sections, section_path):
    """Find a section by its path (e.g., 'Preamble / Imports') in the template JSON."""
    path_parts = section_path.split(" / ")
    current_section = template_sections

    for part in path_parts:
        found = next((sec for sec in current_section if sec["name"] == part), None)
        if not found:
            return None  # Section not found
        current_section = found.get("children", [])

    return found


def add_sections_to_notebook(notebook, sections, template_sections, level=1):
    """Recursively adds sections and subsections to the notebook based on their depth in the structure."""
    for section_name, section_options in sections.items():
        title = section_options.get("title", section_name.split("/")[-1])
        replace_pairs = section_options.get("replace", {})
        all_option = section_options.get("all", False)
        children = {
            k: v
            for k, v in section_options.items()
            if k not in ["title", "replace", "all"]
        }

        # Find the section in the template JSON using the path-like section name
        section_data = find_section(template_sections, section_name)
        if section_data is None:
            raise ValueError(f"Section '{section_name}' not found in template.")

        # Add the section header as a markdown cell with the appropriate level
        header_cell = f"{'#' * level} {title}"
        notebook["cells"].append(nbf.v4.new_markdown_cell(header_cell))

        # Add the section's cells with the replacements applied
        add_cells_to_notebook(notebook, section_data["cells"], replace_pairs)

        # Add all children if "all" is set to True
        if all_option:
            # First add explicitly defined children
            for child_name, child_options in children.items():
                child_data = find_section(section_data.get("children", []), child_name)
                if child_data:
                    add_sections_to_notebook(
                        notebook,
                        {child_name: child_options},
                        section_data.get("children", []),
                        level + 1,
                    )

            # Then add remaining children from the template that were not explicitly defined
            for child in section_data.get("children", []):
                if child["name"] not in children:
                    add_sections_to_notebook(
                        notebook,
                        {child["name"]: {"all": True}},
                        section_data.get("children", []),
                        level + 1,
                    )

        # Recursively add specific children if provided and 'all' is not set
        if children and not all_option:
            add_sections_to_notebook(
                notebook, children, section_data.get("children", []), level + 1
            )


def extract_sections_from_notebook(notebook):
    """Extracts sections from an existing notebook into a JSON structure."""
    sections = []
    stack = []  # Track the current section hierarchy
    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            # Detect headers based on the number of "#" symbols
            header_match = re.match(r"^(#+)\s+(.*)", cell.source)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2)

                # Create a new section
                new_section = {"name": title, "cells": []}

                # Adjust the section hierarchy based on header level
                while stack and stack[-1][0] >= level:
                    stack.pop()

                if stack:
                    # Add as a child of the current section
                    parent = stack[-1][1]
                    if "children" not in parent:
                        parent["children"] = []
                    parent["children"].append(new_section)
                else:
                    sections.append(new_section)

                # Push the new section onto the stack
                stack.append((level, new_section))
            else:
                # Add markdown cells that aren't headers to the current section
                if stack:
                    stack[-1][1]["cells"].append(
                        {"cell_type": "markdown", "source": cell.source}
                    )

        elif cell.cell_type == "code":
            # Add code cells to the current section
            if stack:
                stack[-1][1]["cells"].append(
                    {"cell_type": "code", "source": cell.source}
                )

    return sections


def create_selection_from_input(input_path, include_all=False):
    """Generates a selection.json from either a notebook or template input."""
    if input_path.endswith(".json"):
        input_type = "template"
    elif input_path.endswith(".ipynb"):
        input_type = "notebook"

    def recurse_sections(sections):
        selection = {}
        for section in sections:
            children = section.get("children", [])
            # Populate the section structure with optional fields for user modification
            selection[section["name"]] = {
                "title": section["name"],  # Default title as section name
                "replace": {},  # Empty replace field
                "all": include_all,  # Option to include all subsections
            }
            if children:
                # Recurse into subsections if they exist
                selection[section["name"]].update(recurse_sections(children))
        return selection

    if input_type == "template":
        with open(input_path, "r") as f:
            template_data = json.load(f)
        return recurse_sections(template_data)

    elif input_type == "notebook":
        with open(input_path, "r") as f:
            notebook_data = nbf.read(f, as_version=4)
        sections = extract_sections_from_notebook(notebook_data)
        return recurse_sections(sections)


def save_selection_file(selection_data, output_path="selection.json"):
    """Saves the generated selection.json to a file."""
    with open(output_path, "w") as f:
        json.dump(selection_data, f, indent=4)
    print(f"Selection file saved to {output_path}")


def save_notebook(notebook, filename):
    """Saves the composed notebook to a file."""
    with open(filename, "w") as f:
        nbf.write(notebook, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compose or extract notebook sections")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-nb",
        "--notebook",
        help="Path to input notebook (.ipynb). Used to either extract sections or compose a notebook.",
    )
    group.add_argument(
        "-t",
        "--template",
        help="Path to JSON template file (sections.json)",
    )

    parser.add_argument(
        "-s",
        "--selection",
        help="Path to user dictionary with selected sections' structure (required for composition)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to save notebook or sections JSON",
        required=False,
        default="output.ipynb",
    )

    parser.add_argument(
        "--create-selection",
        action="store_true",
        help="Create a selection.json from the template or notebook",
    )

    args = parser.parse_args()

    if args.create_selection:
        # Generate selection.json from notebook or template
        if args.template:
            selection_data = create_selection_from_input(args.template)
            output_path = (
                f"{os.path.basename(args.template).replace('.json','_selection.json')}"
            )
        elif args.notebook:
            selection_data = create_selection_from_input(args.notebook)
            output_path = (
                f"{os.path.basename(args.notebook).replace('.ipynb','_selection.json')}"
            )

        save_selection_file(selection_data, output_path=output_path)

    if args.notebook and not args.selection:
        # Extract sections from notebook and save to sections.json
        with open(args.notebook, "r") as f:
            notebook_data = nbf.read(f, as_version=4)

        output_path = os.path.basename(args.notebook).replace(".ipynb", ".json")
        sections = extract_sections_from_notebook(notebook_data)
        with open(output_path, "w") as f:
            json.dump(sections, f, indent=4)
        print(f"Sections extracted and saved to {output_path}")

    elif args.notebook and args.selection:
        # Compose notebook using input notebook as template
        with open(args.notebook, "r") as f:
            template_data = extract_sections_from_notebook(nbf.read(f, as_version=4))

        with open(args.selection, "r") as f:
            input_data = json.load(f)

        composed_nb = nbf.v4.new_notebook()
        add_sections_to_notebook(composed_nb, input_data, template_data)
        save_notebook(composed_nb, args.output)
        print(f"Notebook composed and saved to {args.output}")

    elif args.template and args.selection:
        # Compose notebook using sections.json as template
        with open(args.template, "r") as f:
            template_data = json.load(f)

        with open(args.selection, "r") as f:
            input_data = json.load(f)

        composed_nb = nbf.v4.new_notebook()
        add_sections_to_notebook(composed_nb, input_data, template_data)
        save_notebook(composed_nb, args.output)
        print(f"Notebook composed and saved to {args.output}")
