#!specpp 0.1

# Meta

- name: std/io/compression
- version: 0.1.0
- description: gzip 압축·해제와 ZIP 아카이브 읽기/쓰기에 대한 추상 계약.

# Intent

로그 파일을 압축해 저장하거나, HTTP 응답을 gzip으로 내려주거나
([`std/net/httpserver.md`](../net/httpserver.md)의 Open Points가 미뤄둔
부분), 여러 파일을 하나로 묶어 배포할 때 쓴다.

# Domain

## Class: Gzip

[Static]
- compress(data: bytes) -> bytes
- decompress(data: bytes) -> bytes
- compressStream(source: Stream, destination: Stream) -> void
  설명: [`std/io/stream.md`](stream.md)를 통해 전체를 메모리에 올리지
  않고 압축한다 — 큰 파일에 쓴다.
- decompressStream(source: Stream, destination: Stream) -> void

## Class: ZipArchive.Entry

멤버:
- name: string
- size: int — 압축 해제 후 크기.
- compressedSize: int

## Class: ZipArchive

[Static]
- open(path: string) -> ZipArchive
  설명: 기존 zip 파일을 읽기 모드로 연다.
- create(path: string) -> ZipArchive
  설명: 새 zip 파일을 쓰기 모드로 만든다.

메서드:
- entries() -> list<ZipArchive.Entry>
- readEntry(name: string) -> bytes
  설명: `name`이 없으면 오류를 낸다.
- writeEntry(name: string, content: bytes) -> void
- close() -> void
  설명: 쓰기 모드였다면 이 호출로 실제 디스크에 반영된다.

# Interface

## Library

단일 파일은 `Gzip.compress(data)`/`Gzip.decompress(data)`로 다룹니다.
여러 파일을 묶어야 하면
`zip = ZipArchive.create("out.zip"); zip.writeEntry("a.txt", data);
zip.close();`처럼 씁니다.

# Constraints

- 대상 언어의 표준 압축 라이브러리(Python `gzip`/`zipfile`, Java
  `java.util.zip`, C# `System.IO.Compression`, Node.js `zlib`, C++
  zlib/miniz 등)에 매핑한다.
- Gzip은 DEFLATE 기반 **단일 스트림** 압축이고, `ZipArchive`는 여러
  파일(과 이름)을 함께 담는 **컨테이너 포맷**이라는 차이가 있다 —
  여러 파일을 압축해야 한다고 Gzip을 반복 호출하지 않는다.
- `ZipArchive.open`이 존재하지 않는 파일이나 손상된 zip을 가리키면
  오류를 낸다.

# Examples

## 예제: gzip 왕복

호출 (순서대로): `c = Gzip.compress(data)`, `Gzip.decompress(c)`

기대 동작: 두 번째 호출은 원본 `data`와 동일한 바이트를 반환한다.

## 예제: zip 쓰고 읽기

호출 (순서대로):
```
zip = ZipArchive.create("out.zip")
zip.writeEntry("a.txt", "hello")
zip.close()
zip2 = ZipArchive.open("out.zip")
zip2.readEntry("a.txt")
```

기대 동작: 마지막 호출은 `"hello"`에 해당하는 바이트를 반환한다.

# Open Points

- 압축 레벨 지정, 암호화된 zip, tar/7z 등 다른 아카이브 포맷은 이
  버전의 범위 밖이다.
