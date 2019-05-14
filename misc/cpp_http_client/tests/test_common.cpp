#include <gtest/gtest.h>
#include "common.h"

TEST(TestCommon, trim) {
    ASSERT_EQ(Trimmed("  abc  "), "abc");
    ASSERT_EQ(Trimmed("  abc"), "abc");
    ASSERT_EQ(Trimmed("abc  "), "abc");
    ASSERT_EQ(Trimmed("abc"), "abc");
    ASSERT_EQ(Trimmed(" abc "), "abc");
    ASSERT_EQ(Trimmed(" a b c "), "a b c");
    ASSERT_EQ(Trimmed(""), "");
    ASSERT_EQ(Trimmed(" "), "");
    ASSERT_EQ(Trimmed("    "), "");
    ASSERT_EQ(Trimmed("a"), "");
}

TEST(TestCommon, startsWith) {
    ASSERT_EQ(StartsWith("hello, world", "hello"), true);
    ASSERT_EQ(StartsWith("hello, world", "hAllo"), false);
    ASSERT_EQ(StartsWith("hello, world", ""), true);
    ASSERT_EQ(StartsWith("", ""), true);
    ASSERT_EQ(StartsWith("", "aaa"), false);
}
