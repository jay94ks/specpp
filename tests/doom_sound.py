"""examples/doom/sound.md 의 # Domain/# Behavior 참조 구현."""
import struct

MAX_CHANNELS = 8


class SoundEffect:
    def __init__(self, name, sampleRate, pcmSamples):
        self.name = name
        self.sampleRate = sampleRate
        self.pcmSamples = pcmSamples

    # spp-source: examples/doom/sound.md#Domain.Class:Doom.SoundEffect.Load
    @staticmethod
    def Load(wad, lumpName):
        idx = wad.findLump(lumpName)
        if idx < 0:
            raise ValueError(f"sound lump not found: {lumpName}")
        data = wad.readLump(idx)
        fmt, sampleRate, sampleCount = struct.unpack_from("<HHI", data, 0)
        if fmt != 3:
            raise ValueError(f"unexpected DMX format id: {fmt}")
        pcm = data[8 : 8 + sampleCount]
        return SoundEffect(lumpName, sampleRate, pcm)


class MusicTrack:
    def __init__(self, name, lumpName):
        self.name = name
        self.lumpName = lumpName


class PlayingSound:
    def __init__(self, effect, x, y, positional):
        self.effect = effect
        self.x = x
        self.y = y
        self.positional = positional


class SoundSystem:
    def __init__(self, wad=None, max_channels=MAX_CHANNELS):
        self.wad = wad
        self.effectCache = {}
        self.playing = []
        self.max_channels = max_channels
        self.currentMusic = None

    def init(self):
        self.playing = []

    # spp-source: examples/doom/sound.md#Feature:_효과음_재생
    def playEffect(self, effectName, source, listener):
        if effectName not in self.effectCache:
            self.effectCache[effectName] = SoundEffect.Load(self.wad, effectName)
        effect = self.effectCache[effectName]

        if len(self.playing) >= self.max_channels:
            farthest = self._farthest_from(listener)
            if farthest is not None:
                self.playing.remove(farthest)

        if source is not None:
            playing = PlayingSound(effect, source.x, source.y, positional=True)
        else:
            playing = PlayingSound(effect, listener.actor.x, listener.actor.y, positional=False)
        self.playing.append(playing)
        return playing

    def _farthest_from(self, listener):
        if not self.playing:
            return None
        lx, ly = listener.actor.x, listener.actor.y
        return max(self.playing, key=lambda p: (p.x - lx) ** 2 + (p.y - ly) ** 2)

    def playMusic(self, track):
        self.currentMusic = track

    def stopMusic(self):
        self.currentMusic = None

    def updateListenerPosition(self, listener):
        pass

    def panFor(self, playing, listener):
        """왼쪽/오른쪽 어느 쪽이 더 크게 들려야 하는지: -1(완전 왼쪽)~+1(완전 오른쪽)."""
        if not playing.positional:
            return 0.0
        dx = playing.x - listener.actor.x
        angle = listener.viewAngle
        import math
        rad = math.radians(angle)
        forward = (math.cos(rad), math.sin(rad))
        right = (-forward[1], forward[0])
        dy = playing.y - listener.actor.y
        pan = dx * right[0] + dy * right[1]
        return max(-1.0, min(1.0, pan / 200.0))
