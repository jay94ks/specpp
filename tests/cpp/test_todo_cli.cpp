// examples/todo-cli.md 의 # Examples 섹션 + test_required 블록을 그대로 옮긴 테스트.
#include "minitest.hpp"
#include "todo_cli.hpp"

TEST(test_add_to_empty_list) {
    TodoApp app;
    Task& t = app.add("우유 사기");
    CHECK_EQ(formatAdd(t), std::string("✔ 추가됨: 우유 사기 (#1)"));
}

TEST(test_second_add_increments_id) {
    TodoApp app;
    app.add("우유 사기");
    Task& t = app.add("청소하기");
    CHECK_EQ(formatAdd(t), std::string("✔ 추가됨: 청소하기 (#2)"));
}

TEST(test_blank_title_fails) {
    TodoApp app;
    bool threw = false;
    try {
        app.add("   ");
    } catch (const ValidationError& e) {
        threw = true;
        CHECK_EQ(e.message, std::string("title은 필수입니다"));
    }
    CHECK(threw);
}

// SPEC.md 4.7절: specRef는 스펙 작성자가 적는 게 아니라 AI가 코드 생성
// 시점에 자동으로 채운다. 여기서는 그 결과를 검증한다.
TEST(test_blank_title_error_carries_specref) {
    TodoApp app;
    bool threw = false;
    try {
        app.add("   ");
    } catch (const ValidationError& e) {
        threw = true;
        CHECK(e.specRef.has_value());
        CHECK_EQ(*e.specRef, std::string("examples/todo-cli.md#Behavior.할 일 추가"));
    }
    CHECK(threw);
}

TEST(test_done_task_excluded_from_default_list) {
    TodoApp app;
    app.add("우유 사기");
    app.done(1);
    CHECK(app.list(false).empty());
}

TEST(test_all_flag_includes_done) {
    TodoApp app;
    app.add("우유 사기");
    app.done(1);
    auto all = app.list(true);
    CHECK_EQ(all.size(), size_t(1));
    CHECK_EQ(formatListLine(all[0]), std::string("[x] #1 우유 사기"));
}

TEST(test_done_missing_id_fails) {
    TodoApp app;
    bool threw = false;
    try {
        app.done(999);
    } catch (const NotFoundError& e) {
        threw = true;
        CHECK_EQ(e.message, std::string("Task #999를 찾을 수 없습니다"));
    }
    CHECK(threw);
}

TEST(test_done_missing_id_error_carries_specref) {
    TodoApp app;
    bool threw = false;
    try {
        app.done(999);
    } catch (const NotFoundError& e) {
        threw = true;
        CHECK(e.specRef.has_value());
        CHECK_EQ(*e.specRef, std::string("examples/todo-cli.md#Behavior.할 일 완료 처리"));
    }
    CHECK(threw);
}

// test_required Todo.Task: markDone()을 두 번 호출해도 예외 없이 done=true를 유지한다.
TEST(test_mark_done_twice_is_idempotent) {
    TodoApp app;
    app.add("우유 사기");
    app.done(1);
    app.done(1);
    auto all = app.list(true);
    CHECK(all[0].done);
}

TEST_MAIN()
