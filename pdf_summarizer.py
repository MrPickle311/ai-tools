import sys

from langchain.chains.summarize import load_summarize_chain
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI

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


def main():
    if len(sys.argv) < 4:
        raise Exception('Usage: python pdf_summarizer.py '
                        '<input pdf file> <start_page> <end_page>  <output .md file>')

    filename = sys.argv[1]
    start_page = int(sys.argv[2])
    end_page = int(sys.argv[3])
    output_filename = sys.argv[4]

    llm = OpenAI()

    map_prompt_template = PromptTemplate(template=MAP_PROMPT, input_variables=["text"])
    combine_prompt_template = PromptTemplate(template=COMBINE_PROMPT, input_variables=["text"])

    summary_chain = load_summarize_chain(llm=llm,
                                         chain_type='map_reduce',
                                         map_prompt=map_prompt_template,
                                         combine_prompt=combine_prompt_template,
                                         )

    pages = get_pages_from_pdf(filename, start_page, end_page)
    output = summary_chain.run(pages)
    save_md_file(output_filename, output)


if __name__ == '__main__':
    main()
