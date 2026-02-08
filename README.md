# nbtools

This repository contains scripts to manage Jupyter notebooks and NBConvert templates. The main scripts are `toc.py`, `headingnum.py`, `compose.py`, and `generate_auto_theme.py`.

## toc.py

The `toc.py` script generates a Table of Contents (ToC) for a Jupyter notebook. It intelligently handles both numbered and unnumbered headings, preserving existing numbering while generating sequential numbers for headings without them.

### Features

- Generates a hierarchical table of contents from markdown headings
- Preserves existing heading numbers (e.g., "1.2 Section Title")
- Auto-generates numbers for unnumbered headings
- Creates proper anchor links (with numbers for pre-numbered headings, without for auto-numbered ones)
- Inserts ToC above the first heading in the notebook

### Usage

```sh
python toc.py <input_notebook> [output_notebook]
```

- `input_notebook`: The path to the input Jupyter notebook file.
- `output_notebook` (optional): The path to save the output Jupyter notebook file with the ToC. If not provided, the ToC will be printed to the console.

### Examples

**Generate and preview ToC:**
```sh
python toc.py notebook.ipynb
```

**Add ToC to notebook:**
```sh
python toc.py notebook.ipynb notebook_with_toc.ipynb
```

## headingnum.py

The `headingnum.py` script adds or removes hierarchical numbering to/from markdown headings in Jupyter notebooks. It automatically updates the table of contents if one exists.

### Features

- Add sequential numbering to all headings (1, 1.1, 1.2, 2, 2.1, etc.)
- Remove numbering from headings
- Supports unlimited heading levels
- Skips already-numbered headings when adding numbers
- Automatically updates existing table of contents
- Option to skip TOC updates with `--no-toc` flag

### Usage

```sh
python headingnum.py <input_notebook> [output_notebook] [-r] [--no-toc]
```

- `input_notebook`: The path to the input Jupyter notebook file.
- `output_notebook` (optional): The path to save the output notebook. If not provided, modifies the input file in place.
- `-r, --remove`: Remove numbering from headings instead of adding it.
- `--no-toc`: Don't update the table of contents (if one exists).

### Examples

**Add numbering to headings (and update TOC if exists):**
```sh
python headingnum.py notebook.ipynb
```

**Add numbering and save to new file:**
```sh
python headingnum.py notebook.ipynb numbered_notebook.ipynb
```

**Remove numbering from headings:**
```sh
python headingnum.py notebook.ipynb -r
```

**Add numbering but don't update TOC:**
```sh
python headingnum.py notebook.ipynb --no-toc
```

## compose.py

The `compose.py` script extracts, composes, and manages sections from Jupyter notebooks. It allows you to create reusable notebook templates and compose custom notebooks from predefined sections.

### Features

- **Extract sections**: Parse notebook structure and save as JSON templates
- **Create selection files**: Generate selection templates for choosing which sections to include
- **Compose notebooks**: Build new notebooks from templates and user selections
- **Modular workflow**: Reuse common notebook sections across multiple documents

### Workflow

1. Extract sections from an existing notebook into a JSON template
2. Create a selection file to specify which sections you want
3. Compose a new notebook using the template and your selections

### Usage

**Extract sections from a notebook:**
```sh
python compose.py -nb <notebook> [-o <output.json>]
```

**Create a selection file from template:**
```sh
python compose.py -t <template> --create-selection
```

**Create a selection file from notebook:**
```sh
python compose.py -nb <notebook> --create-selection
```

**Compose a notebook from template and selection:**
```sh
python compose.py -t <template> -s <selection> -o <output.ipynb>
```

### Variable Replacement

The compose script supports variable replacement in templates. You can define placeholder variables in your notebook cells (e.g., `{{variable_name}}`), and then specify their values in the selection file. When composing the notebook, these placeholders will be replaced with the actual values you provide.

### Options

- `-nb, --notebook`: Path to the input notebook (.ipynb)
- `-t, --template`: Path to JSON template file containing extracted sections
- `-s, --selection`: Path to JSON file with selected sections to include
- `-o, --output`: Output path (default: `output.ipynb` for notebooks, auto-generated for JSON)
- `--create-selection`: Generate a selection template file

### Examples

**Extract sections from a notebook to create a template:**
```sh
python compose.py -nb notebook.ipynb
```
*Output: `notebook.json` containing all sections from the notebook*

**Create a selection file from the template:**
```sh
python compose.py -t notebook.json --create-selection
```
*Output: `notebook_selection.json` with toggleable section choices*

**Compose a new notebook from template and selection:**
```sh
python compose.py -t notebook.json -s notebook_selection.json -o custom_notebook.ipynb
```
*Output: `custom_notebook.ipynb` with only the selected sections*

**Direct workflow (extract and create selection from notebook):**
```sh
python compose.py -nb notebook.ipynb --create-selection
```
*Output: Both `notebook.json` and `notebook_selection.json`*

## generate_auto_theme.py

The `generate_auto_theme.py` script generates a CSS file that automatically switches between light and dark themes based on the user's system preferences for NBConvert's "Lab" template.

### Features

- Automatically adapts to system theme preferences (light/dark mode)
- Uses CSS `prefers-color-scheme` media query
- Updates NBConvert Lab template files automatically
- Creates `theme-auto.css` for seamless theme switching

### Usage

```sh
python generate_auto_theme.py
```

**This will:**
1. Generate the `theme-auto.css` file with auto-switching theme styles
2. Update `index.html.j2` to include the new theme stylesheet
3. Update `conf.json` in the JupyterLab template directory

### Output

The script modifies files in the NBConvert Lab template directory to enable automatic theme detection and switching between light and dark modes based on user system preferences.

