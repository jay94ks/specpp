"""examples/doom/wad.md 의 # Domain(Doom.WadLump/Doom.WadFile/Doom.Palette) 참조 구현."""
import struct


class WadLump:
    def __init__(self, name, offset, size):
        self.name = name
        self.offset = offset
        self.size = size


class WadFile:
    HEADER_FMT = "<4sii"
    DIR_ENTRY_FMT = "<ii8s"

    # spp-source: examples/doom/wad.md#Domain.Class:Doom.WadFile
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            data = f.read()

        magic, numlumps, infotableofs = struct.unpack_from(self.HEADER_FMT, data, 0)
        if magic not in (b"IWAD", b"PWAD"):
            raise ValueError(f"not a WAD file (magic={magic!r})")

        self.lumps = []
        entry_size = struct.calcsize(self.DIR_ENTRY_FMT)
        for i in range(numlumps):
            offset, size, raw_name = struct.unpack_from(
                self.DIR_ENTRY_FMT, data, infotableofs + i * entry_size
            )
            name = raw_name.split(b"\x00", 1)[0].decode("ascii")
            self.lumps.append(WadLump(name, offset, size))

        self._data = data

    def findLump(self, name):
        name = name.upper()
        found = -1
        for i, lump in enumerate(self.lumps):
            if lump.name.upper() == name:
                found = i  # 나중에 나열된 것이 이긴다 (패치 WAD가 덮어쓰는 규칙).
        return found

    def readLump(self, index):
        lump = self.lumps[index]
        return self._data[lump.offset : lump.offset + lump.size]


class Palette:
    # spp-source: examples/doom/wad.md#Domain.Class:Doom.Palette
    def __init__(self, playpal_bytes):
        base = playpal_bytes[:768]
        self._colors = [
            tuple(base[i : i + 3]) for i in range(0, len(base), 3)
        ]

    def colorAt(self, palette_index):
        return self._colors[palette_index]


def build_wad_bytes(lumps):
    """테스트용 헬퍼: [(name, data), ...] 로 WAD 파일 바이트를 만든다.

    실제 원본 wad.md의 포맷 그대로 헤더 12바이트 + lump 데이터 + 디렉터리를 만든다.
    """
    header_size = 12
    body = b"".join(data for _, data in lumps)
    directory = b""
    offset = header_size
    for name, data in lumps:
        name_bytes = name.encode("ascii")[:8].ljust(8, b"\x00")
        directory += struct.pack("<ii8s", offset, len(data), name_bytes)
        offset += len(data)

    header = struct.pack("<4sii", b"PWAD", len(lumps), header_size + len(body))
    return header + body + directory
