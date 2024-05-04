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
            ADDED:\n {self.added}\n
            DELETED: {self.deleted}\n
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
    Clause FILE contains name of changed file, ADDED contains lines which are added to file, \
    DELETED contains list of lines which are deleted from file. \
    Summary messages should contain name of changed file in summary header")


def generate_commit_message(length_characters: int, style: str, changes: str) -> str:
    prompt = (f"{prompt_role} \
        LENGTH: max {length_characters} characters \
        STYLE: {style} \
        COMMIT_CHANGES: {changes}")
    return ask_chatgpt([{"role": "user", "content": prompt}])


def get_cached_changes() -> Dict[str, FileChange]:
    # Wywołanie polecenia git diff --cached i pobranie wyniku
    diff_output = subprocess.check_output(["git", "diff", "--cached"]).decode("utf-8")

    # Podzielenie wyniku na linie
    diff_lines = diff_output.split("\n")

    # Inicjalizacja słownika do przechowywania zmian w plikach
    changes = {}
    current_file = None

    # Analiza wyniku
    for line in diff_lines:
        if line.startswith("diff --git"):
            # Znaleziono nowy plik, zapisujemy jego nazwę
            current_file = line.split(" ")[-1][2:]
            changes[current_file] = FileChange(current_file)
        elif line.startswith("+++ ") or line.startswith("--- "):
            # Ignorujemy linie z nagłówkami pliku
            pass
        elif line.startswith("@@ "):
            # Ignorujemy linie z informacjami o zmianach
            # changes[current_file].append_modified_line(line)
            pass
        elif line.startswith("+"):
            # Znaleziono dodany wiersz, dodajemy go do zmian w bieżącym pliku
            if current_file:
                changes[current_file].append_added_line(line[1:])
        elif line.startswith("-"):
            # Znaleziono usunięty wiersz, dodajemy go do zmian w bieżącym pliku
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


generate_commit_messages()
