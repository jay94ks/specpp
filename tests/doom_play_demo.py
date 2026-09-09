"""examples/doom/ 스펙을 검증한 실제 tests/doom_game.py Game 클래스를 그대로 돌려
한 판을 텍스트로 재생하는 데모.

실제 doom.wad 자산과 render.md의 화면 렌더링은 구현되어 있지 않으므로(그래픽 창은
띄우지 않는다), tests/doom_test_fixtures.py의 손으로 만든 2방짜리 맵으로
플레이어가 문을 지나 Zombieman과 교전하고 맵을 나가는 과정을 이동/충돌/AI/전투/
문 특수 효과/맵 종료까지 실제 시뮬레이션 코드로 그대로 실행해 보여준다.
"""
import random
import tempfile

from doom_game import Game, deal_damage, fire_weapon_input, move_and_collide, use_key
from doom_specials import Door
from doom_test_fixtures import MAP_NAME, build_two_room_map_wad
from doom_wad import WadFile


def log(tic, msg):
    print(f"[tic {tic:4d}] {msg}")


def main():
    f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
    f.write(build_two_room_map_wad())
    f.close()
    wad = WadFile(f.name)

    rng = random.Random(42).random
    game = Game.Start(wad, MAP_NAME, rng=rng)

    player = game.player.actor
    zombie = game.monsters()[0]
    door_line = game.map.lineDefs[1]  # 두 방 사이 문.
    door_line.special = 1

    print("=== DOOM 시뮬레이션 재생 시작 ===")
    print(f"플레이어 시작 위치: ({player.x:.0f}, {player.y:.0f}), 체력 {game.player.health}")
    print(f"Zombieman 위치: ({zombie.x:.0f}, {zombie.y:.0f}), 체력 {zombie.health}")
    print()

    # 1. 플레이어가 문 앞까지 걸어간다.
    # (맵이 아주 작아서(2방 x 64x64) 시작 위치부터 이미 Zombieman과의 충돌 판정
    #  반경이 겹친다 — 순수 이동 구간에서는 잠시 몬스터를 충돌 목록에서 뺀다.)
    all_actors = game.actors
    game.actors = [game.player.actor]
    for _ in range(7):
        move_and_collide(game, player, 2.0, 0.0)
        game.tic += 1
    game.actors = all_actors
    log(game.tic, f"문 앞 도착: 플레이어 ({player.x:.0f}, {player.y:.0f}), 섹터={player.sector.floorTexture}")

    # 2. 문을 연다 (Feature.사용 키 처리와 같은 방식).
    def make_mover(line):
        return Door(line.backSide.sector, "Open", targetCeilingHeight=96, speed=32)

    player.angle = 0.0
    mover = use_key(game, make_mover=make_mover)
    log(game.tic, f"문 사용: special={door_line.special} (0이면 이미 발동됨), 진행 중 특수 효과 {len(game.specials)}개")
    while game.specials:
        game.specials = [m for m in game.specials if m.tick()]
        game.tic += 1
    log(game.tic, f"문이 완전히 열렸다 (천장 높이={mover.sector.ceilingHeight:.0f})")

    # 3. 동쪽 방으로 들어가 Zombieman을 발견한다.
    from doom_ai import look_for_players
    game.actors = [game.player.actor]
    for _ in range(6):
        move_and_collide(game, player, 2.0, 0.0)
        game.tic += 1
    game.actors = all_actors
    found = look_for_players(zombie, [game.player], game.map.lineDefs)
    log(game.tic, f"Zombieman이 플레이어를 발견함: {found} (state={zombie.state.sprite}/{zombie.state.frame})")

    # 4. 총격전.
    player.angle = 180.0  # Zombieman을 마주본다 (동쪽 방에서 서쪽을 보고 있으므로 zombie는 뒤에 있다).
    import math
    dx, dy = zombie.x - player.x, zombie.y - player.y
    player.angle = math.degrees(math.atan2(dy, dx))
    game.player.ammo["bullets"] = 50

    round_no = 0
    while zombie.health > 0 and game.player.health > 0 and round_no < 30:
        round_no += 1
        fired = fire_weapon_input(game)
        game.tic += 1
        if fired:
            log(game.tic, f"발사! Zombieman 체력: {zombie.health}, 남은 총알: {game.player.ammo['bullets']}")
        if zombie.health > 0 and zombie.target is player:
            # Zombieman도 반격한다 (원거리 즉발 명중).
            from doom_ai import hitscan_attack
            hitscan_attack(zombie, lambda r: (r() % 3 + 1) * 5, game.rngByte,
                            lambda t, d, i: deal_damage(game, t, d, i), game.map.lineDefs)
            game.tic += 1

    if zombie.health <= 0:
        log(game.tic, f"Zombieman 처치! killCount={game.killCount}, 플레이어 체력={game.player.health}")
    else:
        log(game.tic, f"플레이어 체력 {game.player.health} (교전 계속 중)")

    # 5. 맵 출구로 이동해 종료 조건을 확인한다.
    exit_line = game.map.lineDefs[6]
    exit_line.special = 11  # EXIT_SPECIAL
    from doom_game import check_map_exit
    ended = check_map_exit(game, exit_line)
    log(game.tic, f"출구 선을 밟음: 맵 종료={ended} (game.exited={game.exited})")

    print()
    print("=== 요약 ===")
    print(f"총 진행 tic: {game.tic} ({game.tic / 35:.1f}초 분량)")
    print(f"처치 수: {game.killCount} / 전체 몬스터 {game.totalKills}")
    print(f"플레이어 최종 상태: 체력={game.player.health}, 남은 총알={game.player.ammo['bullets']}")
    print(f"플레이어 최종 위치: ({player.x:.1f}, {player.y:.1f})")


if __name__ == "__main__":
    main()
