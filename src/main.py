import json
from pathlib import Path
from ollama import chat, generate
import seedir as sd
from rich import print as rprint

# Embedded in system prompt: shows.md and movies.md
# https://github.com/jellyfin/jellyfin.org/tree/master/docs/general/server/media

ROOT_PATH = Path(__file__).parent
BASE_PROMPT = """
Below, documents are given that describe the naming convention for shows and
movies in Jellyfin. Later, I want you to transform a file tree (folder
structure) to fit the convention. Respond with a modified file tree where files
and directories are renamed according to the naming convention in the documents.
Do not introduce any new information that is not given by the file and directory
names. Do not delete or add any files or directories. The number and order of
files and directories must remain the same. Leave types of files that are not
mentioned in the documents (e.g. subtitles or extras) unchanged.


The documents are as follows:

{documents}
"""

SECOND_PROMPT = """
The input file tree is as follows:

{file_tree}
"""

SYSTEM_PROMPT = """
You are a helpful assistant that helps to organize folder structures for movies
and shows. You respond with a JSON file that contains the new folder structure.
"""

# Okay, I'm ready to analyze the provided documents and answer questions based
# on them.  Please ask your questions! I'll do my best to extract the
# information accurately. Just let me know what you want to know.

# Transform the input file tree according to the naming conventions in the
# documents. Use the files and directories from the file tree enclosed in the
# <filetree> tag.


# Your response should start like this:

# ```
# <filetree>
# Movies and Shows/


# Below, a file tree and documents are given. The file tree consists of a
# collection of movies and shows and is enclosed in the <filetree> tag. Please
# name the files and directories in this file tree in the way described in the
# documents. Respond with a modified file tree where files and directories are
# renamed according to the naming convention in the documents. Enclose your file
# tree with the <filetree> tag. Use the same format and symbols for your new file
# tree as the input file tree. Do not introduce any new information that is not
# given by the file and directory names. Do not delete or add any files or
# directories. The number and order of files and directories must remain the same.
# Leave types of files that are not mentioned in the documents unchanged.

# The input file tree is from the data directory of a Jellyfin server. It is a
# collection of movies and shows. The goal is to name the files and directories
# in a consistent and deterministic way, as described in the documents. The
# documents are Markdown files from the Jellyfin documentation, describing their
# naming conventions.


# ```filetree
# Movies and Shows/
# ├─Show Name 1 (2010) Season 7/
# │ ├─Show Name 1 S07E01.mkv
# │ ├─Show Name 1 S07E02.mkv
# │ ├─Show Name 1 S07E03.mkv
# ├─Movie Name 1.mkv
# ├─Show Name 2 Season 1/
# │ ├─Show Name 2 S01E01.mp4
# ...
# ```

# The input file tree is from the data directory of a Jellyfin server. It is a
# collection of movies and shows. The goal is to name the files and directories
# in a consistent and deterministic way, as described in the documents. The
# documents are Markdown files from the Jellyfin documentation, describing their
# naming conventions.

# The output file tree is as follows:


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
    file_path = ROOT_PATH / name
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist.")
    return file_path.read_text(encoding="utf-8")


def format_prompt_single(path: Path) -> str:
    tree = file_tree_json(media_root)
    tree_str = json.dumps(tree, indent=2, ensure_ascii=False)
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

    tree = file_tree_str(media_root)
    # tree = json.dumps(tree, indent=2, ensure_ascii=False)
    Path("tree.json").write_text(tree, encoding="utf-8")
    prompt2 = remove_line_wraps(SECOND_PROMPT).format(file_tree=tree)
    return prompt1, prompt2


def model_chat(
    model: str, prompt1: str, prompt2: str, print_response: bool = True
) -> str:
    """Queries the model with a prompt."""
    stream = chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt1},
            {
                "role": "assistant",
                "content": "Okay, I'm ready to analyze the provided file tree and answer with an updated file tree. My next response will be the a file tree in the given format.",
                # "content": "Okay, I'm ready to analyze the provided file tree and answer with an updated file tree. My next response will be a valid JSON file.",
            },
            {"role": "user", "content": prompt2},
        ],
        stream=True,
    )

    response = ""
    if print_response:
        print()
        print("Response:")
        print()
    for chunk in stream:
        response += chunk["message"]["content"]
        if print_response:
            print(chunk["message"]["content"], end="", flush=True)
    if print_response:
        print()
    return response


def model_generate(model: str, prompt: str, print_response: bool = True) -> str:
    """Queries the model with a prompt."""
    stream = generate(
        model=model,
        prompt=prompt,
        stream=True,
    )

    response = ""
    if print_response:
        print()
        print("Response:")
        print()
    for chunk in stream:
        response += chunk["response"]
        if print_response:
            print(chunk["response"], end="", flush=True)
    if print_response:
        print()
    return response


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


if __name__ == "__main__":
    media_root = Path("C:/Users/Marco/Nextcloud/Movies and Shows")
    curent_path = media_root / "Chernobyl"

    rprint("Selected folder/file:\n\t", curent_path)
    rprint("Name:")
    show_name = input().strip()
    # TODO: Check if the name is valid
    rprint("You selected:\n\t", show_name)
    rprint("Year:")
    year = input().strip()

    # print(
    #     json.dumps(
    #         file_tree_json(
    #             media_root
    #             / "Common.Side.Effects.S01.1080p.WEBRip.x265-KONTRAST"
    #         ),
    #         indent=4,
    #         ensure_ascii=False,
    #     )
    # )

    # prompt1, prompt2 = format_prompts(media_root)
    # Path("prompt.txt").write_text(prompt1, encoding="utf-8")
    # # prompt = "Write a poem about nature, but format it using custom tags like
    # # <line> for each line and <stanza> for each stanza."
    # models = [
    #     "gemma3:12b",
    #     "deepseek-r1:14b",
    #     "qwen2.5:14b",
    #     "qwen2.5-coder:14b",
    #     "dolphin3",
    # ]
    # response = model_chat(models[0], prompt1, prompt2)
