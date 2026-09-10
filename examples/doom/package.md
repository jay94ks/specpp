#!specpp 0.1

# Meta

- name: doom
- version: 0.1.0
- description: id Software DOOM(1993)을 원본 C 소스(id-software/DOOM,
  linuxdoom-1.10)의 자료구조·알고리즘·게임 콘텐츠(몬스터·무기 수치 등)에
  최대한 가깝게 옮긴 명세. "엔진 프레임워크"가 아니라 **그 게임 자체**를
  목표로 한다.
- target: 미지정 — AI가 상황에 맞게 제안. 셰이더·버텍스 버퍼 기반의
  현대적 OpenGL(3.3+)/Direct3D(11)/WebGL2 렌더링을 전제한다 (아래
  Intent, `render.md` 참조). 웹을 타겟으로 고를 경우 멀티플레이
  네트워킹은 UDP를 그대로 쓸 수 없다는 제약이 있다(`netplay.md`의
  Constraints 참조).

# Intent

[id-software/DOOM](https://github.com/id-software/DOOM) 저장소의
`linuxdoom-1.10` 소스에 있는 실제 DOOM을 SPP로 옮긴 것이다: WAD 파일에서
맵·텍스처·팔레트를 읽고, BSP 트리로 가시성을 판정해 벽·바닥·천장·
스프라이트를 그리고, 플레이어가 이동·충돌·전투하며, 몬스터가 상태
기계(state machine)로 움직이는 고전 FPS를 재현한다. 이 명세는 "이런
프로그램을 만드는 방법"을 보여주는 예시 엔진이 아니라, 원본 `info.c`의
실제 수치(몬스터 18종·무기 8종의 체력·속도·피해량 등, `actors.md`/
`weapons.md` 참조)까지 담아 **다시 만들면 그대로 DOOM이 되는 것**을
목표로 한다.

**자산과 코드의 경계.** 맵의 실제 벽 배치(`E1M1` 등), 텍스처·스프라이트
그래픽, 효과음·음악 원본 데이터는 이 명세가 "코드로 재현"하는 대상이
아니다 — 원본 IWAD(`doom.wad`)에 이미 들어있는 **자산**이며, 이 명세는
그 자산을 원본과 똑같은 형식으로 정확히 읽어들이는 방법
([`wad.md`](wad.md)/[`map.md`](map.md)의 정확한 바이트 포맷)을 규정한다.
즉 IWAD 파일 없이는 실제로 플레이할 콘텐츠(구체적인 맵, 그림, 소리)가
없다는 뜻이다 — 반대로 진짜 `doom.wad`를 함께 두면, 이 명세대로
트랜스파일한 프로그램은 원본과 같은 맵·그래픽·소리로 정확히 같은
게임을 재현해야 한다.

**번들 자산.** [`assets/doom1.wad`](assets/doom1.wad)는 id Software가
직접 무료 재배포를 허용한 셰어웨어 에피소드(E1 "Knee-Deep in the Dead",
버전 1.1, [Internet Archive](https://archive.org/details/DoomsharewareEpisode)
배포본)다. 상용 3-에피소드 IWAD가 아니라 셰어웨어판이라 `E1M1`~`E1M9`만
들어있다 — 이 명세를 검증·시연할 때는 이 파일을 그대로 쓰면 된다.

원본은 CPU가 화면 픽셀을 직접 계산하는 소프트웨어 렌더러다. 이 명세는 그
계산 "결과"(어떤 벽이 화면 어디에 얼마나 크게, 어떤 조명으로 보이는지)는
원본과 똑같이 재현하되, 계산 "방식"은 현대적인 GPU 파이프라인을 쓴다 —
맵을 불러올 때 벽·바닥·천장 지오메트리를 한 번 GPU에 올려두고, 매
프레임에는 카메라 유니폼만 갱신해 깊이 버퍼로 앞뒤를 가리는 몇 번의
드로우 콜로 그린다(원본처럼 CPU가 화면 열마다 그려졌는지 추적할 필요가
없다 — `render.md` 참조). 최종 출력 단계는
[`std/graphics/opengl3.md`](../../std/graphics/opengl3.md),
[`std/windows/direct3d11.md`](../../std/windows/direct3d11.md), 또는
[`std/web/webgl.md`](../../std/web/webgl.md)의 셰이더·버텍스 버퍼 기반
렌더링에 맡긴다 — 그래서 OpenGL·DirectX·웹 브라우저 셋 다 위에서 그대로
돌아간다. 구현이 짧은 걸 우선한다면 레거시 즉시 모드
([`std/graphics/opengl.md`](../../std/graphics/opengl.md)/
[`std/windows/direct3d.md`](../../std/windows/direct3d.md))도 여전히
유효한 선택이다(`render.md`의 Constraints 참조).

**범위.** 원본 엔진의 게임플레이 시스템 전체 — WAD 로딩, 맵/BSP
지오메트리, 렌더링 파이프라인, 액터 상태 기계와 몬스터 AI, 무기, 문/
바닥/천장/플랫폼/조명 같은 특수 효과, 플레이어 이동·충돌·전투, 효과음·
음악, 락스텝 멀티플레이 네트워킹과 데모 녹화/재생, HUD, 자동 지도, 메뉴,
인터미션·피날레, 저장/불러오기 — 를 원본 자료구조와 알고리즘에 충실하게
옮겼다. 1993년 DOS/리눅스 시절의 저수준 시스템 계층(메모리 zone 할당자,
직접 하드웨어 접근 등)만은 의도적으로 옮기지 않았다 — 대상 언어·플랫폼의
기본 메모리 관리와 이 저장소의 다른 `std/` 패키지가 그 역할을 대신한다.
정확한 경계와 이유는 `game.md`의 Open Points에 정리되어 있다.

# Files

- wad.md
- map.md
- actors.md
- ai.md
- weapons.md
- specials.md
- render.md
- sound.md
- netplay.md
- hud.md
- automap.md
- menu.md
- intermission.md
- savegame.md
- game.md
