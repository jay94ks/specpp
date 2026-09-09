#!specpp 0.1

# Meta

- name: std/audio/openal
- version: 0.1.0
- description: 짧은 효과음과 위치 기반(스테레오 패닝) 음향을 재생하는 데 필요한 최소 OpenAL 부분집합에 대한 실체 명세.
- kind: native

# Intent

효과음을 여러 개 동시에, 소리 나는 위치에 따라 좌우 볼륨이 달라지도록
재생해야 하는 프로그램(대표적으로
[`examples/doom/sound.md`](../../examples/doom/sound.md))을 위한 것이다.
이미 존재하는 API이므로 새로 구현할 대상이 아니다(`kind: native`, 1.2절).
플랫폼과 무관하므로 `platform` 필드를 두지 않는다 —
[`std/windows/directsound.md`](../windows/directsound.md)가 같은 역할의
Windows/DirectX 대응이다.

# Domain

## Class: AL.Buffer

(불투명 핸들이다 — 실제로는 `ALuint` 버퍼 이름이다. 소리 데이터 자체를
담는다.)

## Class: AL.Source

(불투명 핸들이다 — 실제로는 `ALuint` 소스 이름이다. "지금 이 소리를 이
위치에서 재생 중이다"라는 재생 인스턴스다.)

## Class: AL

메서드:
[Static]
- Init() -> void
  설명: 기본 재생 장치를 열고 컨텍스트를 만든다(`alcOpenDevice` +
  `alcCreateContext` + `alcMakeContextCurrent`).
- CreateBuffer(pcmSamples: bytes, sampleRate: int, channels: int) -> AL.Buffer
  설명: 16비트 PCM 원시 샘플로 재생 가능한 버퍼를 만든다
  (`alGenBuffers` + `alBufferData`).
- CreateSource(buffer: AL.Buffer) -> AL.Source
  설명: buffer를 재생할 소스를 만든다(`alGenSources` + `alSourcei`로
  버퍼 연결).
- SetSourcePosition(source: AL.Source, x: float, y: float, z: float) -> void
  설명: 소스의 3D 위치를 정한다 — 리스너(카메라) 위치와의 상대 거리·방향에
  따라 자동으로 볼륨·좌우 패닝이 계산된다.
- SetListenerPosition(x: float, y: float, z: float, facingAngle: float) -> void
  설명: 지금 듣고 있는 사람(카메라)의 위치와 바라보는 방향을 정한다.
- Play(source: AL.Source) -> void
- Stop(source: AL.Source) -> void
- IsPlaying(source: AL.Source) -> boolean

# Interface

## Library

`Init`을 한 번 부른 뒤, 효과음마다 `CreateBuffer`로 한 번씩 업로드해
재사용합니다. 소리를 낼 때마다 `CreateSource`로 재생 인스턴스를 만들고
(또는 미리 만들어 둔 소스를 재사용하고) `SetSourcePosition` + `Play`를
부릅니다. 매 프레임(또는 매 tic) `SetListenerPosition`으로 카메라 위치를
갱신합니다.

# Constraints

- 헤더 `<AL/al.h>`, `<AL/alc.h>`. 링크: 플랫폼별 OpenAL 구현(예:
  OpenAL Soft)의 라이브러리.
- 스트리밍 재생(음악처럼 긴 오디오를 조금씩 버퍼링하는 것)은 이 버전의
  범위 밖이다 — `CreateBuffer`는 전체를 한 번에 담는 짧은 효과음을
  전제한다.

# Examples

## 예제: 왼쪽에서 나는 소리

호출: `AL.SetListenerPosition(0, 0, 0, 0)`,
`source = AL.CreateSource(gunshotBuffer)`,
`AL.SetSourcePosition(source, -10, 0, 0)`, `AL.Play(source)`

기대 동작: 왼쪽 스피커(채널)가 오른쪽보다 크게 들린다.

# Open Points

- 도플러 효과, 반사·잔향(리버브) 같은 환경음향은 이 버전의 범위 밖이다.
