// examples/rock-paper-scissors.md 의 # Domain(Rps.Game/Rps.RoundResult)
// 참조 구현 (C++17). GUI와 무관한 순수 규칙만 다룬다.
#pragma once
#include <functional>
#include <map>
#include <random>
#include <string>

namespace Rps {

enum class Choice { Rock, Paper, Scissors };
enum class Outcome { Win, Lose, Draw };

inline Choice beats(Choice c) {
    // Rock은 Scissors를, Scissors는 Paper를, Paper는 Rock을 이긴다.
    switch (c) {
        case Choice::Rock: return Choice::Scissors;
        case Choice::Scissors: return Choice::Paper;
        case Choice::Paper: return Choice::Rock;
    }
    return Choice::Rock;
}

struct RoundResult {
    Choice playerChoice;
    Choice computerChoice;
    Outcome outcome;
};

class Game {
    std::function<Choice()> computerChooser_;

public:
    int playerScore = 0;
    int computerScore = 0;

    Game() : computerChooser_([]() {
        static std::mt19937 rng{std::random_device{}()};
        static std::uniform_int_distribution<int> dist(0, 2);
        return static_cast<Choice>(dist(rng));
    }) {}

    explicit Game(std::function<Choice()> computerChooser) : computerChooser_(std::move(computerChooser)) {}

    // spp-source: examples/rock-paper-scissors.md#Domain.Class:Rps.Game
    RoundResult play(Choice playerChoice) {
        Choice computerChoice = computerChooser_();

        Outcome outcome;
        if (playerChoice == computerChoice) {
            outcome = Outcome::Draw;
        } else if (beats(playerChoice) == computerChoice) {
            outcome = Outcome::Win;
            playerScore++;
        } else {
            outcome = Outcome::Lose;
            computerScore++;
        }
        return RoundResult{playerChoice, computerChoice, outcome};
    }
};

}  // namespace Rps
