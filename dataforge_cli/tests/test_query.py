"""
查询引擎测试模块
================
测试JMESPath风格查询引擎的功能。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dataforge_cli.core.query import QueryEngine


class TestDotAccess(unittest.TestCase):
    """点号访问测试"""

    def test_simple_dot_access(self) -> None:
        """测试简单点号访问"""
        data = {"name": "Alice"}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("name"), "Alice")

    def test_nested_dot_access(self) -> None:
        """测试嵌套点号访问"""
        data = {"user": {"profile": {"name": "Alice"}}}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("user.profile.name"), "Alice")

    def test_missing_key(self) -> None:
        """测试访问不存在的键"""
        data = {"name": "Alice"}
        engine = QueryEngine(data)
        self.assertIsNone(engine.query("age"))


class TestArrayIndex(unittest.TestCase):
    """数组索引测试"""

    def test_positive_index(self) -> None:
        """测试正数索引"""
        data = {"items": ["a", "b", "c"]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("items[0]"), "a")
        self.assertEqual(engine.query("items[2]"), "c")

    def test_negative_index(self) -> None:
        """测试负数索引"""
        data = {"items": ["a", "b", "c"]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("items[-1]"), "c")

    def test_nested_array_index(self) -> None:
        """测试嵌套数组索引"""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("users[0].name"), "Alice")
        self.assertEqual(engine.query("users[1].name"), "Bob")


class TestArraySlice(unittest.TestCase):
    """数组切片测试"""

    def test_simple_slice(self) -> None:
        """测试简单切片"""
        data = {"items": [0, 1, 2, 3, 4]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("items[0:3]"), [0, 1, 2])

    def test_open_end_slice(self) -> None:
        """测试开放式切片"""
        data = {"items": [0, 1, 2, 3, 4]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("items[2:]"), [2, 3, 4])

    def test_open_start_slice(self) -> None:
        """测试从开头切片"""
        data = {"items": [0, 1, 2, 3, 4]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("items[:3]"), [0, 1, 2])


class TestWildcard(unittest.TestCase):
    """通配符测试"""

    def test_array_wildcard(self) -> None:
        """测试数组通配符"""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        engine = QueryEngine(data)
        result = engine.query("users[*].name")
        self.assertEqual(result, ["Alice", "Bob"])

    def test_dict_wildcard(self) -> None:
        """测试字典通配符"""
        data = {"user": {"a": 1, "b": 2, "c": 3}}
        engine = QueryEngine(data)
        result = engine.query("user.*")
        self.assertEqual(sorted(result), [1, 2, 3])


class TestFilter(unittest.TestCase):
    """过滤器测试"""

    def test_greater_than(self) -> None:
        """测试大于过滤器"""
        data = {"users": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 18}]}
        engine = QueryEngine(data)
        result = engine.query("users[?age > 18]")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

    def test_equal_filter(self) -> None:
        """测试等于过滤器"""
        data = {"users": [{"name": "Alice", "role": "admin"}, {"name": "Bob", "role": "user"}]}
        engine = QueryEngine(data)
        result = engine.query('users[?role == "admin"]')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

    def test_less_than(self) -> None:
        """测试小于过滤器"""
        data = {"items": [{"val": 1}, {"val": 5}, {"val": 3}, {"val": 8}, {"val": 2}]}
        engine = QueryEngine(data)
        result = engine.query("items[?val < 4]")
        self.assertEqual(len(result), 3)


class TestPipe(unittest.TestCase):
    """管道操作测试"""

    def test_simple_pipe(self) -> None:
        """测试简单管道"""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        engine = QueryEngine(data)
        result = engine.query("users | [0].name")
        self.assertEqual(result, "Alice")


class TestAggregate(unittest.TestCase):
    """聚合函数测试"""

    def test_length(self) -> None:
        """测试length函数"""
        data = {"items": [1, 2, 3, 4, 5]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("length(items)"), 5)

    def test_sum(self) -> None:
        """测试sum函数"""
        data = {"nums": [1, 2, 3, 4, 5]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("sum(nums)"), 15)

    def test_max(self) -> None:
        """测试max函数"""
        data = {"nums": [1, 5, 3, 8, 2]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("max(nums)"), 8)

    def test_min(self) -> None:
        """测试min函数"""
        data = {"nums": [1, 5, 3, 8, 2]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("min(nums)"), 1)

    def test_first(self) -> None:
        """测试first函数"""
        data = {"items": ["a", "b", "c"]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("first(items)"), "a")

    def test_last(self) -> None:
        """测试last函数"""
        data = {"items": ["a", "b", "c"]}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("last(items)"), "c")

    def test_keys(self) -> None:
        """测试keys函数"""
        data = {"user": {"name": "Alice", "age": 25}}
        engine = QueryEngine(data)
        result = engine.query("keys(user)")
        self.assertIn("name", result)
        self.assertIn("age", result)


class TestSortBy(unittest.TestCase):
    """排序函数测试"""

    def test_sort_by_ascending(self) -> None:
        """测试升序排序"""
        data = {"users": [{"name": "Bob", "age": 25}, {"name": "Alice", "age": 18}]}
        engine = QueryEngine(data)
        result = engine.query("sort_by(users, age)")
        self.assertEqual(result[0]["name"], "Alice")
        self.assertEqual(result[1]["name"], "Bob")


class TestEmptyInput(unittest.TestCase):
    """空输入测试"""

    def test_empty_expression(self) -> None:
        """测试空表达式"""
        data = {"key": "value"}
        engine = QueryEngine(data)
        self.assertEqual(engine.query(""), data)

    def test_root_access(self) -> None:
        """测试根访问"""
        data = {"key": "value"}
        engine = QueryEngine(data)
        self.assertEqual(engine.query("."), data)


if __name__ == "__main__":
    unittest.main()
