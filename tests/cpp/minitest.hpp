// 이 폴더 전체에서 쓰는 아주 작은 테스트 헬퍼. 외부 프레임워크(gtest 등) 없이
// g++만으로 컴파일·실행해서 SPEC.md 검증을 하기 위한 것이다.
#pragma once
#include <functional>
#include <iostream>
#include <string>
#include <vector>

struct TestCase {
    std::string name;
    std::function<void()> fn;
};

inline std::vector<TestCase>& registry() {
    static std::vector<TestCase> tests;
    return tests;
}

struct Registrar {
    Registrar(const std::string& name, std::function<void()> fn) {
        registry().push_back({name, std::move(fn)});
    }
};

#define TEST(name) \
    void name(); \
    static Registrar registrar_##name(#name, name); \
    void name()

#define CHECK(cond) \
    if (!(cond)) { \
        throw std::runtime_error(std::string("CHECK failed: ") + #cond + " at " + __FILE__ + ":" + std::to_string(__LINE__)); \
    }

#define CHECK_EQ(a, b) \
    if (!((a) == (b))) { \
        throw std::runtime_error(std::string("CHECK_EQ failed: ") + #a + " != " + #b + " at " + __FILE__ + ":" + std::to_string(__LINE__)); \
    }

inline int runAllTests() {
    int failed = 0;
    for (auto& t : registry()) {
        try {
            t.fn();
            std::cout << "ok   " << t.name << "\n";
        } catch (const std::exception& e) {
            std::cout << "FAIL " << t.name << " - " << e.what() << "\n";
            failed++;
        }
    }
    std::cout << "\n" << (registry().size() - failed) << "/" << registry().size() << " passed\n";
    return failed == 0 ? 0 : 1;
}

#define TEST_MAIN() int main() { return runAllTests(); }
