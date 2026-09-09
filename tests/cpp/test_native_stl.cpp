// std/native/cpp/{memory,containers}.md 가 실제 STL API와 정확히 일치하는지
// 확인한다. 이 파일들은 kind: native(실체 명세)이므로 "구현"이 아니라 "이미
// 있는 것을 정확히 묘사했는가"를 검증하는 것이 목적이다.
#include "minitest.hpp"
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

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

TEST_MAIN()
