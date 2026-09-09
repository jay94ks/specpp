"""examples/doom/netplay.md 의 # Domain/# Behavior 참조 구현."""


class TicCmd:
    def __init__(self, forwardMove=0, sideMove=0, angleTurn=0, buttons=0):
        self.forwardMove = forwardMove
        self.sideMove = sideMove
        self.angleTurn = angleTurn
        self.buttons = buttons

    def __eq__(self, other):
        return isinstance(other, TicCmd) and (
            self.forwardMove, self.sideMove, self.angleTurn, self.buttons
        ) == (other.forwardMove, other.sideMove, other.angleTurn, other.buttons)

    def __repr__(self):
        return f"TicCmd(fwd={self.forwardMove}, side={self.sideMove}, turn={self.angleTurn}, btn={self.buttons})"

    # spp-source: examples/doom/netplay.md#Domain.Class:Doom.TicCmd.FromInput
    @staticmethod
    def FromInput(rawInput):
        return TicCmd(
            forwardMove=rawInput.get("forwardMove", 0),
            sideMove=rawInput.get("sideMove", 0),
            angleTurn=rawInput.get("angleTurn", 0),
            buttons=rawInput.get("buttons", 0),
        )


class NetGame:
    def __init__(self, localPlayerIndex, players, isServer=True):
        self.localPlayerIndex = localPlayerIndex
        self.players = players
        self.pendingTicCmds = {}
        self.isServer = isServer

    def broadcastLocalTicCmd(self, tic, cmd):
        self.receiveRemoteTicCmd(tic, self.localPlayerIndex, cmd)

    def receiveRemoteTicCmd(self, tic, playerIndex, cmd):
        slot = self.pendingTicCmds.setdefault(tic, [None] * len(self.players))
        slot[playerIndex] = cmd

    # spp-source: examples/doom/netplay.md#Domain.Class:Doom.NetGame.isReadyToAdvance
    def isReadyToAdvance(self, tic):
        slot = self.pendingTicCmds.get(tic)
        if slot is None:
            return False
        return all(cmd is not None for cmd in slot)


class Demo:
    def __init__(self, header, recordedTicCmds=None):
        self.header = header
        self.recordedTicCmds = recordedTicCmds if recordedTicCmds is not None else []

    @staticmethod
    def Load(raw_bytes):
        import struct
        mapNameLen = raw_bytes[0]
        offset = 1
        mapName = raw_bytes[offset : offset + mapNameLen].decode("ascii")
        offset += mapNameLen
        difficulty = raw_bytes[offset]
        offset += 1
        count = struct.unpack_from("<I", raw_bytes, offset)[0]
        offset += 4
        cmds = []
        for _ in range(count):
            fwd, side, turn, btn = struct.unpack_from("<bbhB", raw_bytes, offset)
            offset += 5
            cmds.append(TicCmd(fwd, side, turn, btn))
        return Demo((mapName, difficulty), cmds)

    def toBytes(self):
        import struct
        mapName, difficulty = self.header
        out = bytes([len(mapName)]) + mapName.encode("ascii") + bytes([difficulty])
        out += struct.pack("<I", len(self.recordedTicCmds))
        for cmd in self.recordedTicCmds:
            out += struct.pack("<bbhB", cmd.forwardMove, cmd.sideMove, cmd.angleTurn, cmd.buttons)
        return out


class TicCmdSource:
    """Feature.틱 명령 수집: 로컬/데모 녹화/데모 재생/멀티플레이를 하나의 콜러블로 통일한다."""

    MODE_LOCAL = "local"
    MODE_RECORD = "record"
    MODE_PLAYBACK = "playback"
    MODE_NET = "net"

    def __init__(self, mode, demo=None, netGame=None):
        self.mode = mode
        self.demo = demo
        self.netGame = netGame
        self.playbackIndex = 0
        self.playbackFinished = False

    # spp-source: examples/doom/netplay.md#Feature:_틱_명령_수집(네트워크/로컬_공통)
    def collect(self, tic, rawInput):
        if self.mode == self.MODE_LOCAL:
            return TicCmd.FromInput(rawInput)

        if self.mode == self.MODE_RECORD:
            cmd = TicCmd.FromInput(rawInput)
            self.demo.recordedTicCmds.append(cmd)
            return cmd

        if self.mode == self.MODE_PLAYBACK:
            if self.playbackIndex >= len(self.demo.recordedTicCmds):
                self.playbackFinished = True
                return None
            cmd = self.demo.recordedTicCmds[self.playbackIndex]
            self.playbackIndex += 1
            return cmd

        if self.mode == self.MODE_NET:
            cmd = TicCmd.FromInput(rawInput)
            self.netGame.broadcastLocalTicCmd(tic, cmd)
            if not self.netGame.isReadyToAdvance(tic):
                return None
            return self.netGame.pendingTicCmds[tic]

        raise ValueError(f"unknown mode: {self.mode}")
