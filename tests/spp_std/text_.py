"""std/text/{string,json,regex}.md reference implementation."""
import json as _json
import re as _re


class String:
    @staticmethod
    def length(text):
        return len(text)

    @staticmethod
    def toUpper(text):
        return text.upper()

    @staticmethod
    def toLower(text):
        return text.lower()

    @staticmethod
    def trim(text):
        return text.strip()

    @staticmethod
    def split(text, separator):
        return text.split(separator)

    @staticmethod
    def join(items, separator):
        return separator.join(items)

    @staticmethod
    def replace(text, target, replacement):
        return text.replace(target, replacement)

    @staticmethod
    def contains(text, part):
        return part in text

    @staticmethod
    def indexOf(text, part):
        return text.find(part)

    @staticmethod
    def substring(text, start, end):
        if start < 0 or end > len(text) or start > end:
            raise ValueError("substring out of range")
        return text[start:end]


class Json:
    @staticmethod
    def stringify(value):
        return _json.dumps(value)

    @staticmethod
    def parse(text):
        return _json.loads(text)


class Regex:
    def __init__(self, pattern):
        self._re = _re.compile(pattern)

    def test(self, text):
        return self._re.search(text) is not None

    def match(self, text):
        m = self._re.search(text)
        return m.group(0) if m else None

    def matchAll(self, text):
        return [m.group(0) for m in self._re.finditer(text)]

    def replace(self, text, replacement):
        return self._re.sub(replacement, text, count=1)

    def replaceAll(self, text, replacement):
        return self._re.sub(replacement, text)
