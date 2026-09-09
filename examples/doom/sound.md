#!specpp 0.1

# Domain

원본 `s_sound.h`/`s_sound.c`(사운드 재생 로직)와 `i_sound.c`(저수준
재생)에 대응한다. 효과음은 WAD의 `DS`로 시작하는 lump(예:
`"DSPISTOL"`), 음악은 `D_`로 시작하는 lump(예: `"D_E1M1"`)에 들어있다.

## Class: Doom.SoundEffect

원본의 DMX 사운드 포맷에 대응한다: lump 맨 앞 2바이트는 포맷 번호(항상
3), 다음 2바이트는 샘플레이트(보통 11025Hz), 다음 4바이트는 샘플 개수,
그 뒤로 그만큼의 8비트 무부호(unsigned) PCM 샘플이 이어진다.

멤버:
- name: string
- sampleRate: int
- pcmSamples: bytes — 8비트 무부호 PCM.

생성자:
[Static]
- Load(wad: Doom.WadFile, lumpName: string) -> Doom.SoundEffect
  설명: [`Doom.WadFile.readLump`](wad.md)로 원시 바이트를 읽어 위 헤더
  포맷대로 파싱한다.

## Class: Doom.MusicTrack

원본의 MUS 포맷(자체 MIDI 비슷한 포맷, `D_*` lump)에 대응한다. 이 명세는
바이트 단위 포맷을 규정하지 않고 재생 단위로만 다룬다(아래 Open Points).

멤버:
- name: string
- lumpName: string

## Class: Doom.SoundSystem

멤버:
- effectCache: map<string, Doom.SoundEffect> — 한 번 읽은 효과음을
  재사용하기 위한 캐시.

메서드:
- init() -> void
- playEffect(effectName: string, source: Doom.Actor?, listener: Doom.Player) -> void
  설명: `Behavior.효과음 재생`을 실행한다.
- playMusic(track: Doom.MusicTrack) -> void
- stopMusic() -> void
- updateListenerPosition(listener: Doom.Player) -> void
  설명: 매 tic 호출되어, 위치 기반 재생 중인 효과음들의 좌우 밸런스·
  볼륨이 리스너(플레이어) 기준으로 갱신되게 한다.

# Behavior

## Feature: 효과음 재생

입력:
- effectName: string
- source: Doom.Actor? — 소리가 나는 위치. null이면 방향 없이(예: 메뉴
  클릭음, 화면 전체에 울리는 소리) 재생한다.
- listener: Doom.Player

절차:
1. `effectCache`에 `effectName`이 없으면 `Doom.SoundEffect.Load`로 읽어
   캐시에 넣는다.
2. 이미 재생 한도(원본 기본 8채널 동시 재생)를 넘겼으면, 가장 우선순위가
   낮은(예: 가장 멀리서 나는) 재생 중인 소리를 하나 멈추고 자리를
   비운다.
3. `source`가 있으면 `source.x, source.y`를 재생 위치로 준다(z는 생략해도
   된다 — DOOM은 수평 방향 패닝만 쓴다). 없으면 리스너와 같은 위치로
   재생해 방향성이 없게 한다.
4. 재생을 시작한다.

# Interface

## Library

`ai.md`/`game.md`/`specials.md`의 각 절차 중 "소리를 낸다"고 서술된
지점마다 `Feature.효과음 재생`을 호출합니다.

# Constraints

- Windows에서는 [`std/windows/directsound.md`](../../std/windows/directsound.md)로,
  다른 플랫폼에서는 [`std/audio/openal.md`](../../std/audio/openal.md)로
  구현한다 — 둘 다 "버퍼 만들기 → 위치 정하기 → 재생"이라는 같은 모양이라
  `Doom.SoundSystem` 자체는 어느 쪽을 쓰든 바뀌지 않는다.
- `updateListenerPosition`은 [`game.md`](game.md)의 `Feature.틱 진행`에서
  매 tic 호출된다.

# Examples

## 예제: 총소리는 쏜 위치에서 난다

호출: `soundSystem.playEffect("DSPISTOL", zombieman, player)`

기대 동작: `zombieman`이 플레이어 왼쪽에 있으면 왼쪽 채널이 더 크게
들린다.

# Open Points

- MUS→MIDI 변환의 정확한 바이트 포맷은 다루지 않는다 — `MusicTrack`은
  "이 lump을 재생한다"는 수준까지만 정의한다. 실제 재생은 대상 플랫폼의
  MIDI 신시사이저(Windows는 `winmm`/`XAudio2`, 그 외는 시스템 MIDI
  라이브러리 등)에 맡긴다.
- 동시 재생 채널 수 제한, 소리 우선순위 규칙의 정확한 값은 원본
  `S_MAX_CHANNELS`를 참고해 채운다.
