#include "minitest.hpp"
#include "collections.hpp"

TEST(test_set_duplicate_add_is_ignored) {
    Set<std::string> s;
    s.add("a");
    s.add("a");
    CHECK_EQ(s.size(), 1);
}

TEST(test_set_isEmpty_inherited_default) {
    Set<std::string> s;
    CHECK(s.isEmpty());
    s.add("a");
    CHECK(!s.isEmpty());
}

TEST(test_queue_fifo_order) {
    Queue<std::string> q;
    q.enqueue("a");
    q.enqueue("b");
    CHECK_EQ(*q.dequeue(), std::string("a"));
    CHECK_EQ(*q.dequeue(), std::string("b"));
}

TEST(test_queue_dequeue_empty_returns_nullopt) {
    Queue<std::string> q;
    CHECK(!q.dequeue().has_value());
}

TEST(test_stack_lifo_order) {
    Stack<std::string> s;
    s.push("a");
    s.push("b");
    CHECK_EQ(*s.pop(), std::string("b"));
    CHECK_EQ(*s.pop(), std::string("a"));
}

TEST(test_dictionary_set_and_get) {
    Dictionary<std::string, int> d;
    d.set("a", 1);
    CHECK_EQ(*d.get("a"), 1);
    CHECK(!d.get("b").has_value());
}

TEST_MAIN()
