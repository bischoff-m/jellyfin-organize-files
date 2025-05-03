import json
from pathlib import Path
import seedir as sd

from definitions import ROOT_PATH
from prompts import BASE_PROMPT, SECOND_PROMPT


def remove_line_wraps(text: str) -> str:
    """Removes line wraps from blocks of text."""
    lines = text.splitlines()
    result = ""
    for line1, line2 in zip(["\n"] + lines, lines + ["\n"]):
        if len(line1.strip()) == 0 or len(line2.strip()) == 0:
            result += line1 + "\n"
        else:
            result += line1.rstrip() + " "
    return result.strip()


def file_tree_str(path: Path, indent: int = 2) -> str:
    return sd.seedir(path, style="lines", printout=False, indent=indent)


def file_tree_json(path: Path) -> dict:
    tree = dict()
    tree["path"] = path.as_posix()
    tree["name"] = path.name
    tree["type"] = "directory" if path.is_dir() else "file"
    if path.is_dir():
        children = []
        for child in path.iterdir():
            children.append(file_tree_json(child))
        tree["children"] = children
    return tree


def read_file(name: str) -> str:
    """Reads a file from the data directory."""
    file_path = ROOT_PATH / "data" / name
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist.")
    return file_path.read_text(encoding="utf-8")


def format_prompt_single(path: Path) -> str:
    tree = file_tree_json(path)
    tree_str = json.dumps(tree, indent=4, ensure_ascii=False)
    Path("tree.json").write_text(tree_str, encoding="utf-8")

    documents = [
        read_file("shows_sub.md"),
        read_file("movies_sub.md"),
    ]
    return remove_line_wraps(BASE_PROMPT).format(
        file_tree=tree_str, documents="\n\n".join(documents)
    )


def format_prompts(path: Path) -> tuple[str, str]:
    documents = [
        read_file("shows_sub.md"),
        read_file("movies_sub.md"),
    ]
    prompt1 = remove_line_wraps(BASE_PROMPT).format(
        documents="\n\n".join(documents)
    )

    tree = file_tree_str(path)
    # tree = json.dumps(tree, indent=2, ensure_ascii=False)
    Path("tree.json").write_text(tree, encoding="utf-8")
    prompt2 = remove_line_wraps(SECOND_PROMPT).format(file_tree=tree)
    return prompt1, prompt2


def parse_file_tree(file_tree: str) -> str:
    """Parses the file tree into a string."""
    lines = file_tree.splitlines()
    result = ""
    for line in lines:
        if line.startswith("  "):
            result += line[2:] + "\n"
        else:
            result += line + "\n"
    return result.strip()
