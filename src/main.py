import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ollama import Message, chat
from rich import print as rprint

from definitions import ROOT_PATH
from io_util import file_tree_json, file_tree_str, remove_line_wraps
from prompts import SYSTEM_PROMPT

# Embedded in system prompt: shows.md and movies.md
# https://github.com/jellyfin/jellyfin.org/tree/master/docs/general/server/media

models = [
    "gemma3:12b",
    "deepseek-r1:14b",
    "qwen2.5:14b",
    "qwen2.5-coder:14b",
    "dolphin3",
]


def model_chat(
    model: str,
    messages: Sequence[Mapping[str, Any] | Message] | None,
    print_response: bool = True,
) -> str:
    """Queries the model with a prompt."""
    stream = chat(
        model=model,
        messages=messages,
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


# def example_tree(example: dict[str, Any]) -> str:
#     """Formats a file tree for the example."""
#     folder = example["input"]["file_tree"]["path"]
#     tree = file_tree_str(Path(folder))


if __name__ == "__main__":
    media_root = Path("C:/Users/Marco/Nextcloud/Movies and Shows")

    example_files = (ROOT_PATH / "data").glob("*.example.json")
    examples = [json.loads(file.read_text()) for file in example_files]
    example_prompts = [
        [
            {
                "role": "user",
                "content": json.dumps(
                    example["input"], indent=4, ensure_ascii=False
                ),
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    example["output"], indent=4, ensure_ascii=False
                ),
            },
        ]
        for example in examples
    ]
    # Flatten the list of examples
    example_prompts = [item for sublist in example_prompts for item in sublist]
    # for example in example_prompts:
    #     print(example["role"] + ":")

    current_path = (
        media_root
        / "Severance.S01.2160p.ATVP.WEB-DL.x265.10bit.HDR.DDP5.1.Atmos-TEPES[rartv]"
    )
    file_tree = file_tree_json(current_path)

    rprint("Selected folder/file:\n\t", current_path)
    rprint("Name:")
    # show_name = input().strip()
    show_name = "Severance"
    # TODO: Check if the name is valid
    rprint("You selected:\n\t", show_name)
    rprint("Year:")
    # year = input().strip()
    year = "2019"

    messages = [
        {
            "role": "system",
            "content": remove_line_wraps(SYSTEM_PROMPT),
        },
        *example_prompts,
        {
            "role": "user",
            "content": json.dumps(
                {
                    "name": show_name,
                    "year": year,
                    "file_tree": file_tree,
                },
                indent=4,
                ensure_ascii=False,
            ),
        },
    ]
    (ROOT_PATH / "data" / "request.json").write_text(
        json.dumps(messages, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    response = model_chat(models[2], messages).strip()
    #     response = """
    # ```json
    # {
    #   "name": "Chernobyl",
    #   "year": 2019,
    #   "type": "directory",
    #   "children": [
    #     {
    #       "name": "Season 01",
    #       "type": "directory",
    #       "children": [
    #         {
    #           "name": "Chernobyl S01E01.mkv",
    #           "type": "file",
    #           "origin": "C:/Users/Marco/Nextcloud/Movies and Shows/Chernobyl/Chernobyl S01E01.mkv"
    #         },
    #         {
    #           "name": "Chernobyl S01E02.mkv",
    #           "type": "file",
    #           "origin": "C:/Users/Marco/Nextcloud/Movies and Shows/Chernobyl/Chernobyl S01E02.mkv"
    #         },
    #         {
    #           "name": "Chernobyl S01E03.mkv",
    #           "type": "file",
    #           "origin": "C:/Users/Marco/Nextcloud/Movies and Shows/Chernobyl/Chernobyl S01E03.mkv"
    #         },
    #         {
    #           "name": "Chernobyl S01E04.mkv",
    #           "type": "file",
    #           "origin": "C:/Users/Marco/Nextcloud/Movies and Shows/Chernobyl/Chernobyl S01E04.mkv"
    #         },
    #         {
    #           "name": "Chernobyl S01E05.mkv",
    #           "type": "file",
    #           "origin": "C:/Users/Marco/Nextcloud/Movies and Shows/Chernobyl/Chernobyl S01E05.mkv"
    #         }
    #       ]
    #     }
    #   ]
    # }
    # ```""".strip()

    try:
        response_json = json.loads(response)
    except json.JSONDecodeError:
        pass
    try:
        lines = response.splitlines()
        response_json = json.loads("\n".join(lines[1:-1]))
    except json.JSONDecodeError as e:
        rprint(
            "[red]Invalid chat response.[/red] Expected JSON, got:\n",
            "\n".join(lines[:3]),
            "...",
        )
        raise e

    print("Response JSON:")
    (ROOT_PATH / "data" / "response.json").write_text(
        json.dumps(response_json, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

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
    # response = model_chat(models[0], prompt1, prompt2)
