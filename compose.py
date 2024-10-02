import nbformat as nbf
import json
import re
import argparse


def add_cells_to_notebook(notebook, cells, replace_pairs=None):
    """Adds cells to the notebook in the correct format with optional replacements."""
    replace_pairs = replace_pairs or {}

    for cell in cells:
        source = cell["source"]
        # Apply replacements to the source code
        for old, new in replace_pairs.items():
            # Ensure only exact matches are replaced (e.g., words or variables)
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
            for child in section_data.get("children", []):
                add_sections_to_notebook(
                    notebook,
                    {child["name"]: {"all": True}},
                    template_sections,
                    level + 1,
                )

        # Recursively add specific children if provided
        if children:
            add_sections_to_notebook(
                notebook, children, section_data.get("children", []), level + 1
            )


def compose_notebook_from_template(template_data, input_sections):
    """Composes a notebook based on the structure in a template JSON file."""
    # Create a new notebook
    new_nb = nbf.v4.new_notebook()

    # Add sections and subsections using the provided input dictionary
    add_sections_to_notebook(new_nb, input_sections, template_data["sections"])

    return new_nb


def save_notebook(notebook, filename):
    """Saves the composed notebook to a file."""
    with open(filename, "w") as f:
        nbf.write(notebook, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compose a notebook from a JSON template"
    )
    parser.add_argument(
        "-t",
        "--template",
        help="Path to JSON template file",
        default="template.json",
        required=False,
    )
    parser.add_argument(
        "-s",
        "--selection",
        help="Path to user dictionary with selected sections' structure",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to save notebook",
        required=False,
        default="composed.ipynb",
    )

    args = parser.parse_args()

    with open(args.template, "r") as f:
        template_data = json.load(f)

    with open(args.selection, "r") as f:
        input_data = json.load(f)

    # Load template JSON and compose the notebook
    composed_nb = compose_notebook_from_template(template_data, input_data)

    # Save the composed notebook to an output file
    save_notebook(composed_nb, args.output)
