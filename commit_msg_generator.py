import subprocess
from typing import Dict

import openai


class FileChange:
    def __init__(self, filename: str):
        self.filename = filename
        self.added = ''
        self.deleted = ''

    def append_added_line(self, line: str):
        self.added += line + '\n'

    def append_deleted_line(self, line: str):
        self.deleted += line + '\n'

    def to_string(self):
        return f"""\n
            FILE: {self.filename}
            ADDED LINES:\n {self.added}\n
            DELETED LINES:\n {self.deleted}\n
            """


client = openai.OpenAI()


def ask_chatgpt(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )
    return response.choices[0].message.content


prompt_role = ("You are an commit message analyzer. \
    Your task is to analyze commit diffs and write summary messages about it. \
    You should respect the instructions: the LENGTH, and the STYLE, COMMIT_CHANGES. \
    Clause FILE contains name of changed file, ADDED LINES contains lines which are added to file, \
    DELETED LINES contains list of lines which are deleted from file. \
    Summary messages should contain name of changed file in summary header. \
    I expect the following output format: \n\
    Summary of file1: \n\
    - change1 ... \n\
    - change2 ... \n\
    ... \n\
    Summary of file2: \n\
    - change1 ... \n\
    - change2 ... \n\
    ...")


def generate_commit_message(length_characters: int, style: str, changes: str) -> str:
    prompt = (f"{prompt_role} \
        LENGTH: max {length_characters} characters \
        STYLE: {style} \
        COMMIT_CHANGES: {changes}")
    return ask_chatgpt([{"role": "user", "content": prompt}])


def get_cached_changes() -> Dict[str, FileChange]:
    diff_output = subprocess.check_output(["git", "diff", "--cached"]).decode("utf-8")

    diff_lines = diff_output.split("\n")

    changes = {}
    current_file = None

    for line in diff_lines:
        if line.startswith("diff --git"):
            current_file = line.split(" ")[-1][2:]
            changes[current_file] = FileChange(current_file)
        elif line.startswith("+++ ") or line.startswith("--- "):
            pass
        elif line.startswith("@@ "):
            pass
        elif line.startswith("+"):
            if current_file:
                changes[current_file].append_added_line(line[1:])
        elif line.startswith("-"):
            if current_file:
                changes[current_file].append_deleted_line(line[1:])

    return changes


def generate_commit_messages():
    changes = get_cached_changes()

    message = ''

    for file_path, file_changes in changes.items():
        message += file_changes.to_string()

    resp = generate_commit_message(50, 'BULLET POINT LIST OF CHANGES', message)
    print(resp)


if __name__ == '__main__':
    generate_commit_messages()
