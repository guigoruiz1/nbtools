import re
import argparse
import nbformat as nbf
from toc import remove_existing_toc, generate_toc, format_toc, add_toc_to_notebook


def number_headings_in_notebook(notebook):
    """Add numbers to markdown headings in notebook cells."""
    counters = {}

    def replace_heading(match):
        level = len(match.group(1))

        # Initialize counter for this level if not exists
        if level not in counters:
            counters[level] = 0

        counters[level] += 1

        # Reset deeper level counters
        levels_to_reset = [l for l in counters.keys() if l > level]
        for l in levels_to_reset:
            counters[l] = 0

        heading_text = match.group(2)

        # Check if heading already has a number prefix
        existing_match = re.match(r"^(\d+(?:\.\d+)*)\s+(.*)$", heading_text)
        if existing_match:
            # Already numbered, skip
            return match.group(0)

        number = ".".join(str(counters[i]) for i in range(1, level + 1))

        return f"{match.group(1)} {number} {heading_text}"

    # Process each cell in the notebook
    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            # Match markdown headings: # Heading
            pattern = r"^(#{1,})\s+(.*)$"
            cell.source = re.sub(
                pattern, replace_heading, cell.source, flags=re.MULTILINE
            )

    return notebook


def remove_numbering_from_notebook(notebook):
    """Remove numbers from markdown headings in notebook cells."""

    def replace_heading(match):
        heading_text = match.group(2)

        # Check if heading has a number prefix and remove it
        number_match = re.match(r"^(\d+(?:\.\d+)*)\s+(.*)$", heading_text)
        if number_match:
            clean_text = number_match.group(2)
            return f"{match.group(1)} {clean_text}"

        # No numbering found, return as is
        return match.group(0)

    # Process each cell in the notebook
    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            # Match markdown headings: # Heading
            pattern = r"^(#{1,})\s+(.*)$"
            cell.source = re.sub(
                pattern, replace_heading, cell.source, flags=re.MULTILINE
            )

    return notebook


def main(notebook_file, output_file=None, remove=False, update_toc=True):
    """Main method to read a notebook, number/remove headings, and save the updated notebook."""
    # Load the notebook
    with open(notebook_file, "r") as f:
        notebook = nbf.read(f, as_version=4)

    # Check if TOC exists before making changes
    toc_exists = any(
        'class="jp-toc-ignore"' in cell.get("source", "") for cell in notebook.cells
    )

    if remove:
        # Remove numbering from headings
        notebook = remove_numbering_from_notebook(notebook)
        action = "Removed numbering from"
    else:
        # Add numbers to the headings
        notebook = number_headings_in_notebook(notebook)
        action = "Numbered headings saved to"

    # Update TOC if it exists and update_toc is True
    if toc_exists and update_toc:
        remove_existing_toc(notebook)
        toc = generate_toc(notebook)
        toc_markdown = format_toc(toc)
        add_toc_to_notebook(notebook, toc_markdown)

    # Save the updated notebook
    output = output_file or notebook_file
    with open(output, "w") as f:
        nbf.write(notebook, f)

    print(f"{action} {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add or remove numbers from markdown headings in a Jupyter notebook."
    )
    parser.add_argument("input_notebook", help="The input Jupyter notebook file.")
    parser.add_argument(
        "output_notebook",
        nargs="?",
        help="The output Jupyter notebook file (defaults to input file).",
    )
    parser.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="Remove numbering from headings instead of adding it.",
    )
    parser.add_argument(
        "--no-toc",
        action="store_true",
        help="Don't update the table of contents (if one exists).",
    )

    args = parser.parse_args()

    main(
        args.input_notebook,
        args.output_notebook,
        remove=args.remove,
        update_toc=not args.no_toc,
    )
