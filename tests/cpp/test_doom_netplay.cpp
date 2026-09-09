// examples/doom/netplay.md 검증 (C++17).
#include "doom_netplay.hpp"
#include "minitest.hpp"

using namespace Doom;

TEST(netgame_not_ready_until_all_players_arrived) {
    NetGame net(0, 2);
    net.receiveRemoteTicCmd(100, 0, TicCmd{1, 0, 0, 0});
    CHECK(!net.isReadyToAdvance(100));
    net.receiveRemoteTicCmd(100, 1, TicCmd{0, 1, 0, 0});
    CHECK(net.isReadyToAdvance(100));
}

TEST(netgame_unknown_tic_not_ready) {
    NetGame net(0, 1);
    CHECK(!net.isReadyToAdvance(999));
}

TEST(local_mode_builds_ticcmd_from_raw_input) {
    TicCmdSource src(TicCmdSource::Local);
    auto cmd = src.collect(0, RawPlayerInput{50, 0, 10, 1});
    TicCmd expected{50, 0, 10, 1};
    CHECK(cmd.has_value());
    CHECK(*cmd == expected);
}

TEST(demo_record_and_playback_replay_identically) {
    Demo demo{"E1M1", 2, {}};
    TicCmdSource recorder(TicCmdSource::Record, &demo);
    std::vector<RawPlayerInput> inputs = {
        {50, 0, 0, 0}, {50, 0, 5, 0}, {0, 0, 0, 1},
    };
    std::vector<TicCmd> recorded;
    for (int tic = 0; tic < 3; tic++) recorded.push_back(*recorder.collect(tic, inputs[tic]));

    TicCmdSource player(TicCmdSource::Playback, &demo);
    std::vector<TicCmd> replayed;
    for (int tic = 0; tic < 3; tic++) replayed.push_back(*player.collect(tic, {}));

    CHECK(recorded.size() == replayed.size());
    for (size_t i = 0; i < recorded.size(); i++) CHECK(recorded[i] == replayed[i]);
}

TEST(demo_playback_ends_when_exhausted) {
    Demo demo{"E1M1", 2, {TicCmd{1, 0, 0, 0}}};
    TicCmdSource player(TicCmdSource::Playback, &demo);
    CHECK(player.collect(0, {}).has_value());
    CHECK(!player.collect(1, {}).has_value());
    CHECK(player.playbackFinished);
}

TEST(demo_round_trips_through_bytes) {
    Demo demo{"E1M1", 3, {TicCmd{50, -10, 5, 1}, TicCmd{0, 0, 0, 0}}};
    auto restored = Demo::Load(demo.toBytes());
    CHECK_EQ(restored.mapName, demo.mapName);
    CHECK_EQ(restored.difficulty, demo.difficulty);
    CHECK(restored.recordedTicCmds.size() == demo.recordedTicCmds.size());
    for (size_t i = 0; i < demo.recordedTicCmds.size(); i++) {
        CHECK(restored.recordedTicCmds[i] == demo.recordedTicCmds[i]);
    }
}

TEST(multiplayer_waits_for_remote_ticcmd) {
    NetGame net(0, 2);
    TicCmdSource src(TicCmdSource::Net, nullptr, &net);

    auto result = src.collectMulti(100, RawPlayerInput{10, 0, 0, 0});
    CHECK(!result.has_value());

    net.receiveRemoteTicCmd(100, 1, TicCmd{0, 0, 0, 0});
    result = src.collectMulti(100, RawPlayerInput{10, 0, 0, 0});
    CHECK(result.has_value());
    CHECK_EQ(result->size(), 2u);
}

TEST_MAIN()
