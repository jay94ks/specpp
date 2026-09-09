#include "minitest.hpp"
#include "game2048.hpp"

using namespace Game2048;

TEST(test_adjacent_tiles_merge) {
    Game game([]() { return 0.0; });
    game.grid = {{{2, 2, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}}};
    game.score = 0;
    game.move(Direction::Left);
    CHECK(game.grid[0] == (std::array<int, BOARD_SIZE>{4, 0, 0, 0}));
    CHECK_EQ(game.score, 4);
}

TEST(test_no_chain_merge_in_one_move) {
    Game game([]() { return 0.0; });
    game.grid = {{{2, 2, 2, 2}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}}};
    game.move(Direction::Left);
    CHECK(game.grid[0] == (std::array<int, BOARD_SIZE>{4, 4, 0, 0}));
}

TEST(test_no_op_move_returns_false_and_leaves_grid_unchanged) {
    Game game([]() { return 0.0; });
    game.grid = {{{4, 2, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}}};
    Grid before = game.grid;
    bool changed = game.move(Direction::Left);
    CHECK(!changed);
    CHECK(game.grid == before);
}

TEST(test_game_over_when_full_and_no_adjacent_equal) {
    Game game([]() { return 0.0; });
    game.grid = {{{2, 4, 2, 4}, {4, 2, 4, 2}, {2, 4, 2, 4}, {4, 2, 4, 2}}};
    CHECK(game.isGameOver());
}

// test_required Game2048.Game
TEST(test_merge_increases_score_by_merged_value) {
    Game game([]() { return 0.0; });
    game.grid = {{{8, 8, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}}};
    game.score = 0;
    game.move(Direction::Left);
    CHECK_EQ(game.score, 16);
}

TEST(test_four_equal_tiles_pair_up_not_chain_right) {
    Game game([]() { return 0.0; });
    game.grid = {{{2, 2, 2, 2}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}}};
    game.move(Direction::Right);
    CHECK(game.grid[0] == (std::array<int, BOARD_SIZE>{0, 0, 4, 4}));
}

TEST(test_move_with_nothing_to_do_returns_false) {
    Game game([]() { return 0.0; });
    game.grid = {{{0, 0, 0, 2}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}}};
    CHECK(!game.move(Direction::Right));
}

TEST(test_win_detection) {
    Game game([]() { return 0.0; });
    game.grid[0][0] = 2048;
    CHECK(game.hasWon());
}

TEST_MAIN()
