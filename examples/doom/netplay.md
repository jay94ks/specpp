#!specpp 0.1

# Domain

원본 `d_net.h`/`d_net.c`/`i_net.c`(멀티플레이 네트워킹)와 `g_game.c`의
데모 녹화/재생 부분에 대응한다. 핵심 아이디어: DOOM은 **결정론적
락스텝(lockstep)** 시뮬레이션이다 — 매 tic, "이번 tic에 무엇을
할지"(이동/회전/발사/사용 여부)를 아주 작은 `Doom.TicCmd` 하나로
압축하고, 모든 플레이어의 그 tic 명령이 모이면 그제서야 `game.md`의
`Feature.틱 진행`을 실행한다. **같은 입력이면 항상 같은 결과가 나온다는
것**이 전제이므로, 멀티플레이는 "모든 클라이언트에 같은 TicCmd들을
나눠주는 것"으로, 데모는 "TicCmd들을 실시간 대신 파일에서 읽는 것"으로
둘 다 같은 메커니즘 위에서 구현된다.

## Class: Doom.TicCmd

원본 `ticcmd_t`에 대응한다 — 한 플레이어가 한 tic 동안 하려는 행동을
아주 작은 값들로 압축한 것(원본은 이걸 몇 바이트로 눌러 담아 네트워크
대역폭을 아꼈다).

멤버:
- forwardMove: int — 전후 이동량(-127~127로 정규화된 값).
- sideMove: int — 좌우 이동량.
- angleTurn: int — 이번 tic에 시야각을 얼마나 돌릴지.
- buttons: int — 발사/사용 등을 비트로 담은 값.

메서드:
[Static]
- FromInput(rawInput: Doom.RawPlayerInput) -> Doom.TicCmd
  설명: 실제 키보드/마우스 상태를 이 압축된 형태로 바꾼다
  (`G_BuildTiccmd`에 대응).

## Class: Doom.NetGame

원본 `d_net.c`의 핵심 상태에 대응한다.

멤버:
- localPlayerIndex: int
- players: list<Doom.Player>
- pendingTicCmds: map<int, list<Doom.TicCmd?>> — tic 번호 → 그 tic의
  플레이어별 명령(아직 도착하지 않은 원격 플레이어 것은 null).
- isServer: boolean — 원본은 대등 계층(peer-to-peer)이지만, 이 명세는
  단순화를 위해 한 인스턴스가 tic 진행의 기준(권위, authority)을 갖는
  형태를 기본으로 한다(아래 Open Points).

메서드:
- broadcastLocalTicCmd(tic: int, cmd: Doom.TicCmd) -> void
  설명: 이번 tic의 로컬 입력을 다른 모든 참가자에게 보낸다.
- receiveRemoteTicCmd(tic: int, playerIndex: int, cmd: Doom.TicCmd) -> void
  설명: 원격 참가자로부터 받은 명령을 `pendingTicCmds`에 채운다.
- isReadyToAdvance(tic: int) -> boolean
  설명: `pendingTicCmds[tic]`에 모든 `players`의 명령이 다 모였으면
  true.

test_required Doom.NetGame {
  - `isReadyToAdvance(tic)`가 true일 때만 `game.md`의
    `Feature.틱 진행`을 실행한다 — 하나라도 빠진 채로 진행하지 않는다.
}

## Class: Doom.Demo

원본 `g_game.c`의 데모 녹화/재생에 대응한다.

멤버:
- header: (string, int) — (맵 이름, 난이도) 같은 시작 조건.
- recordedTicCmds: list<Doom.TicCmd> — 한 명(싱글 플레이 데모 기준)의,
  tic 순서대로 나열된 명령들.

메서드:
[Static]
- Load(bytes: bytes) -> Doom.Demo
- toBytes() -> bytes

# Behavior

## Feature: 틱 명령 수집(네트워크/로컬 공통)

설명: `game.md`의 `Feature.틱 진행`이 "이번 tic의 입력을 읽는" 단계에서
실제로 하는 일이다 — 입력의 출처가 로컬 키보드든, 네트워크든, 데모
파일이든 결과는 항상 `Doom.TicCmd` 하나다.

절차:
1. **싱글 플레이, 녹화 없음**: 이번 tic의 실제 입력을 `TicCmd.FromInput`으로
   변환해 그대로 쓴다.
2. **데모 녹화 중**: 위와 같이 만들고, 추가로 `Doom.Demo.recordedTicCmds`
   끝에 덧붙인다.
3. **데모 재생 중**: 실제 입력을 무시하고,
   `Doom.Demo.recordedTicCmds[tic]`을 그대로 쓴다. 남은 명령이 없으면
   데모 재생을 끝낸다.
4. **멀티플레이**: 로컬 입력을 `broadcastLocalTicCmd`로 다른 참가자에게
   보내고, `isReadyToAdvance(tic)`가 true가 될 때까지(모든 참가자의
   명령이 도착할 때까지) 그 tic의 `game.md`의 `Feature.틱 진행` 실행을
   미룬다 — 이 대기 때문에 멀티플레이 게임 속도는 가장 느린(지연이 큰)
   참가자에 맞춰진다.

# Interface

## Library

`game.md`의 `Doom.Game`은 매 tic `Feature.틱 명령 수집`으로 얻은
`Doom.TicCmd`(들)를 `Feature.이동과 충돌`/`Feature.발사 입력 처리`/
`Feature.사용 키 처리`에 그대로 입력값으로 넘깁니다.

# Constraints

- 네트워크 전송 자체는 [`std/net/udp.md`](../../std/net/udp.md)로
  구현한다 — 지연에 민감한 소규모 데이터(TicCmd 몇 바이트)를 자주
  주고받는 데는 TCP보다 UDP가 적합하다. 유실된 TicCmd를 어떻게
  복구하는지(재전송, 이전 명령 재사용 등)는 이 파일이 규정하지 않는다
  (아래 Open Points).
- **`platform: web`에서는 원시 UDP 소켓 자체가 브라우저 샌드박스에
  없다**(SPEC.md 3.10절) — [`std/net/udp.md`](../../std/net/udp.md)를
  그대로 쓸 수 없다. 가장 가까운 대안은 WebRTC의
  `RTCDataChannel`을(순서 보장 없음·재전송 없음으로 설정하면 UDP와
  비슷하게 동작한다) 쓰는 것이지만, 연결 수립 과정(시그널링 서버로
  SDP/ICE 후보를 교환하는 것)이 UDP 소켓을 여는 것과는 전혀 다른
  모양이라 이 저장소는 아직 `std/web/`에 그 바인딩을 두지 않았다(아래
  Open Points).
- 이 락스텝 방식이 실제로 결정론적이려면 `game.md`의 시뮬레이션(이동,
  충돌, 전투, 난수 사용 등)이 **모든 참가자의 기기에서 완전히 같은
  결과**를 내야 한다 — 그래서 [`game.md`](game.md#Behavior.Feature:_틱_진행)의
  `Feature.틱 진행`에 `[Deterministic]`(SPEC.md 3.2절)이 붙어 있다.
  `map.md`/`game.md`의 Constraints에서 이미 언급했듯, 부동소수점 대신
  16.16 고정소수점(`fixed_t`) 연산을 쓰는
  것을 강하게 권장하는 이유가 바로 이것이다(타겟 언어·CPU마다 부동소수점
  반올림이 미묘하게 달라지면 몇 분 안에 참가자들의 게임 상태가
  어긋난다). 난수도 원본처럼 미리 정해진 표(`m_random.c`의
  256개짜리 고정 테이블)에서 순서대로 뽑는 방식이면 모든 참가자가 항상
  같은 "무작위" 값을 얻는다.

# Examples

## 예제: 데모는 정확히 재현된다

전제: 같은 맵에서 녹화된 `Doom.Demo`가 있다.

호출: 그 데모로 `Feature.틱 명령 수집`(재생 모드)을 데모의 tic 수만큼
반복해 `game.md`의 `Feature.틱 진행`을 그만큼 실행한다.

기대 동작: 최종 플레이어 위치·점수·맵 상태가, 원래 녹화할 때 그 입력으로
플레이했을 때의 결과와 정확히 같다(시뮬레이션이 결정론적이라는 전제
하에).

## 예제: 멀티플레이는 모두 도착해야 진행한다

전제: 2인 게임에서 tic 100에 대해 player 0의 명령은 도착했지만 player 1의
명령은 아직 도착하지 않았다.

호출: `netGame.isReadyToAdvance(100)`

기대 동작: `false`를 반환한다 — 이 tic은 아직 진행되지 않는다.

# Open Points

- 참가자 발견(로비, IP 직접 입력 등), 연결 끊김 처리, 늦게 참가하기는
  다루지 않는다.
- 패킷 유실 시 재전송/보정(원본은 최근 몇 tic의 명령을 함께 반복
  전송해 유실에 대비한다)은 이 버전에서 규정하지 않는다.
- 이 명세의 `isServer` 권위자 모델은 원본의 순수 대등 계층 방식을
  단순화한 것이다 — 진짜 대등 계층으로 구현하고 싶다면
  `Doom.NetGame`을 참가자 수만큼 대칭적으로 두는 형태로 바꾼다.
- 웹 타겟을 위한 `RTCDataChannel` 기반 `std/web/` 바인딩(과 그 앞에
  필요한 시그널링 서버 프로토콜)은 아직 이 저장소에 없다 — 지금은
  위 Constraints에 대안만 적어 뒀다.
