import nbformat as nbf
import json
import argparse


def extract_sections_to_json(notebook_path):
    """
    Extract sections and subsections from the notebook and save them to a JSON file.

    Args:
        notebook_path (str): Path to the input notebook.
        output_json (str): Path to save the output JSON file.
    """
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = nbf.read(f, as_version=4)

    sections = []
    stack = []  # Stack to maintain nested sections

    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            # Look for headers to identify sections and subsections
            lines = cell.source.splitlines()
            if lines and lines[0].startswith("#"):
                header = lines[0]
                level = header.count("#")  # Number of '#' defines the level
                title = header.strip("# ").strip()

                # Create a new section/subsection
                new_section = {
                    "name": title,
                    "cells": [],
                    "children": [],
                }

                # If the stack is empty or this is a top-level section
                while stack and stack[-1][0] >= level:
                    stack.pop()  # Pop sections of higher or equal level

                if stack:
                    # Add as a child to the last section in the stack
                    stack[-1][1]["children"].append(new_section)
                else:
                    # Add as a root section
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


# Write sections to JSON
def save_json(sections, output_json):
    """Save the extracted sections to a JSON file."""
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({"sections": sections}, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract sections from a notebook.")
    parser.add_argument("notebook_path", help="Path to the input notebook.")
    parser.add_argument(
        "-o",
        "--output",
        default="template.json",
        required=False,
        help="Path to save the output JSON file.",
    )

    args = parser.parse_args()

    sections = extract_sections_to_json(args.notebook_path)
    save_json(sections, args.output)
