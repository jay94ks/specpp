// examples/notepad.md 의 # Interface > ## GUI 참조 구현 (C++17, 순수 Win32 —
// std/windows/win32.md 대응). 프레임워크 없음, 실제 EDIT 컨트롤 + 네이티브
// 메뉴 + 공용 파일 대화 상자.
//
// 범위: 새로 만들기/열기/저장/다른 이름으로 저장/끝내기(저장 확인 포함),
// 잘라내기/복사/붙여넣기/실행 취소/모두 선택(EDIT 컨트롤에 그대로 위임),
// 상태 표시줄(줄/열). 찾기/바꾸기/이동 대화 상자와 자동 줄 바꿈 토글은
// 시간 관계상 Python 버전(tests/app_notepad.py)에만 구현되어 있다 —
// std/ui/textbox.md의 core는 이 파일로도 검증되지만, 전체 기능 목록은
// Python 쪽이 더 완전하다.
#define NOMINMAX
#include <windows.h>
#include <commdlg.h>
#include <string>
#include <fstream>
#include <sstream>

#pragma comment(lib, "comdlg32.lib")

namespace {

constexpr int ID_FILE_NEW = 101;
constexpr int ID_FILE_OPEN = 102;
constexpr int ID_FILE_SAVE = 103;
constexpr int ID_FILE_SAVEAS = 104;
constexpr int ID_FILE_EXIT = 105;
constexpr int ID_EDIT_UNDO = 111;
constexpr int ID_EDIT_CUT = 112;
constexpr int ID_EDIT_COPY = 113;
constexpr int ID_EDIT_PASTE = 114;
constexpr int ID_EDIT_SELECTALL = 115;
constexpr int ID_EDITBOX = 200;

HWND g_mainWindow;
HWND g_editBox;
HWND g_statusBar;
std::wstring g_filePath;  // 비어있으면 "저장된 적 없음"
bool g_isDirty = false;

// spp-source: examples/notepad.md#Domain.Class:Notepad.App
void updateTitle() {
    std::wstring name = g_filePath.empty() ? L"제목 없음" : g_filePath.substr(g_filePath.find_last_of(L"\\/") + 1);
    SetWindowTextW(g_mainWindow, (name + L" - 메모장").c_str());
}

void updateStatusBar() {
    DWORD start = 0, end = 0;
    SendMessageW(g_editBox, EM_GETSEL, (WPARAM)&start, (LPARAM)&end);
    int line = (int)SendMessageW(g_editBox, EM_LINEFROMCHAR, start, 0) + 1;
    int lineStart = (int)SendMessageW(g_editBox, EM_LINEINDEX, line - 1, 0);
    int col = (int)start - lineStart + 1;
    wchar_t buf[64];
    swprintf_s(buf, L"줄 %d, 열 %d", line, col);
    SetWindowTextW(g_statusBar, buf);
}

std::wstring getEditText() {
    int len = GetWindowTextLengthW(g_editBox);
    std::wstring buf(len, L'\0');
    GetWindowTextW(g_editBox, buf.data(), len + 1);
    return buf;
}

void setEditText(const std::wstring& text) {
    SetWindowTextW(g_editBox, text.c_str());
    g_isDirty = false;
}

std::string toUtf8(const std::wstring& wide) {
    if (wide.empty()) return "";
    int len = WideCharToMultiByte(CP_UTF8, 0, wide.c_str(), (int)wide.size(), nullptr, 0, nullptr, nullptr);
    std::string out(len, '\0');
    WideCharToMultiByte(CP_UTF8, 0, wide.c_str(), (int)wide.size(), out.data(), len, nullptr, nullptr);
    return out;
}

std::wstring fromUtf8(const std::string& utf8) {
    if (utf8.empty()) return L"";
    int len = MultiByteToWideChar(CP_UTF8, 0, utf8.c_str(), (int)utf8.size(), nullptr, 0);
    std::wstring out(len, L'\0');
    MultiByteToWideChar(CP_UTF8, 0, utf8.c_str(), (int)utf8.size(), out.data(), len);
    return out;
}

bool writeFile(const std::wstring& path, const std::wstring& text) {
    std::ofstream out(path, std::ios::binary);
    if (!out) return false;
    std::string utf8 = toUtf8(text);
    out.write(utf8.data(), (std::streamsize)utf8.size());
    return true;
}

bool readFile(const std::wstring& path, std::wstring& outText) {
    std::ifstream in(path, std::ios::binary);
    if (!in) return false;
    std::ostringstream ss;
    ss << in.rdbuf();
    outText = fromUtf8(ss.str());
    return true;
}

// spp-source: examples/notepad.md#Domain.Class:Notepad.App
bool saveCurrent();

bool saveAsDialog() {
    wchar_t fileBuf[MAX_PATH] = L"";
    if (!g_filePath.empty()) wcsncpy_s(fileBuf, g_filePath.c_str(), _TRUNCATE);

    OPENFILENAMEW ofn = {};
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = g_mainWindow;
    ofn.lpstrFilter = L"텍스트 문서 (*.txt)\0*.txt\0모든 파일 (*.*)\0*.*\0";
    ofn.lpstrFile = fileBuf;
    ofn.nMaxFile = MAX_PATH;
    ofn.lpstrDefExt = L"txt";
    ofn.Flags = OFN_OVERWRITEPROMPT;

    if (!GetSaveFileNameW(&ofn)) return false;
    if (!writeFile(fileBuf, getEditText())) return false;
    g_filePath = fileBuf;
    g_isDirty = false;
    updateTitle();
    return true;
}

bool saveCurrent() {
    if (g_filePath.empty()) return saveAsDialog();
    if (!writeFile(g_filePath, getEditText())) return false;
    g_isDirty = false;
    updateTitle();
    return true;
}

// spp-source: examples/notepad.md#Domain.Class:Notepad.App
// 반환값: 진행해도 되면 true(=이어서 하려던 동작을 계속), 취소면 false.
bool confirmDiscardChanges() {
    if (!g_isDirty) return true;
    int choice = MessageBoxW(g_mainWindow, L"변경 내용을 저장하시겠습니까?", L"메모장", MB_YESNOCANCEL | MB_ICONWARNING);
    if (choice == IDCANCEL) return false;
    if (choice == IDNO) return true;
    return saveCurrent();
}

// spp-source: examples/notepad.md#Behavior.새로 만들기
void newDocument() {
    if (!confirmDiscardChanges()) return;
    setEditText(L"");
    g_filePath.clear();
    updateTitle();
}

// spp-source: examples/notepad.md#Behavior.파일 열기
void openDialog() {
    if (!confirmDiscardChanges()) return;

    wchar_t fileBuf[MAX_PATH] = L"";
    OPENFILENAMEW ofn = {};
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = g_mainWindow;
    ofn.lpstrFilter = L"텍스트 문서 (*.txt)\0*.txt\0모든 파일 (*.*)\0*.*\0";
    ofn.lpstrFile = fileBuf;
    ofn.nMaxFile = MAX_PATH;
    ofn.Flags = OFN_FILEMUSTEXIST;

    if (!GetOpenFileNameW(&ofn)) return;

    std::wstring text;
    if (!readFile(fileBuf, text)) {
        MessageBoxW(g_mainWindow, L"파일을 열 수 없습니다.", L"메모장", MB_ICONERROR);
        return;
    }
    setEditText(text);
    g_filePath = fileBuf;
    updateTitle();
}

// spp-source: examples/notepad.md#Behavior.끝내기
void requestExit() {
    if (confirmDiscardChanges()) DestroyWindow(g_mainWindow);
}

HMENU buildMenu() {
    HMENU menuBar = CreateMenu();

    HMENU fileMenu = CreateMenu();
    AppendMenuW(fileMenu, MF_STRING, ID_FILE_NEW, L"새로 만들기\tCtrl+N");
    AppendMenuW(fileMenu, MF_STRING, ID_FILE_OPEN, L"열기...\tCtrl+O");
    AppendMenuW(fileMenu, MF_STRING, ID_FILE_SAVE, L"저장\tCtrl+S");
    AppendMenuW(fileMenu, MF_STRING, ID_FILE_SAVEAS, L"다른 이름으로 저장...");
    AppendMenuW(fileMenu, MF_SEPARATOR, 0, nullptr);
    AppendMenuW(fileMenu, MF_STRING, ID_FILE_EXIT, L"끝내기");
    AppendMenuW(menuBar, MF_POPUP, (UINT_PTR)fileMenu, L"파일(&F)");

    HMENU editMenu = CreateMenu();
    AppendMenuW(editMenu, MF_STRING, ID_EDIT_UNDO, L"실행 취소\tCtrl+Z");
    AppendMenuW(editMenu, MF_SEPARATOR, 0, nullptr);
    AppendMenuW(editMenu, MF_STRING, ID_EDIT_CUT, L"잘라내기\tCtrl+X");
    AppendMenuW(editMenu, MF_STRING, ID_EDIT_COPY, L"복사\tCtrl+C");
    AppendMenuW(editMenu, MF_STRING, ID_EDIT_PASTE, L"붙여넣기\tCtrl+V");
    AppendMenuW(editMenu, MF_SEPARATOR, 0, nullptr);
    AppendMenuW(editMenu, MF_STRING, ID_EDIT_SELECTALL, L"모두 선택\tCtrl+A");
    AppendMenuW(menuBar, MF_POPUP, (UINT_PTR)editMenu, L"편집(&E)");

    return menuBar;
}

LRESULT CALLBACK wndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CREATE: {
            g_editBox = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"",
                                         WS_CHILD | WS_VISIBLE | WS_VSCROLL | ES_MULTILINE | ES_AUTOVSCROLL |
                                             ES_WANTRETURN,
                                         0, 0, 0, 0, hwnd, (HMENU)(INT_PTR)ID_EDITBOX, GetModuleHandleW(nullptr),
                                         nullptr);
            g_statusBar = CreateWindowExW(0, L"STATIC", L"줄 1, 열 1", WS_CHILD | WS_VISIBLE | SS_SUNKEN, 0, 0, 0, 0,
                                           hwnd, nullptr, GetModuleHandleW(nullptr), nullptr);
            SetMenu(hwnd, buildMenu());
            return 0;
        }
        case WM_SIZE: {
            RECT rc;
            GetClientRect(hwnd, &rc);
            int statusHeight = 22;
            MoveWindow(g_editBox, 0, 0, rc.right, rc.bottom - statusHeight, TRUE);
            MoveWindow(g_statusBar, 0, rc.bottom - statusHeight, rc.right, statusHeight, TRUE);
            return 0;
        }
        case WM_COMMAND: {
            int id = LOWORD(wParam);
            int notify = HIWORD(wParam);
            if ((HWND)lParam == g_editBox && notify == EN_CHANGE) {
                g_isDirty = true;
                updateStatusBar();
                return 0;
            }
            switch (id) {
                case ID_FILE_NEW: newDocument(); break;
                case ID_FILE_OPEN: openDialog(); break;
                case ID_FILE_SAVE: saveCurrent(); break;
                case ID_FILE_SAVEAS: saveAsDialog(); break;
                case ID_FILE_EXIT: requestExit(); break;
                case ID_EDIT_UNDO: SendMessageW(g_editBox, EM_UNDO, 0, 0); break;
                case ID_EDIT_CUT: SendMessageW(g_editBox, WM_CUT, 0, 0); break;
                case ID_EDIT_COPY: SendMessageW(g_editBox, WM_COPY, 0, 0); break;
                case ID_EDIT_PASTE: SendMessageW(g_editBox, WM_PASTE, 0, 0); break;
                case ID_EDIT_SELECTALL: SendMessageW(g_editBox, EM_SETSEL, 0, -1); break;
            }
            return 0;
        }
        case WM_SETFOCUS:
            SetFocus(g_editBox);
            return 0;
        case WM_CLOSE:
            requestExit();
            return 0;
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
    wc.lpszClassName = L"NotepadCloneWindowClass";
    wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_BTNFACE + 1);
    RegisterClassW(&wc);

    g_mainWindow = CreateWindowExW(0, L"NotepadCloneWindowClass", L"제목 없음 - 메모장", WS_OVERLAPPEDWINDOW,
                                    CW_USEDEFAULT, CW_USEDEFAULT, 700, 500, nullptr, nullptr, hInstance, nullptr);

    ShowWindow(g_mainWindow, SW_SHOW);
    UpdateWindow(g_mainWindow);

    HACCEL accel = nullptr;
    ACCEL accels[] = {
        {FCONTROL | FVIRTKEY, 'N', ID_FILE_NEW},
        {FCONTROL | FVIRTKEY, 'O', ID_FILE_OPEN},
        {FCONTROL | FVIRTKEY, 'S', ID_FILE_SAVE},
        {FCONTROL | FVIRTKEY, 'Z', ID_EDIT_UNDO},
        {FCONTROL | FVIRTKEY, 'X', ID_EDIT_CUT},
        {FCONTROL | FVIRTKEY, 'C', ID_EDIT_COPY},
        {FCONTROL | FVIRTKEY, 'V', ID_EDIT_PASTE},
        {FCONTROL | FVIRTKEY, 'A', ID_EDIT_SELECTALL},
    };
    accel = CreateAcceleratorTableW(accels, sizeof(accels) / sizeof(accels[0]));

    MSG msg;
    while (GetMessageW(&msg, nullptr, 0, 0)) {
        if (!TranslateAcceleratorW(g_mainWindow, accel, &msg)) {
            TranslateMessage(&msg);
            DispatchMessageW(&msg);
        }
    }
    return 0;
}
