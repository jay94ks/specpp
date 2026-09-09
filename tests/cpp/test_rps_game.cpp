#include "minitest.hpp"
#include "rps_game.hpp"

using namespace Rps;

TEST(test_player_wins) {
    Game game([]() { return Choice::Scissors; });
    RoundResult r = game.play(Choice::Rock);
    CHECK(r.outcome == Outcome::Win);
    CHECK_EQ(game.playerScore, 1);
    CHECK_EQ(game.computerScore, 0);
}

TEST(test_player_loses) {
    Game game([]() { return Choice::Paper; });
    RoundResult r = game.play(Choice::Rock);
    CHECK(r.outcome == Outcome::Lose);
    CHECK_EQ(game.computerScore, 1);
    CHECK_EQ(game.playerScore, 0);
}

TEST(test_draw) {
    Game game([]() { return Choice::Rock; });
    RoundResult r = game.play(Choice::Rock);
    CHECK(r.outcome == Outcome::Draw);
    CHECK_EQ(game.playerScore, 0);
    CHECK_EQ(game.computerScore, 0);
}

TEST(test_score_accumulates_across_rounds) {
    Game game([]() { return Choice::Scissors; });
    RoundResult r1 = game.play(Choice::Rock);
    RoundResult r2 = game.play(Choice::Rock);
    CHECK(r1.outcome == Outcome::Win);
    CHECK(r2.outcome == Outcome::Win);
    CHECK_EQ(game.playerScore, 2);
}

// test_required Rps.Game
TEST(test_rock_beats_scissors_scissors_beats_paper_paper_beats_rock) {
    CHECK(Game([]() { return Choice::Scissors; }).play(Choice::Rock).outcome == Outcome::Win);
    CHECK(Game([]() { return Choice::Paper; }).play(Choice::Scissors).outcome == Outcome::Win);
    CHECK(Game([]() { return Choice::Rock; }).play(Choice::Paper).outcome == Outcome::Win);
}

TEST(test_same_choice_is_always_draw_and_scores_unchanged) {
    for (Choice c : {Choice::Rock, Choice::Paper, Choice::Scissors}) {
        Game game([c]() { return c; });
        RoundResult r = game.play(c);
        CHECK(r.outcome == Outcome::Draw);
        CHECK_EQ(game.playerScore, 0);
        CHECK_EQ(game.computerScore, 0);
    }
}

TEST(test_scores_never_negative) {
    Game game([]() { return Choice::Paper; });
    for (int i = 0; i < 5; i++) game.play(Choice::Rock);
    CHECK(game.playerScore >= 0);
    CHECK(game.computerScore >= 0);
}

TEST_MAIN()
