#! /usr/bin/env python3

# -*- coding: utf-8 -*-

# generate_toc.py

import argparse
import nbformat as nbf


def generate_toc(notebook):
    """Generates a Table of Contents (ToC) from the notebook's headings."""
    toc = []
    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            # Extract heading level and text
            lines = cell.source.splitlines()
            for line in lines:
                if line.startswith("#"):
                    level = line.count("#")
                    heading_text = line.lstrip("#").strip()
                    toc.append((level, heading_text))
    return toc


def format_toc(toc):
    """Formats the ToC into a numbered markdown string."""
    toc_markdown = [
        'Table of Contents <a class="jp-toc-ignore"></a>\n================='
    ]
    numbering = {}

    for level, heading in toc:
        # Create a number for the current heading
        if level not in numbering:
            numbering[level] = 1
        else:
            numbering[level] += 1

        # Reset numbering for sublevels
        for l in range(level + 1, max(numbering.keys()) + 1):
            if l in numbering:
                numbering[l] = 1

        # Create a number string for the heading
        number_string = ".".join(str(numbering[l]) for l in range(1, level + 1))
        toc_markdown.append(
            "  " * (level - 1)
            + f'* [{number_string} {heading}](#{heading.lower().replace(" ", "-")})'
        )

    return "\n".join(toc_markdown)


def add_toc_to_notebook(notebook, toc_markdown):
    """Adds the Table of Contents to the notebook one cell above the first section header."""
    toc_cell = nbf.v4.new_markdown_cell(toc_markdown)

    # Find the first section header to insert the ToC above
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type == "markdown" and any(
            line.startswith("#") for line in cell.source.splitlines()
        ):
            # Insert ToC one cell above the first section header
            notebook.cells.insert(i, toc_cell)
            break


def main(notebook_file, output_file):
    """Main method to read a notebook, generate a ToC, and save the updated notebook."""
    # Load the notebook
    with open(notebook_file, "r") as f:
        notebook = nbf.read(f, as_version=4)

    # Generate the ToC
    toc = generate_toc(notebook)
    toc_markdown = format_toc(toc)

    # Add ToC to the notebook
    add_toc_to_notebook(notebook, toc_markdown)

    # Save the updated notebook
    with open(output_file, "w") as f:
        nbf.write(notebook, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a Table of Contents for a Jupyter notebook."
    )
    parser.add_argument("input_notebook", help="The input Jupyter notebook file.")
    parser.add_argument(
        "output_notebook", help="The output Jupyter notebook file with the ToC."
    )

    args = parser.parse_args()

    main(args.input_notebook, args.output_notebook)
