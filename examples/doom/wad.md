#!specpp 0.1

# Domain

## Class: Doom.WadLump

원본의 `lumpinfo_t`에 대응한다.

멤버:
- name: string — 최대 8자, 대문자 (예: `"E1M1"`, `"PLAYPAL"`, `"STARTAN1"`).
- offset: int — 파일에서 이 lump 데이터가 시작하는 바이트 위치.
- size: int — 바이트 크기.

[Endianness(little)]
## Class: Doom.WadFile

원본의 WAD 로딩(`w_wad.c`의 `W_InitMultipleFiles` 등)에 대응한다. WAD 파일
포맷: 12바이트 헤더(`"IWAD"` 또는 `"PWAD"` 4글자 + lump 개수 4바이트 +
디렉터리 오프셋 4바이트, 정수는 모두 리틀 엔디언) 뒤에 실제 lump
데이터들이 있고, 헤더가 가리키는 오프셋에 디렉터리(lump 하나당 16바이트:
offset 4 + size 4 + name 8)가 있다.

생성자:
- WadFile(path: string)
  설명: path의 WAD 파일을 열어 헤더와 디렉터리를 읽고, `lumps`를 채운다.
  헤더의 4글자가 `"IWAD"`/`"PWAD"`가 아니면 오류를 낸다.

멤버:
- lumps: list<Doom.WadLump>

메서드:
- findLump(name: string) -> int
  설명: name과 일치하는(대소문자 무시) lump 중 **가장 나중에 나열된** 것의
  인덱스를 반환한다 — 원본과 같은 규칙으로, 나중 WAD(패치)가 앞선 WAD를
  덮어쓸 수 있게 한다. 없으면 -1.
- readLump(index: int) -> bytes
  설명: 해당 lump의 원시 바이트를 파일에서 읽어 반환한다.

test_required Doom.WadFile {
  - findLump()으로 찾은 인덱스로 readLump()한 결과의 바이트 길이는 그
    lump의 size와 같다.
  - 존재하지 않는 이름으로 findLump()하면 -1을 반환한다.
  - 같은 이름의 lump가 여러 번 나오면, findLump()는 그중 가장 나중(파일
    안에서 더 뒤에 있는) 것을 찾는다.
}

## Class: Doom.Palette

원본의 `PLAYPAL` lump(`i_video.c`의 팔레트 처리)에 대응한다. `PLAYPAL`
lump 하나는 256색 팔레트 14벌(정상 화면, 피격 시 붉은 화면, 방사능 피해
시 녹색 화면 등 상태별 색조 보정용)을 담고 있으며, 각 팔레트는
256 * 3바이트(R, G, B 각 1바이트)다. 이 명세는 그중 0번(기본) 팔레트만
다룬다.

생성자:
- Palette(playpalBytes: bytes)
  설명: playpalBytes의 앞 768바이트(256 * 3)를 기본 팔레트로 읽는다.

메서드:
- colorAt(paletteIndex: int) -> (int, int, int)
  설명: 0~255 팔레트 인덱스에 대응하는 (R, G, B)를 반환한다. 텍스처/스프라이트
  픽셀은 원본에서 RGB가 아니라 이 팔레트 인덱스(0~255, 1바이트)로
  저장되어 있다 — 화면에 그리기 전에 이 메서드로 실제 색을 구해야 한다.

# Interface

## Library

다른 파일은 `WadFile`을 한 번 열어 두고 `findLump`/`readLump`로 맵 데이터,
텍스처, 팔레트 등 필요한 lump를 그때그때 읽습니다.

# Constraints

- 이 명세는 원본 IWAD(`doom.wad`/`doom1.wad`)의 lump 구성을 그대로
  전제한다 — 여러 PWAD를 겹쳐 읽는 병합(모드 로딩) 규칙은 범위 밖이다.

# Examples

## 예제: lump을 찾아서 읽는다

전제: `doom1.wad`에 `"E1M1"`이라는 이름의 lump가 있고 크기는 알려진
값이다.

호출: `wad = WadFile("doom1.wad")`, `idx = wad.findLump("E1M1")`,
`data = wad.readLump(idx)`

기대 동작: `idx`는 -1이 아니고, `data`의 길이는 `wad.lumps[idx].size`와
같다.

# Open Points

- 압축된 lump, PWAD 병합, 그래픽이 아닌 lump(사운드 `DS*`, 음악 `D_*`
  등)의 세부 포맷은 이 파일의 범위 밖이다 — `game.md`의 Open Points 참조.
