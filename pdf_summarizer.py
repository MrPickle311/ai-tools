import os
import sys
from typing import List

from langchain.chains.summarize import load_summarize_chain
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from pyxtension.streams import stream

from notion_client import NotionClient
from tools import get_pages_from_pdf, save_md_file

COMBINE_PROMPT = """
    Write a concise summary of the following text delimited by triple backquotes.
    Return your response in markdown format. Write title of summarized data as header 2 and extract 
    important information to bullet points
    ```{text}```
    MARKDOWN SUMMARY:
    """

MAP_PROMPT = """
    Write a concise summary of the following:
    "{text}"
    CONCISE SUMMARY:
    """


def get_summary_from_pdf(end_page, filename, llm, start_page):
    map_prompt_template = create_prompt_template(MAP_PROMPT)
    combine_prompt_template = create_prompt_template(COMBINE_PROMPT)
    summary_chain = load_summarize_chain(llm=llm,
                                         chain_type='map_reduce',
                                         map_prompt=map_prompt_template,
                                         combine_prompt=combine_prompt_template,
                                         )
    pages = get_pages_from_pdf(filename, start_page, end_page)
    output = summary_chain.run(pages)
    return output


def create_prompt_template(template: str) -> PromptTemplate:
    return PromptTemplate(template=template, input_variables=["text"])


def extract_args():
    filename = sys.argv[1]
    start_page = int(sys.argv[2])
    end_page = int(sys.argv[3])
    output_dest = sys.argv[4]
    return end_page, filename, output_dest, start_page


def print_usage():
    print('Usage: python pdf_summarizer.py '
          '<input pdf file> <start_page> <end_page>  <output .md file>'
          '\nExample: python3 pdf_summarizer.py /home/example-user/book.pdf 3 6 /home/example-user/out.md')


def cleanup_lines(lines: List[str], page: str) -> List[str]:
    return (stream(lines)
            .filter(lambda line: line != '')
            .filter(lambda line: page not in line)
            .filter(lambda line: not line.startswith('#'))
            .map(lambda line: line.replace('-', ''))
            .map(lambda line: line.replace('"', ''))
            .map(lambda line: line[1:] if line.startswith(' ') else line)
            .toList())


def save_to_notion(text: str, page: str) -> None:
    client = NotionClient(os.environ['NOTION_TOKEN'])

    lines = text.splitlines()
    lines = lines[1:-1]

    client.append_heading_2(parent_id=page, text=lines[0][2:-1])

    lines = cleanup_lines(lines, page)
    client.append_bulleted_list_items(parent_id=page, items=lines)


def is_notion_page(output_filename: str) -> bool:
    return output_filename.startswith('https://www.notion.so')


def main():
    if len(sys.argv) < 4:
        print_usage()
        return

    end_page, filename, output_dest, start_page = extract_args()

    llm = OpenAI()

    summary = get_summary_from_pdf(end_page, filename, llm, start_page)

    if is_notion_page(output_dest):
        save_to_notion(text=summary, page=output_dest)
        return

    save_md_file(output_dest, summary)


if __name__ == '__main__':
    main()
