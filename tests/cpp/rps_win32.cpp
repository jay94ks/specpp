// examples/rock-paper-scissors.md 의 # Interface > ## GUI 참조 구현
// (C++17, 순수 Win32 API — std/windows/win32.md, std/ui/widgets.md 대응).
//
// 프레임워크 없이 CreateWindowExW로 만든 버튼 3개("BUTTON" 클래스)와
// 정적 텍스트 2개("STATIC" 클래스)로 이루어진 실제 창을 띄운다. 버튼 클릭은
// WM_COMMAND 메시지로 들어오며, wndProc에서 컨트롤 ID로 구분해
// Rps::Game::play()를 호출하고 두 라벨을 갱신한다.
#include <windows.h>
#include <string>
#include "rps_game.hpp"

namespace {

constexpr int ID_ROCK = 101;
constexpr int ID_PAPER = 102;
constexpr int ID_SCISSORS = 103;

Rps::Game g_game;
HWND g_resultLabel;
HWND g_scoreLabel;

const wchar_t* choiceLabel(Rps::Choice c) {
    switch (c) {
        case Rps::Choice::Rock: return L"바위";
        case Rps::Choice::Paper: return L"보";
        case Rps::Choice::Scissors: return L"가위";
    }
    return L"";
}

const wchar_t* outcomeText(Rps::Outcome o) {
    switch (o) {
        case Rps::Outcome::Win: return L"이겼습니다!";
        case Rps::Outcome::Lose: return L"졌습니다.";
        case Rps::Outcome::Draw: return L"비겼습니다.";
    }
    return L"";
}

void updateScoreLabel() {
    std::wstring text = L"당신 " + std::to_wstring(g_game.playerScore) + L" : " +
                         std::to_wstring(g_game.computerScore) + L" 컴퓨터";
    SetWindowTextW(g_scoreLabel, text.c_str());
}

// spp-source: examples/rock-paper-scissors.md#Behavior.한 라운드 진행
void playRound(Rps::Choice choice) {
    Rps::RoundResult r = g_game.play(choice);
    std::wstring text = std::wstring(L"당신: ") + choiceLabel(r.playerChoice) +
                         L" / 컴퓨터: " + choiceLabel(r.computerChoice) + L" — " +
                         outcomeText(r.outcome);
    SetWindowTextW(g_resultLabel, text.c_str());
    updateScoreLabel();
}

LRESULT CALLBACK wndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_COMMAND: {
            int id = LOWORD(wParam);
            if (id == ID_ROCK) playRound(Rps::Choice::Rock);
            else if (id == ID_PAPER) playRound(Rps::Choice::Paper);
            else if (id == ID_SCISSORS) playRound(Rps::Choice::Scissors);
            return 0;
        }
        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
    }
    return DefWindowProcW(hwnd, msg, wParam, lParam);
}

}  // namespace

int main() {
    HINSTANCE hInstance = GetModuleHandleW(nullptr);

    WNDCLASSW wc = {};
    wc.lpfnWndProc = wndProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = L"RpsWindowClass";
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    RegisterClassW(&wc);

    HWND window = CreateWindowExW(
        0, L"RpsWindowClass", L"가위바위보", WS_OVERLAPPEDWINDOW & ~WS_THICKFRAME & ~WS_MAXIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, 340, 220, nullptr, nullptr, hInstance, nullptr);

    CreateWindowExW(0, L"BUTTON", L"✊ 바위", WS_CHILD | WS_VISIBLE, 20, 20, 80, 40,
                     window, (HMENU)(INT_PTR)ID_ROCK, hInstance, nullptr);
    CreateWindowExW(0, L"BUTTON", L"✋ 보", WS_CHILD | WS_VISIBLE, 120, 20, 80, 40,
                     window, (HMENU)(INT_PTR)ID_PAPER, hInstance, nullptr);
    CreateWindowExW(0, L"BUTTON", L"✌️ 가위", WS_CHILD | WS_VISIBLE, 220, 20, 80, 40,
                     window, (HMENU)(INT_PTR)ID_SCISSORS, hInstance, nullptr);

    g_resultLabel = CreateWindowExW(0, L"STATIC", L"눌러서 시작하세요",
                                     WS_CHILD | WS_VISIBLE, 20, 80, 280, 40, window, nullptr, hInstance, nullptr);
    g_scoreLabel = CreateWindowExW(0, L"STATIC", L"", WS_CHILD | WS_VISIBLE,
                                    20, 130, 280, 30, window, nullptr, hInstance, nullptr);
    updateScoreLabel();

    ShowWindow(window, SW_SHOW);
    UpdateWindow(window);

    MSG msg;
    while (GetMessageW(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
    return 0;
}
