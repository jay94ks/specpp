import struct
import tempfile
import unittest

from doom_actors import Actor, MONSTER_TYPES, Player
from doom_sound import MAX_CHANNELS, SoundEffect, SoundSystem
from doom_wad import WadFile, build_wad_bytes


def _dmx_bytes(sampleRate, samples):
    header = struct.pack("<HHI", 3, sampleRate, len(samples))
    return header + bytes(samples)


class SoundEffectLoadTest(unittest.TestCase):
    def test_parses_dmx_header_and_pcm(self):
        data = build_wad_bytes([("DSPISTOL", _dmx_bytes(11025, [10, 20, 30, 200]))])
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(data)
        f.close()
        wad = WadFile(f.name)
        effect = SoundEffect.Load(wad, "DSPISTOL")
        self.assertEqual(effect.sampleRate, 11025)
        self.assertEqual(effect.pcmSamples, bytes([10, 20, 30, 200]))

    def test_rejects_unknown_format_id(self):
        data = build_wad_bytes([("DSBAD", struct.pack("<HHI", 99, 11025, 0))])
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(data)
        f.close()
        wad = WadFile(f.name)
        with self.assertRaises(ValueError):
            SoundEffect.Load(wad, "DSBAD")


class SoundSystemTest(unittest.TestCase):
    """sound.md의 '## 예제: 총소리는 쏜 위치에서 난다'와 채널 한도 검증."""

    def setUp(self):
        lumps = [(f"DSSND{i}", _dmx_bytes(11025, [0])) for i in range(MAX_CHANNELS + 2)]
        data = build_wad_bytes(lumps)
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(data)
        f.close()
        self.wad = WadFile(f.name)
        self.system = SoundSystem(self.wad)
        listenerActor = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)
        self.player = Player(listenerActor)

    def test_positional_sound_pans_toward_source_side(self):
        # 리스너는 +x 방향(viewAngle=0)을 보고 있다 — 왼/오는 y축 방향이다.
        left_source = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, -100)
        right_source = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 100)
        leftPlaying = self.system.playEffect("DSSND0", left_source, self.player)
        rightPlaying = self.system.playEffect("DSSND0", right_source, self.player)
        leftPan = self.system.panFor(leftPlaying, self.player)
        rightPan = self.system.panFor(rightPlaying, self.player)
        self.assertLess(leftPan, 0)
        self.assertGreater(rightPan, 0)

    def test_non_positional_sound_has_zero_pan(self):
        playing = self.system.playEffect("DSSND0", None, self.player)
        self.assertEqual(self.system.panFor(playing, self.player), 0.0)

    def test_channel_limit_evicts_farthest_sound(self):
        near = Actor.Spawn(MONSTER_TYPES["Zombieman"], 10, 0)
        far = Actor.Spawn(MONSTER_TYPES["Zombieman"], 5000, 0)
        for i in range(MAX_CHANNELS):
            self.system.playEffect(f"DSSND{i}", near, self.player)
        farPlaying = self.system.playEffect(f"DSSND{MAX_CHANNELS}", far, self.player)
        self.assertEqual(len(self.system.playing), MAX_CHANNELS)
        newest = self.system.playEffect(f"DSSND{MAX_CHANNELS + 1}", near, self.player)
        self.assertNotIn(farPlaying, self.system.playing)
        self.assertIn(newest, self.system.playing)

    def test_effect_cache_reuses_loaded_sound(self):
        self.system.playEffect("DSSND0", None, self.player)
        first = self.system.effectCache["DSSND0"]
        self.system.playEffect("DSSND0", None, self.player)
        self.assertIs(self.system.effectCache["DSSND0"], first)


if __name__ == "__main__":
    unittest.main()
