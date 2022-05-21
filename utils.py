import re

AUTHOR_RE = re.compile(r'Автор: (\[[^\)]+\))')


def parse_author(text: str) -> str:
    return AUTHOR_RE.search(text).group(1)
