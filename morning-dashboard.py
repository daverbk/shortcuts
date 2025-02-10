import os

from notion_client import Client

token = os.environ["NOTION_TOKEN"]
block = os.environ["BLOCK_ID"]
content = os.environ["CONTENT"]
notion = Client(auth=token)

response = notion.blocks.update(
    block_id=block,
    paragraph={
        "rich_text": [
            {
                "text": {
                    "content": content
                }
            }
        ]
    }
)
