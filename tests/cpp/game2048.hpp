// examples/2048.md 의 # Domain(Game2048.Game) 참조 구현 (C++17). GUI와 무관하다.
#pragma once
#include <algorithm>
#include <array>
#include <functional>
#include <random>
#include <string>
#include <utility>
#include <vector>

namespace Game2048 {

constexpr int BOARD_SIZE = 4;
using Grid = std::array<std::array<int, BOARD_SIZE>, BOARD_SIZE>;

enum class Direction { Up, Down, Left, Right };

namespace detail {

inline std::pair<std::array<int, BOARD_SIZE>, int> mergeLine(std::array<int, BOARD_SIZE> line) {
    std::vector<int> filtered;
    for (int v : line)
        if (v != 0) filtered.push_back(v);

    std::vector<int> merged;
    int gained = 0;
    size_t i = 0;
    while (i < filtered.size()) {
        if (i + 1 < filtered.size() && filtered[i] == filtered[i + 1]) {
            int value = filtered[i] * 2;
            merged.push_back(value);
            gained += value;
            i += 2;
        } else {
            merged.push_back(filtered[i]);
            i += 1;
        }
    }
    std::array<int, BOARD_SIZE> result{};
    for (size_t j = 0; j < merged.size(); j++) result[j] = merged[j];
    return {result, gained};
}

}  // namespace detail

class Game {
    std::function<double()> rng_;

    void spawnOnEmpty() {
        std::vector<std::pair<int, int>> empties;
        for (int r = 0; r < BOARD_SIZE; r++)
            for (int c = 0; c < BOARD_SIZE; c++)
                if (grid[r][c] == 0) empties.emplace_back(r, c);
        if (empties.empty()) return;
        int idx = std::min((int)(rng_() * empties.size()), (int)empties.size() - 1);
        auto [r, c] = empties[idx];
        grid[r][c] = rng_() < 0.9 ? 2 : 4;
    }

public:
    Grid grid{};
    int score = 0;

    Game() : rng_([]() {
        static std::mt19937 gen{std::random_device{}()};
        static std::uniform_real_distribution<double> dist(0.0, 1.0);
        return dist(gen);
    }) {
        spawnRandomTile();
        spawnRandomTile();
    }

    explicit Game(std::function<double()> rng) : rng_(std::move(rng)) {
        spawnRandomTile();
        spawnRandomTile();
    }

    // spp-source: examples/2048.md#Domain.Class:Game2048.Game
    bool move(Direction direction) {
        Grid before = grid;

        if (direction == Direction::Left || direction == Direction::Right) {
            bool reversed = direction == Direction::Right;
            for (int r = 0; r < BOARD_SIZE; r++) {
                std::array<int, BOARD_SIZE> line;
                for (int c = 0; c < BOARD_SIZE; c++) line[c] = grid[r][reversed ? BOARD_SIZE - 1 - c : c];
                auto [merged, gained] = detail::mergeLine(line);
                for (int c = 0; c < BOARD_SIZE; c++) grid[r][reversed ? BOARD_SIZE - 1 - c : c] = merged[c];
                score += gained;
            }
        } else {
            bool reversed = direction == Direction::Down;
            for (int c = 0; c < BOARD_SIZE; c++) {
                std::array<int, BOARD_SIZE> line;
                for (int r = 0; r < BOARD_SIZE; r++) line[r] = grid[reversed ? BOARD_SIZE - 1 - r : r][c];
                auto [merged, gained] = detail::mergeLine(line);
                for (int r = 0; r < BOARD_SIZE; r++) grid[reversed ? BOARD_SIZE - 1 - r : r][c] = merged[r];
                score += gained;
            }
        }

        return grid != before;
    }

    void spawnRandomTile() { spawnOnEmpty(); }

    bool isGameOver() const {
        for (int r = 0; r < BOARD_SIZE; r++)
            for (int c = 0; c < BOARD_SIZE; c++)
                if (grid[r][c] == 0) return false;
        for (int r = 0; r < BOARD_SIZE; r++) {
            for (int c = 0; c < BOARD_SIZE; c++) {
                int v = grid[r][c];
                if (c + 1 < BOARD_SIZE && grid[r][c + 1] == v) return false;
                if (r + 1 < BOARD_SIZE && grid[r + 1][c] == v) return false;
            }
        }
        return true;
    }

    bool hasWon() const {
        for (auto& row : grid)
            for (int v : row)
                if (v >= 2048) return true;
        return false;
    }
};

}  // namespace Game2048
