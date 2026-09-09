#!/usr/bin/env bash
# tests/cpp의 모든 검증 프로그램을 컴파일하고 실행한다.
#
# 이 환경에서는 MSYS2의 기본 g++가 비정상 종료해서 LLVM clang++를 대신 쓴다
# (README.md 참조). 다른 환경이라면 CXX 환경 변수로 컴파일러를 바꿀 수 있다.
set -e
cd "$(dirname "$0")"

CXX="${CXX:-/c/Program Files/LLVM/bin/clang++.exe}"

for src in test_*.cpp; do
  exe="${src%.cpp}.exe"
  echo "== $src =="
  "$CXX" -std=c++17 -Wall -pthread -o "$exe" "$src"
  ./"$exe"
  rm -f "$exe"
  echo
done
