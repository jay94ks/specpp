// examples/doom/specials.md 검증 (C++17).
#include "doom_specials.hpp"
#include "minitest.hpp"
#include <vector>

using namespace Doom;
using namespace Doom::Map;

TEST(door_open_reaches_target_and_reports_finished) {
    Sector sector{0, 0, "F", "C", 160, 0, 0};
    Door door(&sector, "Open", 128, 8);
    bool stillGoing = true;
    for (int i = 0; i < 1000 && stillGoing; i++) stillGoing = door.tick();
    CHECK_EQ(sector.ceilingHeight, 128.0f);
    CHECK(!stillGoing);
}

TEST(door_open_then_close_reopens_if_blocked) {
    Sector sector{0, 0, "F", "C", 160, 0, 0};
    Door door(&sector, "OpenThenClose", 128, 64);
    door.waitTicsRemaining = 2;
    for (int i = 0; i < 3; i++) door.tick();
    CHECK_EQ(sector.ceilingHeight, 128.0f);
}

TEST(floor_rises_to_target) {
    Sector sector{0, 64, "F", "C", 160, 0, 0};
    FloorMover mover(&sector, 32, 8);
    while (mover.tick()) {}
    CHECK_EQ(sector.floorHeight, 32.0f);
}

TEST(ceiling_crusher_repeats_forever) {
    Sector sector{0, 128, "F", "C", 160, 0, 0};
    Ceiling crusher(&sector, 128, 32, 32, "Down", true, true);
    bool sawBottom = false;
    for (int i = 0; i < 20; i++) {
        crusher.tick();
        if (sector.ceilingHeight == 32.0f) sawBottom = true;
    }
    CHECK(sawBottom);
    CHECK(crusher.tick());  // 크러셔는 절대 끝나지 않는다.
}

TEST(platform_lift_descends_then_stops) {
    Sector sector{64, 128, "F", "C", 160, 0, 0};
    Platform lift(&sector, 0, 64, 16, "Down");
    while (lift.tick()) {}
    CHECK_EQ(sector.floorHeight, 0.0f);
}

TEST(light_flash_low_roll_picks_max) {
    Sector sector{0, 0, "F", "C", 160, 0, 0};
    LightFlash flash(&sector, 200, 80, [] { return 0.0; }, 1);
    flash.tick();
    CHECK_EQ(sector.lightLevel, 200);
}

TEST(light_flash_high_roll_picks_min) {
    Sector sector{0, 0, "F", "C", 160, 0, 0};
    LightFlash flash(&sector, 200, 80, [] { return 0.9; }, 1);
    flash.tick();
    CHECK_EQ(sector.lightLevel, 80);
}

struct FakePlayer {
    std::vector<std::string> keys;
};

static LineDef makeDoorLineDef(Sector& front, Sector& back, Vertex& v1, Vertex& v2, SideDef& fSide,
                                SideDef& bSide) {
    fSide.sector = &front;
    bSide.sector = &back;
    return LineDef{&v1, &v2, 0, 1, 1, &fSide, &bSide};
}

TEST(locked_door_does_not_open_without_matching_key) {
    Vertex v1{0, 0}, v2{0, 64};
    Sector front{0, 0, "F", "C", 160, 0, 1}, back{0, 0, "F", "C", 160, 0, 0};
    SideDef fSide{0, 0, "-", "-", "-", nullptr}, bSide{0, 0, "-", "-", "-", nullptr};
    LineDef line = makeDoorLineDef(front, back, v1, v2, fSide, bSide);

    std::vector<std::shared_ptr<SectorMover>> active;
    FakePlayer player;  // 키 없음.

    auto makeMover = [&](LineDef*) {
        return std::make_shared<Door>(&back, "Open", 128.0f, 4.0f, std::optional<std::string>("blue"));
    };
    auto isLockedCheck = [&](LineDef*) {
        return std::make_shared<Door>(&back, "Open", 128.0f, 4.0f, std::optional<std::string>("blue"));
    };

    auto mover = triggerLineSpecial(&line, "Use", &player, active, makeMover, isLockedCheck);
    CHECK(mover == nullptr);
    CHECK(active.empty());
    CHECK(line.special != 0);
}

TEST(locked_door_opens_with_matching_key) {
    Vertex v1{0, 0}, v2{0, 64};
    Sector front{0, 0, "F", "C", 160, 0, 1}, back{0, 0, "F", "C", 160, 0, 0};
    SideDef fSide{0, 0, "-", "-", "-", nullptr}, bSide{0, 0, "-", "-", "-", nullptr};
    LineDef line = makeDoorLineDef(front, back, v1, v2, fSide, bSide);

    std::vector<std::shared_ptr<SectorMover>> active;
    FakePlayer player;
    player.keys.push_back("blue");

    auto makeMover = [&](LineDef*) {
        return std::make_shared<Door>(&back, "Open", 128.0f, 4.0f, std::optional<std::string>("blue"));
    };
    auto isLockedCheck = [&](LineDef*) {
        return std::make_shared<Door>(&back, "Open", 128.0f, 4.0f, std::optional<std::string>("blue"));
    };

    auto mover = triggerLineSpecial(&line, "Use", &player, active, makeMover, isLockedCheck);
    CHECK(mover != nullptr);
    CHECK_EQ(active.size(), 1u);
}

TEST(advance_specials_removes_finished_keeps_active) {
    Sector sectorA{0, 0, "F", "C", 160, 0, 0}, sectorB{0, 0, "F", "C", 160, 0, 0};
    auto finishedSoon = std::make_shared<FloorMover>(&sectorA, 1.0f, 1.0f);
    auto longRunning = std::make_shared<FloorMover>(&sectorB, 100.0f, 1.0f);
    std::vector<std::shared_ptr<SectorMover>> active = {finishedSoon, longRunning};
    active = advanceSpecials(active);
    CHECK(std::find(active.begin(), active.end(), longRunning) != active.end());
    CHECK(std::find(active.begin(), active.end(), finishedSoon) == active.end());
}

TEST_MAIN()
