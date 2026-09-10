#!specpp 0.1

# Meta

- name: std/web/webaudio
- version: 0.1.0
- description: 짧은 효과음과 위치 기반 음향을 재생하는 데 필요한 최소 Web Audio API 부분집합에 대한 실체 명세.
- platform: web
- kind: native

# Intent

[`std/audio/openal.md`](../audio/openal.md)/
[`std/windows/directsound.md`](../windows/directsound.md)와 같은
목적(효과음을 소리 나는 위치에 따라 좌우가 달라지도록 재생)을
브라우저에서 이루기 위한 것이다. Web Audio API의 `PannerNode`가
OpenAL/DirectSound의 3D 위치 기반 재생과 같은 역할을 한다. 이미
존재하는 API이므로 새로 구현할 대상이 아니다(`kind: native`, 1.2절).

# Domain

## Class: AudioContext

(불투명 핸들이다 — 실제로는 브라우저의 `AudioContext`를 가리킨다.)

## Class: AudioBuffer

(불투명 핸들이다 — 실제로는 디코딩된 PCM 데이터를 담은
`AudioBuffer`를 가리킨다.)

## Class: WebAudio

메서드:
[Static]
- Init() -> AudioContext
  설명: `new AudioContext()`에 대응한다. 브라우저는 사용자 제스처(클릭
  등) 없이 오디오 재생을 막는 경우가 많다 — 아래 Constraints 참조.
- CreateBuffer(ctx: AudioContext, pcmSamples: bytes, sampleRate: int, channels: int) -> AudioBuffer
  설명: 원시 PCM으로 재생 가능한 버퍼를 만든다(`ctx.createBuffer` +
  채널 데이터 채우기, 또는 이미 인코딩된 파일이면
  `ctx.decodeAudioData`).
- PlayAtPosition(ctx: AudioContext, buffer: AudioBuffer, x: float, y: float, z: float) -> void
  설명: `ctx.createBufferSource()` + `ctx.createPanner()`를 만들어
  `panner.positionX/Y/Z`를 설정하고, `source -> panner ->
  ctx.destination` 순으로 연결한 뒤 `source.start()`한다 —
  [`std/audio/openal.md`](../audio/openal.md)의
  `CreateSource`+`SetSourcePosition`+`Play`를 한 번에 근사한 것이다
  (Web Audio는 재생 인스턴스가 1회용이라 소스 노드를 재사용하지 않는다
  — 아래 Constraints 참조).
- PlayGlobal(ctx: AudioContext, buffer: AudioBuffer) -> void
  설명: 패닝 없이(메뉴 클릭음처럼 방향이 없는 소리) 그대로 재생한다.
- SetListenerPosition(ctx: AudioContext, x: float, y: float, z: float, facingAngleDeg: float) -> void
  설명: `ctx.listener.positionX/Y/Z`와 `forwardX/Y/Z`를 설정한다.

# Interface

## Library

`Init`으로 컨텍스트를 하나 만들어 두고, 효과음마다 `CreateBuffer`로 한
번씩 디코딩해 재사용합니다. 소리를 낼 때마다 `PlayAtPosition`(또는
`PlayGlobal`)을 부릅니다. 매 프레임(또는 매 tic)
`SetListenerPosition`으로 카메라 위치를 갱신합니다.

# Constraints

- 헤더/링크가 필요 없다 — 브라우저가 이미 제공하는 전역 `AudioContext`
  API다.
- 대부분의 브라우저는 사용자가 페이지와 한 번이라도 상호작용(클릭,
  키 입력 등)하기 전에는 오디오 재생을 막는다 — `Init`은 그 상호작용
  이후에 호출하거나, 미리 만들어 둔 컨텍스트를 그 시점에 `resume()`해야
  한다. 이 계약은 그 타이밍을 규정하지 않는다.
- `AudioBufferSourceNode`는 한 번 `start()`하면 다시 쓸 수 없다(1회용) —
  [`std/audio/openal.md`](../audio/openal.md)의 `AL.Source`처럼 만들어
  두고 재사용하는 모델과 다르다. 같은 소리를 다시 재생하려면 매번 새
  소스 노드를 만든다(`AudioBuffer` 자체는 재사용한다).
- 동시 재생 채널 수 제한은 브라우저가 알아서 관리한다 — OpenAL의
  8채널 같은 명시적 한도는 이 계약에 없다.

# Examples

## 예제: 왼쪽에서 나는 소리

호출: `ctx = WebAudio.Init()`,
`WebAudio.SetListenerPosition(ctx, 0, 0, 0, 0)`,
`WebAudio.PlayAtPosition(ctx, gunshotBuffer, -10, 0, 0)`

기대 동작: 왼쪽 채널이 오른쪽보다 크게 들린다
([`std/audio/openal.md`](../audio/openal.md)의 같은 예제와 동일한
결과).

# Open Points

- 도플러 효과, 반사·잔향(리버브)은 이 버전의 범위 밖이다.
- 오디오 자동재생 정책이 브라우저·버전마다 조금씩 달라, 정확한 재생
  허용 조건은 규정하지 않는다.
