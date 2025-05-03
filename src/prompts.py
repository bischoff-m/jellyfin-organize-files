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
