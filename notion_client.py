from typing import Dict, Any, List

import requests
from pyxtension.streams import stream
from requests import Response

"""
All requests return either a json object or dict with "error" and "code" values
"""


class IdExtractor:
    FIRST_HYPHEN_POSITION = 8
    SECOND_HYPHEN_POSITION = FIRST_HYPHEN_POSITION + 4
    THIRD_HYPHEN_POSITION = SECOND_HYPHEN_POSITION + 4
    FOURTH_HYPHEN_POSITION = THIRD_HYPHEN_POSITION + 4
    NOTION_PAGE_BASE_URL = 'https://www.notion.so'

    def get_id_from_url(self, url: str) -> str:
        if url.startswith(self.NOTION_PAGE_BASE_URL):
            return self._extract_id_from_url(url)

        return url

    @staticmethod
    def _add_hyphen_at(result: str, pos: int) -> str:
        return result[:pos] + '-' + result[pos:]

    def _extract_id_from_url(self, url: str) -> str:
        result: str = url.split('/')[-1]
        result: str = result.split('-')[-1]
        hyphens_count = 0
        result = self._add_hyphen_at(result, self.FIRST_HYPHEN_POSITION)
        hyphens_count += 1
        result = self._add_hyphen_at(result, self.SECOND_HYPHEN_POSITION + hyphens_count)
        hyphens_count += 1
        result = self._add_hyphen_at(result, self.THIRD_HYPHEN_POSITION + hyphens_count)
        hyphens_count += 1
        return self._add_hyphen_at(result, self.FOURTH_HYPHEN_POSITION + hyphens_count)


class NotionClient:
    TEXT_BLOCK_TYPES = ["paragraph", "heading_1", "heading_2", "heading_3"]
    BASE_NOTION_API_URL = "https://api.notion.com/v1"

    def __init__(self, notion_token):
        self.headers = {
            'Notion-Version': '2022-06-28',
            'Authorization': 'Bearer ' + notion_token,
            "Content-Type": "application/json"
        }

        self.extractor = IdExtractor()

    def search_page(self, page_title: str = None):
        """
        Search for a page
        :param page_title: The page title
        :return: List of pages
        """
        url = self.BASE_NOTION_API_URL + "/search"
        body = {}
        if page_title is not None:
            body["query"] = page_title

        response = requests.request("POST", url, headers=self.headers, params=body)
        return self._response_or_error(response)

    def get_page(self, page_id: str):
        page_id = self.extractor.get_id_from_url(page_id)
        url = self.BASE_NOTION_API_URL + f"/pages/{page_id}"
        response = requests.request("GET", url, headers=self.headers)
        return self._response_or_error(response)

    def get_page_children(self, page_id: str):
        """
        Get page children
        https://developers.notion.com/reference/get-block-children
        :return: Page dict
        """
        page_id = self.extractor.get_id_from_url(page_id)
        return self.get_block_children(page_id)

    def get_block(self, block_id: str):
        """
        Get a Notion block
        https://developers.notion.com/reference/retrieve-a-block
        :return: Block dict
        """
        block_id = self.extractor.get_id_from_url(block_id)
        url = self.BASE_NOTION_API_URL + f"/blocks/{block_id}"
        response = requests.request("GET", url, headers=self.headers)
        return self._response_or_error(response)

    def get_block_children(self, block_id: str):
        """
        Get block children
        https://developers.notion.com/reference/get-block-children
        :return: List of children
        """

        block_id = self.extractor.get_id_from_url(block_id)
        url = self.BASE_NOTION_API_URL + f"/blocks/{block_id}/children"
        response = requests.request("GET", url, headers=self.headers)
        return self._response_or_error(response, "results")

    def update_block(self, block_id: str, content: dict):
        """
        Update a block
        https://developers.notion.com/reference/update-a-block
        :return: Updated block
        """
        block_id = self.extractor.get_id_from_url(block_id)
        url = self.BASE_NOTION_API_URL + f"/blocks/{block_id}"
        response = requests.request("PATCH", url, headers=self.headers, json=content)
        return self._response_or_error(response)

    def append_child_blocks(self, parent_id: str, children: []):
        """
        Append a block
        https://developers.notion.com/reference/patch-block-children
        :param parent_id: The parent block where children are added
        :param children: Array of blocks to be added
        :return: Appended blocks
        """
        parent_id = self.extractor.get_id_from_url(parent_id)
        url = self.BASE_NOTION_API_URL + f"/blocks/{parent_id}/children"
        response = requests.request(
            "PATCH",
            url,
            headers=self.headers,
            json={"children": children}
        )
        return self._response_or_error(response)

    def delete_block(self, block_id: str):
        """
        Delete a block
        https://developers.notion.com/reference/delete-a-block
        :return: Updated block
        """
        block_id = self.extractor.get_id_from_url(block_id)
        url = self.BASE_NOTION_API_URL + f"/blocks/{block_id}"
        response = requests.request("DELETE", url, headers=self.headers)
        return self._response_or_error(response)

    def append_text(self, parent_id: str, text: str):
        """
        Append text block as a child to parent.
        :param parent_id: The block to which the text will be appended
        :param text: The text
        :return: The new block
        """

        parent_id = self.extractor.get_id_from_url(parent_id)
        text_block = {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": text,
                    }
                }]
            }
        }
        return self.append_child_blocks(parent_id, [text_block])

    def append_heading_2(self, parent_id: str, text: str):
        """
        Append Heading 2 block as a child to parent.
        :param parent_id: The block to which the text will be appended
        :param text: The text
        :return: The new block
        """

        parent_id = self.extractor.get_id_from_url(parent_id)
        text_block = {
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": text,
                    }
                }]
            }
        }
        return self.append_child_blocks(parent_id, [text_block])

    def append_bulleted_list_items(self, parent_id: str, items: List[str]) -> None:
        """
        Append Bullet items block as a child to parent.
        :param parent_id: The block to which the text will be appended
        :param items: The text items to be added in the bulleted list
        :return: The new block
        """

        parent_id = self.extractor.get_id_from_url(parent_id)
        bullet_items = self._to_bullet_items(items)
        for bullet_item in bullet_items:
            text_block = {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [bullet_item]
                }
            }
            self.append_child_blocks(parent_id, [text_block])

    def set_text(self, block_id: str, new_text: str):
        """
        Updates a block text. block["type"] must be one from the "text_block_types"

        :param block_id: The block id with text
        :param new_text: New text set for the block
        :return: The new block
        """
        block_id = self.extractor.get_id_from_url(block_id)
        block = self.get_block(block_id)
        block_type = block["type"]

        if block_type not in self.TEXT_BLOCK_TYPES:
            return {"code": 0, "error": "Not a text block"}

        block[block_type]["text"][0]["text"]["content"] = new_text
        return self.update_block(block_id, block)

    def get_text(self, block: dict):
        """
        Gets a block text.
        :param block: block dict
        :return: block text str
        """
        block_type = block["type"]

        if block_type not in self.TEXT_BLOCK_TYPES:
            return None

        return block[block_type]["text"][0]["text"]["content"]

    def add_image(self, parent_id: str, image_url: str):
        """
        Adds an image block as a child to a parent.

        :param parent_id: The parent block id
        :param image_url: The image url
        :return: The parent block
        """
        parent_id = self.extractor.get_id_from_url(parent_id)
        append_children = [
            {
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": image_url
                    }
                }
            }
        ]

        return self.append_child_blocks(parent_id, append_children)

    @staticmethod
    def _to_bullet_items(items: List[str]) -> List[Dict[str, Any]]:
        return stream(items).map(lambda s: {
            "type": "text",
            "text": {
                "content": s
            }
        }).toList()

    @staticmethod
    def _get_image_url(block: dict):
        block_type = block["type"]

        if block_type != "image":
            return None

        return block["image"]["external"]["url"]

    @staticmethod
    def _response_or_error(response: Response, key: str = None) -> Dict[str, Any]:
        response_json = response.json()

        if "message" in response_json:
            message = response_json["message"]
            return {
                "code": response.status_code,
                "error": message
            }

        json_response = response.json()

        if key is not None:
            return json_response[key]

        return json_response
