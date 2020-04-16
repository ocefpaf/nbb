import logging
import pathlib
import sys

from typing import Optional, Union

import black
import easyargs
import nbformat

from isort import SortImports


PathLike = Union[str, pathlib.Path]

# Incomplete list of magics we handle.
skip = (r"%%R", r"%load_ext", r"%%writefile")
comment = (r"%matplotlib inline", r"%time", r"%timeit", r"!")
mod_comment = tuple((f"# {comm}" for comm in comment))


log = logging.getLogger(__name__)


def _nbcell_isort(cell_source: str) -> str:
    return SortImports(file_contents=cell_source).output


def _nbcell_black(cell_source: str) -> str:
    try:
        cell_source = black.format_str(
            cell_source, mode=black.FileMode()
        ).strip()  # we don't want a new line at the end of the notebook cell
    except black.InvalidInput:
        log.warning(f"Could not process cell:\n\n{cell_source}")
    return cell_source


def _beautify_cell(cell_source: str) -> str:
    lines = cell_source.splitlines()

    # short-circuit some cells
    for line in lines:
        if line.startswith(skip):
            return cell_source

    # FIXME: hack way to handle some line magics, cell magics, and system calls.
    cell_source = "\n".join(
        [
            line.replace("%", "# %", 1).replace("!", "# !", 1)
            if line.startswith(comment)
            else line
            for line in lines
        ]
    )
    cell_source = _nbcell_black(_nbcell_isort(cell_source))

    lines = cell_source.splitlines()
    cell_source = "\n".join(
        [
            line.replace("# %", "%", 1).replace("# !", "!", 1)
            if line.startswith(mod_comment)
            else line
            for line in lines
        ]
    )
    return cell_source


def _load_nb(fname: Optional[PathLike] = None) -> PathLike:
    if fname is None:
        fname = sys.argv[1]
    return pathlib.Path(fname)


def _nbb(fname: pathlib.Path) -> None:
    notebook = nbformat.reads(fname.read_text(), as_version=4)
    kernelspec = notebook["metadata"]["kernelspec"]
    if not kernelspec.get("language") == "python":
        log.warning((f"Ignoring {fname} with non python kernelspec {kernelspec}.\n"))
        return

    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            cell_source = cell["source"]
            cell["source"] = _beautify_cell(cell_source)

    nbformat.write(notebook, str(fname))


@easyargs
def nbb(notebook_or_path):
    """Run isort and black on a jupyter notebook treating each cell separately."""
    notebook_or_path = _load_nb(notebook_or_path)

    if notebook_or_path.is_dir():
        notebook_or_path = notebook_or_path.glob("**/*.ipynb")
    else:
        notebook_or_path = [notebook_or_path]

    for nb in notebook_or_path:
        try:
            _nbb(nb)
        except black.InvalidInput as e:
            raise Exception(f"Could not parse {nb}") from e
