// examples/doom/sound.md 검증 (C++17).
#include "doom_sound.hpp"
#include "minitest.hpp"
#include <cstring>
#include <fstream>

using namespace Doom;

static std::vector<uint8_t> dmxBytes(uint16_t sampleRate, std::vector<uint8_t> samples) {
    std::vector<uint8_t> out;
    auto append16 = [&](uint16_t v) { auto p = reinterpret_cast<uint8_t*>(&v); out.insert(out.end(), p, p + 2); };
    auto append32 = [&](uint32_t v) { auto p = reinterpret_cast<uint8_t*>(&v); out.insert(out.end(), p, p + 4); };
    append16(3);
    append16(sampleRate);
    append32(static_cast<uint32_t>(samples.size()));
    out.insert(out.end(), samples.begin(), samples.end());
    return out;
}

static std::string writeWad(const std::vector<std::pair<std::string, std::vector<uint8_t>>>& lumps,
                             const char* suffix) {
    auto bytes = buildWadBytes(lumps);
    std::string path = std::string("tmp_sound_test") + suffix + ".wad";
    std::ofstream f(path, std::ios::binary);
    f.write(reinterpret_cast<const char*>(bytes.data()), bytes.size());
    return path;
}

TEST(sound_effect_load_parses_dmx_header_and_pcm) {
    auto path = writeWad({{"DSPISTOL", dmxBytes(11025, {10, 20, 30, 200})}}, "_1");
    WadFile wad(path);
    auto effect = SoundEffect::Load(wad, "DSPISTOL");
    CHECK_EQ(effect.sampleRate, 11025);
    CHECK_EQ(effect.pcmSamples.size(), 4u);
    CHECK_EQ(effect.pcmSamples[3], 200);
}

TEST(sound_effect_rejects_unknown_format) {
    std::vector<uint8_t> bad;
    uint16_t fmt = 99, rate = 11025;
    uint32_t count = 0;
    bad.insert(bad.end(), reinterpret_cast<uint8_t*>(&fmt), reinterpret_cast<uint8_t*>(&fmt) + 2);
    bad.insert(bad.end(), reinterpret_cast<uint8_t*>(&rate), reinterpret_cast<uint8_t*>(&rate) + 2);
    bad.insert(bad.end(), reinterpret_cast<uint8_t*>(&count), reinterpret_cast<uint8_t*>(&count) + 4);
    auto path = writeWad({{"DSBAD", bad}}, "_2");
    WadFile wad(path);
    bool threw = false;
    try { SoundEffect::Load(wad, "DSBAD"); } catch (const std::exception&) { threw = true; }
    CHECK(threw);
}

TEST(sound_system_positional_pans_toward_source_side) {
    std::vector<std::pair<std::string, std::vector<uint8_t>>> lumps;
    for (int i = 0; i < MAX_CHANNELS + 2; i++) lumps.push_back({"DSSND" + std::to_string(i), dmxBytes(11025, {0})});
    auto path = writeWad(lumps, "_3");
    WadFile wad(path);
    SoundSystem system(&wad);
    auto listenerActor = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    Player listener(listenerActor);

    auto leftSource = Actor::Spawn(monsterTypes().at("Zombieman"), 0, -100);
    auto rightSource = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 100);
    auto leftPlaying = system.playEffect("DSSND0", leftSource.get(), &listener);
    auto rightPlaying = system.playEffect("DSSND0", rightSource.get(), &listener);
    CHECK(system.panFor(leftPlaying, &listener) < 0);
    CHECK(system.panFor(rightPlaying, &listener) > 0);
}

TEST(sound_system_non_positional_has_zero_pan) {
    auto path = writeWad({{"DSSND0", dmxBytes(11025, {0})}}, "_4");
    WadFile wad(path);
    SoundSystem system(&wad);
    auto listenerActor = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    Player listener(listenerActor);
    auto p = system.playEffect("DSSND0", nullptr, &listener);
    CHECK_EQ(system.panFor(p, &listener), 0.0f);
}

TEST(sound_system_channel_limit_evicts_farthest) {
    std::vector<std::pair<std::string, std::vector<uint8_t>>> lumps;
    for (int i = 0; i < MAX_CHANNELS + 2; i++) lumps.push_back({"DSSND" + std::to_string(i), dmxBytes(11025, {0})});
    auto path = writeWad(lumps, "_5");
    WadFile wad(path);
    SoundSystem system(&wad);
    auto listenerActor = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    Player listener(listenerActor);

    auto near = Actor::Spawn(monsterTypes().at("Zombieman"), 10, 0);
    auto far = Actor::Spawn(monsterTypes().at("Zombieman"), 5000, 0);
    for (int i = 0; i < MAX_CHANNELS; i++) system.playEffect("DSSND" + std::to_string(i), near.get(), &listener);
    auto farPlaying = system.playEffect("DSSND" + std::to_string(MAX_CHANNELS), far.get(), &listener);
    CHECK_EQ(system.playing.size(), size_t(MAX_CHANNELS));
    auto newest = system.playEffect("DSSND" + std::to_string(MAX_CHANNELS + 1), near.get(), &listener);
    CHECK(std::find(system.playing.begin(), system.playing.end(), farPlaying) == system.playing.end());
    CHECK(std::find(system.playing.begin(), system.playing.end(), newest) != system.playing.end());
}

TEST_MAIN()
