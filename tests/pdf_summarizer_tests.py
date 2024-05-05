from langchain_core.documents import Document

from pdf_summarizer import trim_content


class TestTrimContent:

    #  Given a valid begin_paragraph and end_paragraph, the function should correctly
    #  trim the content of all pages in the input list and return the modified list.
    def test_valid_begin_and_end_paragraph(self):
        # Given
        begin_paragraph = "Lorem ipsum"
        end_paragraph = "quis nostrud exercitation ullamco"
        pages = [
            Document(page_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit."),
            Document(page_content="Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."),
            Document(
                page_content="Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.")
        ]

        # When
        result = trim_content(begin_paragraph, end_paragraph, pages)

        # Then
        assert result[0].page_content == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        assert result[1].page_content == "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        assert result[2].page_content == "Ut enim ad minim veniam, "

    #  Given a begin_paragraph or end_paragraph that does not exist in the content of any
    #  page in the input list, the function should return the original input list without any modifications.
    def test_invalid_begin_or_end_paragraph(self):
        # Given
        begin_paragraph = "Nonexistent"
        end_paragraph = "Nonexistent"
        pages = [
            Document(page_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit."),
            Document(page_content="Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."),
            Document(
                page_content="Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.")
        ]

        # When
        result = trim_content(begin_paragraph, end_paragraph, pages)

        # Then
        assert result[0].page_content == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        assert result[1].page_content == "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        assert result[
                   2].page_content == "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."

    #  Given a valid begin_paragraph and no end_paragraph, the function should correctly trim the content of all pages
    #  from the beginning of the input list to the specified begin_paragraph and return the modified list.
    def test_trim_content_valid_begin_paragraph_no_end_paragraph(self):
        # Given
        begin_paragraph = "Lorem ipsum"
        end_paragraph = None
        pages = [
            Document(page_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit."),
            Document(page_content="Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."),
            Document(page_content="Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."),
        ]

        # When
        result = trim_content(begin_paragraph, end_paragraph, pages)

        # Then
        assert len(result) == 3
        assert result[0].page_content == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        assert result[1].page_content == "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        assert result[2].page_content == "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."

    #  Given an empty begin_paragraph and end_paragraph, the function should return the original input list without any modifications.
    def test_empty_begin_and_end_paragraph(self):
        # Given
        begin_paragraph = ""
        end_paragraph = ""
        pages = [Document(page_content="Page 1"), Document(page_content="Page 2"), Document(page_content="Page 3")]

        # When
        result = trim_content(begin_paragraph, end_paragraph, pages)

        # Then
        assert result == [Document(page_content="Page 1"), Document(page_content="Page 2"),
                          Document(page_content="Page 3")]

    #  Given an empty input list and any begin_paragraph and end_paragraph, the function should return an empty list.
    def test_empty_input_list(self):
        # Given
        begin_paragraph = "Lorem ipsum"
        end_paragraph = "dolor sit amet"
        pages = []

        # When
        result = trim_content(begin_paragraph, end_paragraph, pages)

        # Then
        assert result == []

    #  Given a begin_paragraph or end_paragraph that exists in the content of multiple pages in the input list,
    #  the function should only trim the content of the first or last page that contains the specified paragraph, respectively.
    def test_trim_content_multiple_pages(self):
        # Given
        begin_paragraph = "Lorem ipsum"
        end_paragraph = "dolor sit amet"
        pages = [
            Document(page_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit."),
            Document(page_content="Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."),
            Document(page_content="Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."),
            Document(
                page_content="Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."),
            Document(page_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit."),
        ]

        # When
        trimmed_pages = trim_content(begin_paragraph, end_paragraph, pages)

        # Then
        assert trimmed_pages[0].page_content == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        assert trimmed_pages[1].page_content == "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        assert trimmed_pages[2].page_content == "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."
        assert trimmed_pages[
                   3].page_content == "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        assert trimmed_pages[4].page_content == "Lorem ipsum "
