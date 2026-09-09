#!specpp 0.1

# Meta

- name: std/windows/registry
- version: 0.1.0
- description: Windows 레지스트리를 읽고 쓰는 수단.
- platform: windows -> fallback: package_like AppDirectories (예: std/linux/appdirs.md, std/macos/appdirs.md) + std/io/file.md 기반 설정 파일

# Intent

Windows 프로그램이 설정값을 레지스트리에 저장하거나 읽어야 할 때 쓴다.
레지스트리는 Windows에만 있는 개념이므로 이 패키지 전체가 Windows 전용이다
(Meta의 `platform` 필드, SPEC.md 3.10절). Linux/macOS에는 레지스트리에 대응하는
개념이 없으므로, 그곳에서는 [`std/system/appdirs.md`](../system/appdirs.md)로
설정 파일을 둘 위치를 찾고 [`std/io/file.md`](../io/file.md)와
[`std/text/json.md`](../text/json.md)로 직접 읽고 쓰는 방식으로 대체한다.

# Domain

## Class: RegistryKey

멤버:
[Static]
- HKEY_CURRENT_USER: string — 하이브 상수. 값은 `"HKEY_CURRENT_USER"`.
[Static]
- HKEY_LOCAL_MACHINE: string — 하이브 상수. 값은 `"HKEY_LOCAL_MACHINE"`.
[Static]
- HKEY_CLASSES_ROOT: string — 하이브 상수. 값은 `"HKEY_CLASSES_ROOT"`.
[Static]
- HKEY_USERS: string — 하이브 상수. 값은 `"HKEY_USERS"`.
[Static]
- HKEY_CURRENT_CONFIG: string — 하이브 상수. 값은 `"HKEY_CURRENT_CONFIG"`.

생성자:
- RegistryKey(hive: string, subKeyPath: string)
  설명: hive(위 상수 중 하나)와 subKeyPath(`"Software\MyApp"`처럼 `\`로 구분된
  경로)로 이미 존재하는 키를 연다. 없으면 오류를 낸다.

메서드:
[Static]
- create(hive: string, subKeyPath: string) -> RegistryKey
  설명: 키가 없으면 새로 만들고, 있으면 그대로 연다. 중간 경로가 없으면 함께
  만든다.
- getValue(name: string) -> string?
  설명: name 값을 읽어 문자열로 반환한다. 없으면 null.
- setValue(name: string, value: string) -> void
  설명: name 값을 value로 쓴다. 없으면 새로 만든다.
- deleteValue(name: string) -> void
  설명: name 값을 지운다. 없으면 아무 일도 하지 않는다.
- deleteSubKey(subKeyPath: string) -> void
  설명: 이 키 아래의 subKeyPath 하위 키를 지운다. 그 하위 키가 또 다른 하위
  키를 갖고 있으면 오류를 낸다 (재귀 삭제는 지원하지 않는다).
- close() -> void
  설명: 이 키에 대한 핸들을 닫는다. 더 이상 이 인스턴스를 쓰지 않는다.

# Interface

## Library

다른 패키지는 `RegistryKey.create(RegistryKey.HKEY_CURRENT_USER,
"Software\MyApp")`처럼 키를 얻은 뒤 `getValue`/`setValue`를 씁니다.

# Constraints

- Windows 네이티브 레지스트리 API(Win32 `RegOpenKeyEx`/`RegQueryValueEx`/
  `RegSetValueEx` 계열, 또는 C#의 `Microsoft.Win32.Registry`, Python의
  `winreg` 등 언어별 래퍼)에 매핑한다.
- 이 계약은 문자열(REG_SZ) 값만 다룬다 — DWORD, 이진 데이터 등 다른 레지스트리
  값 타입은 이 버전의 범위 밖이다.
- Windows가 아닌 타겟(Linux, macOS 등)으로 트랜스파일해야 하는 상황이면, 이
  패키지를 참조하는 코드는 성립할 수 없다 — AI는 4.5절(모호함 처리)에 따라
  사용자에게 알리고 대안(예: [`std/io/file`](../io/file.md) 기반 설정 파일)을
  제안합니다.

# Examples

## 예제: 쓰고 다시 읽기

호출 (순서대로):
```
key = RegistryKey.create(RegistryKey.HKEY_CURRENT_USER, "Software\MyApp")
key.setValue("Theme", "dark")
key.getValue("Theme")
```

기대 동작: 마지막 호출은 `"dark"`를 반환한다.

## 예제: 없는 값 읽기

호출: `key.getValue("존재하지않는값")`

기대 동작: `null`을 반환한다.

# Open Points

- 값 타입은 REG_SZ(문자열)만 다룬다 — DWORD/QWORD/이진 값, 레지스트리 변경
  감시(notification)는 다음 버전에서 다룬다.
- 32비트/64비트 레지스트리 뷰(WOW64) 구분은 이 버전의 범위 밖이다.
