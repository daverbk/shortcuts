from datetime import datetime


def format_time(date_str):
    return datetime.fromisoformat(date_str).strftime(format('%H:%M'))


def strip_link(data: str):
    return data.split('| Links |')[0].rstrip('\r\n')


def to_do_block(content):
    return block(
        block_type='to_do',
        content=content
    )


def heading_2_block(content):
    return block(
        block_type='heading_2',
        content=content
    )


def paragraph_block(content, link=None):
    return block(
        block_type='paragraph',
        content=content,
        link=link
    )


def block(block_type: str, content, link=None):
    return {
        'object': 'block',
        'type': block_type,
        block_type: rich_text(content, link)
    }


def rich_text(content, link=None):
    return {
        'rich_text':
            [
                {
                    'text': {
                        'content': content,
                        'link': None if link is None else {'url': link}
                    }
                }
            ]
    }
