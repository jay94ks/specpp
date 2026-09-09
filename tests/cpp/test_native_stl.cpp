// std/native/cpp/{memory,containers,iostream}.md 가 실제 STL API와 정확히
// 일치하는지 확인한다. 이 파일들은 kind: native(실체 명세)이므로 "구현"이
// 아니라 "이미 있는 것을 정확히 묘사했는가"를 검증하는 것이 목적이다.
//
// containers.md/memory.md는 STL의 실제 이름(push_back, use_count 등)을 그대로
// 쓰므로 std:: 타입을 직접 두드려 검증한다. iostream.md는 SPP가 아직
// 연산자 오버로드(<<)를 표기할 방법이 없어서 write()/readLine()으로 근사한
// 우리 쪽 표기이므로(파일의 Open Points 참조), 그 근사가 실제 스트림 위에서
// 의도대로 동작하는지 작은 래퍼로 검증한다.
#include "minitest.hpp"
#include <memory>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

// std/native/cpp/iostream.md의 Ostream/Istream을 그대로 옮긴 참조 구현.
class Ostream {
    std::ostream& s_;

public:
    explicit Ostream(std::ostream& s) : s_(s) {}
    void write(const std::string& text) { s_ << text; }
    void flush() { s_.flush(); }
};

class Istream {
    std::istream& s_;

public:
    explicit Istream(std::istream& s) : s_(s) {}
    std::optional<std::string> readLine() {
        std::string line;
        if (std::getline(s_, line)) return line;
        return std::nullopt;
    }
};

TEST(test_vector_matches_spec) {
    std::vector<int> v;
    v.push_back(1);
    v.push_back(2);
    CHECK_EQ(v.size(), size_t(2));
    CHECK(!v.empty());
    CHECK_EQ(v.at(0), 1);
    v.pop_back();
    CHECK_EQ(v.size(), size_t(1));
    v.clear();
    CHECK(v.empty());
}

TEST(test_vector_at_throws_out_of_range) {
    std::vector<int> v;
    bool threw = false;
    try {
        v.at(0);
    } catch (const std::out_of_range&) {
        threw = true;
    }
    CHECK(threw);
}

TEST(test_unordered_map_matches_spec) {
    std::unordered_map<std::string, int> m;
    m.insert({"a", 1});
    CHECK_EQ(m.count("a"), size_t(1));
    CHECK_EQ(m.count("b"), size_t(0));
    CHECK_EQ(m.at("a"), 1);
    m.erase("a");
    CHECK_EQ(m.size(), size_t(0));
}

TEST(test_unique_ptr_matches_spec) {
    auto p = std::make_unique<int>(42);
    CHECK_EQ(*p.get(), 42);
    int* raw = p.release();
    CHECK(p.get() == nullptr);
    delete raw;
}

TEST(test_shared_ptr_matches_spec) {
    auto a = std::make_shared<int>(1);
    CHECK_EQ(a.use_count(), long(1));
    {
        std::shared_ptr<int> b = a;
        CHECK_EQ(a.use_count(), long(2));
    }
    CHECK_EQ(a.use_count(), long(1));
}

TEST(test_basic_string_matches_spec) {
    std::string s = "Hello";
    CHECK_EQ(s.length(), size_t(5));
    s.append(" World");
    CHECK_EQ(s, std::string("Hello World"));
    CHECK_EQ(s.substr(6, 5), std::string("World"));
    CHECK_EQ(std::string(s.c_str()), s);
}

TEST(test_ostream_write_matches_spec) {
    std::ostringstream buf;
    Ostream out(buf);
    out.write("Hello World");
    out.flush();
    CHECK_EQ(buf.str(), std::string("Hello World"));
}

TEST(test_istream_readline_matches_spec) {
    std::istringstream in("우유 사기\n");
    Istream stream(in);
    auto line = stream.readLine();
    CHECK(line.has_value());
    CHECK_EQ(*line, std::string("우유 사기"));
}

TEST(test_istream_readline_at_eof_returns_nullopt) {
    std::istringstream in("");
    Istream stream(in);
    CHECK(!stream.readLine().has_value());
}

TEST_MAIN()
