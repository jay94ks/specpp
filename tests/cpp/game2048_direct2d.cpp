// examples/2048.md 의 # Interface > ## GUI 참조 구현 (C++17, 순수 Win32 + Direct2D/DirectWrite —
// std/windows/win32.md, std/windows/direct2d.md 대응). 프레임워크 없음, 진짜 DirectX 렌더링.
#define NOMINMAX
#include <windows.h>
#include <d2d1.h>
#include <dwrite.h>
#include <string>
#include <sstream>
#include "game2048.hpp"

#pragma comment(lib, "d2d1.lib")
#pragma comment(lib, "dwrite.lib")

using namespace Game2048;

namespace {

constexpr int CELL = 90;
constexpr int PAD = 10;
constexpr int BOARD_TOP = 60;
constexpr int WINDOW_SIZE = PAD + BOARD_SIZE * (CELL + PAD) + BOARD_TOP;

ID2D1Factory* g_d2dFactory = nullptr;
IDWriteFactory* g_dwriteFactory = nullptr;
ID2D1HwndRenderTarget* g_renderTarget = nullptr;
IDWriteTextFormat* g_tileFormat = nullptr;
IDWriteTextFormat* g_scoreFormat = nullptr;

Game g_game;
bool g_wonAnnounced = false;

D2D1_COLOR_F hexColor(const char* hex) {
    unsigned int r, g, b;
    sscanf_s(hex + 1, "%02x%02x%02x", &r, &g, &b);
    return D2D1::ColorF(r / 255.0f, g / 255.0f, b / 255.0f);
}

const char* tileColor(int value) {
    switch (value) {
        case 0: return "#CDC1B4";
        case 2: return "#EEE4DA";
        case 4: return "#EDE0C8";
        case 8: return "#F2B179";
        case 16: return "#F59563";
        case 32: return "#F67C5F";
        case 64: return "#F65E3B";
        case 128: return "#EDCF72";
        case 256: return "#EDCC61";
        case 512: return "#EDC850";
        case 1024: return "#EDC53F";
        case 2048: return "#EDC22E";
        default: return "#3C3A32";
    }
}

void createDeviceResources(HWND hwnd) {
    if (g_renderTarget) return;
    RECT rc;
    GetClientRect(hwnd, &rc);
    D2D1_SIZE_U size = D2D1::SizeU(rc.right - rc.left, rc.bottom - rc.top);
    g_d2dFactory->CreateHwndRenderTarget(D2D1::RenderTargetProperties(),
                                         D2D1::HwndRenderTargetProperties(hwnd, size), &g_renderTarget);
}

void releaseDeviceResources() {
    if (g_renderTarget) {
        g_renderTarget->Release();
        g_renderTarget = nullptr;
    }
}

// spp-source: examples/2048.md#Interface.GUI
void render(HWND hwnd) {
    createDeviceResources(hwnd);
    if (!g_renderTarget) return;

    g_renderTarget->BeginDraw();
    g_renderTarget->Clear(hexColor("#BBADA0"));

    ID2D1SolidColorBrush* brush = nullptr;
    g_renderTarget->CreateSolidColorBrush(hexColor("#776E65"), &brush);

    std::wstring scoreText = L"점수: " + std::to_wstring(g_game.score);
    if (g_game.isGameOver()) scoreText += L"   [게임 오버]";
    else if (g_wonAnnounced) scoreText += L"   [2048 달성!]";
    g_renderTarget->DrawText(scoreText.c_str(), (UINT32)scoreText.size(), g_scoreFormat,
                              D2D1::RectF(PAD, 15, WINDOW_SIZE - PAD, BOARD_TOP), brush);
    brush->Release();

    for (int r = 0; r < BOARD_SIZE; r++) {
        for (int c = 0; c < BOARD_SIZE; c++) {
            int value = g_game.grid[r][c];
            float x = PAD + c * (CELL + PAD);
            float y = BOARD_TOP + PAD + r * (CELL + PAD);

            ID2D1SolidColorBrush* tileBrush = nullptr;
            g_renderTarget->CreateSolidColorBrush(hexColor(tileColor(value)), &tileBrush);
            g_renderTarget->FillRectangle(D2D1::RectF(x, y, x + CELL, y + CELL), tileBrush);
            tileBrush->Release();

            if (value != 0) {
                ID2D1SolidColorBrush* textBrush = nullptr;
                g_renderTarget->CreateSolidColorBrush(hexColor(value <= 4 ? "#776E65" : "#F9F6F2"), &textBrush);
                std::wstring text = std::to_wstring(value);
                g_renderTarget->DrawText(text.c_str(), (UINT32)text.size(), g_tileFormat,
                                          D2D1::RectF(x, y, x + CELL, y + CELL), textBrush);
                textBrush->Release();
            }
        }
    }

    HRESULT hr = g_renderTarget->EndDraw();
    if (hr == D2DERR_RECREATE_TARGET) releaseDeviceResources();
}

// spp-source: examples/2048.md#Behavior.방향키로 한 번 이동
void onKeyDown(HWND hwnd, Direction direction) {
    bool moved = g_game.move(direction);
    if (moved) g_game.spawnRandomTile();
    if (g_game.hasWon()) g_wonAnnounced = true;
    InvalidateRect(hwnd, nullptr, FALSE);
}

LRESULT CALLBACK wndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_PAINT: {
            PAINTSTRUCT ps;
            BeginPaint(hwnd, &ps);
            render(hwnd);
            EndPaint(hwnd, &ps);
            return 0;
        }
        case WM_SIZE:
            if (g_renderTarget) {
                g_renderTarget->Resize(D2D1::SizeU(LOWORD(lParam), HIWORD(lParam)));
            }
            return 0;
        case WM_KEYDOWN:
            switch (wParam) {
                case VK_UP: onKeyDown(hwnd, Direction::Up); break;
                case VK_DOWN: onKeyDown(hwnd, Direction::Down); break;
                case VK_LEFT: onKeyDown(hwnd, Direction::Left); break;
                case VK_RIGHT: onKeyDown(hwnd, Direction::Right); break;
            }
            return 0;
        case WM_DESTROY:
            releaseDeviceResources();
            PostQuitMessage(0);
            return 0;
    }
    return DefWindowProcW(hwnd, msg, wParam, lParam);
}

}  // namespace

int main() {
    D2D1CreateFactory(D2D1_FACTORY_TYPE_SINGLE_THREADED, &g_d2dFactory);
    DWriteCreateFactory(DWRITE_FACTORY_TYPE_SHARED, __uuidof(IDWriteFactory),
                         reinterpret_cast<IUnknown**>(&g_dwriteFactory));
    g_dwriteFactory->CreateTextFormat(L"Malgun Gothic", nullptr, DWRITE_FONT_WEIGHT_BOLD,
                                       DWRITE_FONT_STYLE_NORMAL, DWRITE_FONT_STRETCH_NORMAL, 28.0f, L"ko-kr",
                                       &g_tileFormat);
    g_tileFormat->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
    g_tileFormat->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);

    g_dwriteFactory->CreateTextFormat(L"Malgun Gothic", nullptr, DWRITE_FONT_WEIGHT_BOLD,
                                       DWRITE_FONT_STYLE_NORMAL, DWRITE_FONT_STRETCH_NORMAL, 18.0f, L"ko-kr",
                                       &g_scoreFormat);

    HINSTANCE hInstance = GetModuleHandleW(nullptr);
    WNDCLASSW wc = {};
    wc.lpfnWndProc = wndProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = L"Game2048WindowClass";
    wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    RegisterClassW(&wc);

    HWND window = CreateWindowExW(0, L"Game2048WindowClass", L"2048",
                                   (WS_OVERLAPPEDWINDOW & ~WS_THICKFRAME & ~WS_MAXIMIZEBOX), CW_USEDEFAULT,
                                   CW_USEDEFAULT, WINDOW_SIZE + 16, WINDOW_SIZE + 39, nullptr, nullptr, hInstance,
                                   nullptr);

    ShowWindow(window, SW_SHOW);
    UpdateWindow(window);

    MSG msg;
    while (GetMessageW(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }

    if (g_tileFormat) g_tileFormat->Release();
    if (g_scoreFormat) g_scoreFormat->Release();
    if (g_dwriteFactory) g_dwriteFactory->Release();
    if (g_d2dFactory) g_d2dFactory->Release();
    return 0;
}
