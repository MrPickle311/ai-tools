from typing import List

from notion_client import NotionClient




def add_text_to_notion_page(client: NotionClient, page_url: str, text: str) -> None:
    page_id = _extractor.get_id_from_url(page_url)
    client.append_text(text=text, parent_id=page_id)


def add_heading_2_to_notion_page(client: NotionClient, page_url: str, text: str) -> None:
    page_id = _extractor.get_id_from_url(page_url)
    client.append_heading_2(text=text, parent_id=page_id)


def add_bullet_items_to_notion_page(client: NotionClient, page_url: str, items: List[str]) -> None:
    page_id = _extractor.get_id_from_url(page_url)
    client.append_bulleted_list_items(items=items, parent_id=page_id)
