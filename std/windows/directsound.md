#!specpp 0.1

# Meta

- name: std/windows/directsound
- version: 0.1.0
- description: 짧은 효과음과 위치 기반(스테레오 패닝) 음향을 재생하는 데 필요한 최소 DirectSound 부분집합에 대한 실체 명세.
- platform: windows -> fallback: std/audio/openal.md
- kind: native

# Intent

[`std/audio/openal.md`](../audio/openal.md)와 같은 목적을 DirectX
위에서 이루기 위한 것이다. 이미 존재하는 API이므로 새로 구현할 대상이
아니다(`kind: native`, 1.2절).

# Domain

## Class: DS.Device

(불투명 핸들 — 실제로는 `IDirectSound8*`다.)

## Class: DS.Buffer

(불투명 핸들 — 실제로는 `IDirectSoundBuffer8*`다. OpenAL과 달리
DirectSound는 "버퍼"가 데이터와 재생 인스턴스를 겸한다 — 같은 소리를
동시에 여러 번 내려면 버퍼를 여러 개(또는 이중 버퍼링을) 만든다.)

## Class: DS

메서드:
[Static]
- Init(hwnd: HWND) -> DS.Device
  설명: hwnd([`std/windows/win32.md`](win32.md) 참조)에 연결된 재생
  장치를 연다(`DirectSoundCreate8` + `SetCooperativeLevel`).
- CreateBuffer(device: DS.Device, pcmSamples: bytes, sampleRate: int, channels: int, is3D: boolean) -> DS.Buffer
  설명: 16비트 PCM 원시 샘플로 재생 가능한 버퍼를 만든다. is3D면 위치에
  따른 패닝을 쓸 수 있는 버퍼(`IDirectSound3DBuffer8`)로 만든다.
- SetBufferPosition(buffer: DS.Buffer, x: float, y: float, z: float) -> void
- SetListenerPosition(device: DS.Device, x: float, y: float, z: float, facingAngle: float) -> void
- Play(buffer: DS.Buffer, loop: boolean) -> void
- Stop(buffer: DS.Buffer) -> void
- IsPlaying(buffer: DS.Buffer) -> boolean

# Interface

## Library

[`std/audio/openal.md`](../audio/openal.md)와 같은 순서로 씁니다 —
`Init` → 효과음마다 `CreateBuffer` → 재생 시점마다
`SetBufferPosition` + `Play`.

# Constraints

- 헤더 `<dsound.h>`. 링크: `dsound.lib`, `dxguid.lib`.
- 스트리밍 재생(음악)은 이 버전의 범위 밖이다.

# Examples

## 예제: 오른쪽에서 나는 소리

호출: `device = DS.Init(hwnd)`, `DS.SetListenerPosition(device, 0, 0, 0, 0)`,
`buf = DS.CreateBuffer(device, pcmData, 11025, 1, true)`,
`DS.SetBufferPosition(buf, 10, 0, 0)`, `DS.Play(buf, false)`

기대 동작: 오른쪽 채널이 왼쪽보다 크게 들린다.

# Open Points

- 도플러 효과, EAX 계열 환경음향 확장은 이 버전의 범위 밖이다.
