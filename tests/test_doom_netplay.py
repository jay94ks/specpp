import unittest

from doom_netplay import Demo, NetGame, TicCmd, TicCmdSource


class NetGameRequiredTest(unittest.TestCase):
    """netplay.md의 test_required Doom.NetGame 블록과 두 Examples를 옮긴 테스트."""

    def test_not_ready_until_all_players_arrived(self):
        net = NetGame(localPlayerIndex=0, players=[object(), object()])
        net.receiveRemoteTicCmd(100, 0, TicCmd(1, 0, 0, 0))
        self.assertFalse(net.isReadyToAdvance(100))
        net.receiveRemoteTicCmd(100, 1, TicCmd(0, 1, 0, 0))
        self.assertTrue(net.isReadyToAdvance(100))

    def test_unknown_tic_is_not_ready(self):
        net = NetGame(localPlayerIndex=0, players=[object()])
        self.assertFalse(net.isReadyToAdvance(999))


class TicCmdSourceLocalTest(unittest.TestCase):
    def test_local_mode_builds_ticcmd_from_raw_input(self):
        src = TicCmdSource(TicCmdSource.MODE_LOCAL)
        cmd = src.collect(0, {"forwardMove": 50, "sideMove": 0, "angleTurn": 10, "buttons": 1})
        self.assertEqual(cmd, TicCmd(50, 0, 10, 1))


class DemoRecordAndPlaybackTest(unittest.TestCase):
    """netplay.md의 '## 예제: 데모는 정확히 재현된다'를 옮긴 테스트."""

    def test_recorded_ticcmds_replay_identically(self):
        demo = Demo(header=("E1M1", 2))
        recorder = TicCmdSource(TicCmdSource.MODE_RECORD, demo=demo)
        inputs = [
            {"forwardMove": 50, "sideMove": 0, "angleTurn": 0, "buttons": 0},
            {"forwardMove": 50, "sideMove": 0, "angleTurn": 5, "buttons": 0},
            {"forwardMove": 0, "sideMove": 0, "angleTurn": 0, "buttons": 1},
        ]
        recordedCmds = [recorder.collect(tic, raw) for tic, raw in enumerate(inputs)]

        player = TicCmdSource(TicCmdSource.MODE_PLAYBACK, demo=demo)
        replayedCmds = []
        for tic in range(len(inputs)):
            replayedCmds.append(player.collect(tic, {}))

        self.assertEqual(recordedCmds, replayedCmds)

    def test_playback_ends_when_commands_exhausted(self):
        demo = Demo(header=("E1M1", 2), recordedTicCmds=[TicCmd(1, 0, 0, 0)])
        player = TicCmdSource(TicCmdSource.MODE_PLAYBACK, demo=demo)
        self.assertIsNotNone(player.collect(0, {}))
        self.assertIsNone(player.collect(1, {}))
        self.assertTrue(player.playbackFinished)

    def test_demo_round_trips_through_bytes(self):
        demo = Demo(header=("E1M1", 3), recordedTicCmds=[TicCmd(50, -10, 5, 1), TicCmd(0, 0, 0, 0)])
        restored = Demo.Load(demo.toBytes())
        self.assertEqual(restored.header, demo.header)
        self.assertEqual(restored.recordedTicCmds, demo.recordedTicCmds)


class NetplayTicCmdSourceTest(unittest.TestCase):
    """netplay.md의 '## 예제: 멀티플레이는 모두 도착해야 진행한다'를 옮긴 테스트."""

    def test_waits_for_remote_ticcmd_before_advancing(self):
        net = NetGame(localPlayerIndex=0, players=[object(), object()])
        src = TicCmdSource(TicCmdSource.MODE_NET, netGame=net)

        result = src.collect(100, {"forwardMove": 10, "sideMove": 0, "angleTurn": 0, "buttons": 0})
        self.assertIsNone(result)  # player 1의 명령이 아직 없다.

        net.receiveRemoteTicCmd(100, 1, TicCmd(0, 0, 0, 0))
        # 로컬 입력을 다시 broadcast(같은 tic 재수집)하면 이제 모두 모였다.
        result = src.collect(100, {"forwardMove": 10, "sideMove": 0, "angleTurn": 0, "buttons": 0})
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
