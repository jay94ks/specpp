"""std/ui/filedialog.md reference implementation (tkinter-based)."""
from tkinter import filedialog


def _parseFilters(filters):
    """"텍스트 문서 (*.txt)" -> ("텍스트 문서", "*.txt") 로 변환한다."""
    result = []
    for f in filters:
        if "(" in f and f.endswith(")"):
            name, pattern = f.rsplit("(", 1)
            result.append((name.strip(), pattern[:-1].strip()))
        else:
            result.append((f, "*.*"))
    return result


class FileDialog:
    @staticmethod
    def showOpen(title, filters):
        path = filedialog.askopenfilename(title=title, filetypes=_parseFilters(filters))
        return path or None

    @staticmethod
    def showSave(title, filters, suggestedName):
        path = filedialog.asksaveasfilename(title=title, filetypes=_parseFilters(filters), initialfile=suggestedName)
        return path or None
