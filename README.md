# nbtools

This repository contains scripts to manage and compose Jupyter notebooks for the JupyterLab template. The main scripts are `toc.py`, `compose.py`, and `generate_auto_theme.py`.

## toc.py

The `toc.py` script generates a Table of Contents (ToC) for a Jupyter notebook.

### Usage

```sh
python toc.py <input_notebook> [output_notebook]
```

- `input_notebook`: The path to the input Jupyter notebook file.
- `output_notebook` (optional): The path to save the output Jupyter notebook file with the ToC. If not provided, the ToC will be printed to the console.

### Example

```sh
python toc.py notebook.ipynb notebook_with_toc.ipynb
```

## compose.py

The `compose.py` script allows you to compose or extract sections from Jupyter notebooks.

### Usage

```sh
python compose.py -nb <notebook> [-s <selection>] [-o <output>] [--create-selection]
python compose.py -t <template> [-s <selection>] [-o <output>] [--create-selection]
```

- `-nb, --notebook`: Path to the input notebook (.ipynb). Used to either extract sections or compose a notebook.
- `-t, --template`: Path to JSON template file (sections.json).
- `-s, --selection`: Path to user dictionary with selected sections' structure (required for composition).
- `-o, --output`: Path to save the composed notebook or sections JSON (default: `output.ipynb`).
- `--create-selection`: Create a `selection.json` from the template or notebook.

### Examples

1. **Extract sections from a notebook:**

    ```sh
    python compose.py -nb notebook.ipynb
    ```

    This will extract sections from `notebook.ipynb` and save them to `notebook.json`.

2. **Compose a notebook using a template and selection:**

    ```sh
    python compose.py -t template.json -s selection.json -o composed_notebook.ipynb
    ```

    This will compose a new notebook based on `template.json` and `selection.json`, and save it to `composed_notebook.ipynb`.

3. **Create a selection file from a template:**

    ```sh
    python compose.py -t template.json --create-selection
    ```

    This will create a `template_selection.json` file based on `template.json`.

4. **Create a selection file from a notebook:**

    ```sh
    python compose.py -nb notebook.ipynb --create-selection
    ```

    This will create a `notebook_selection.json` file based on `notebook.ipynb`.

## generate_auto_theme.py

The `generate_auto_theme.py` script generates a CSS file that automatically switches between light and dark themes based on the user's system preferences for the NBConvert "Lab" template.

### Usage

Simply run the script to generate the `theme-auto.css` file and update the necessary template files.

```sh
python generate_auto_theme.py
```

This will generate the `theme-auto.css` file and update the `index.html.j2` and `conf.json` files in the JupyterLab template directory.

