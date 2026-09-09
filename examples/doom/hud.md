#!specpp 0.1

# Domain

원본 `st_stuff.h`/`st_stuff.c`(상태 표시줄, status bar)에 대응한다. 화면
아래에 항상 떠 있는 UI — 체력, 탄약, 무기 아이콘, 열쇠, 얼굴 표정, 갑옷을
보여준다.

## Class: Doom.Hud

멤버:
- faceFrame: string — 지금 보여줄 플레이어 얼굴 이미지 이름. 체력이 낮을
  수록, 최근에 맞았을수록, 남을 죽였을수록 다른 표정을 보여준다(아래
  Behavior 참조).

메서드:
- render(player: Doom.Player, renderer: Doom.Renderer.Backend) -> void
  설명: 화면 아래 띠 영역에 체력/탄약/장비 아이콘과 숫자를 그린다.
  아이콘·막대·얼굴처럼 텍스처 없이 색만으로 그리는 부분은
  [`Doom.Renderer.Backend.drawUIShapes`](render.md)로, 체력·탄약 같은
  숫자는 글꼴 래스터라이즈가 필요하므로
  [`Doom.Renderer.Backend.drawUIText`](render.md)로 그린다 — 둘 다 매
  프레임 값이 바뀌므로(레벨 지오메트리처럼 한 번 올려두고 재사용하는
  대상이 아니다) 그때그때 다시 만든다.

# Behavior

## Feature: 얼굴 표정 갱신

설명: 매 tic, 플레이어 상태에 따라 `faceFrame`을 고른다.

절차:
1. 체력 비율(`player.actor.health` / 최대 체력)에 따라 기본 표정 등급을
   고른다(예: 100%~80% 웃는 얼굴, 그 아래로 갈수록 더 다친 표정, 0%
   근처는 고통스러운 표정).
2. 최근 한 tic 안에 피해를 입었으면, 피해를 준 방향(정면/좌/우)을 보고
   그쪽을 노려보는 변형 표정을 잠깐 대신 보여준다.
3. 최근에 적을 죽였으면 잠깐 웃는(신난) 표정을, 스스로 매우 위험한
   상황(체력이 아주 낮음)이면 겁먹은 표정을 우선한다.

# Constraints

- 얼굴 표정 등급(정확히 몇 종류, 어떤 확률로 곁눈질하는지 등 원본의
  자잘한 랜덤 변형)은 단순화했다.

# Examples

## 예제: 체력이 0에 가까우면 고통스러운 얼굴

전제: `player.actor.health`가 10(최대 100 중)이다.

호출: `Feature.얼굴 표정 갱신`

기대 동작: `faceFrame`이 "많이 다친" 등급의 표정으로 바뀐다.

# Open Points

- 열쇠 카드 3종의 정확한 아이콘 배치, 숫자 폰트의 자릿수 처리(100 초과
  탄약 등)는 다루지 않는다.
