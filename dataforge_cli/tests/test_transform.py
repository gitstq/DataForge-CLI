"""
转换引擎测试模块
================
测试数据格式转换、JSON处理工具等功能。
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dataforge_cli.core.transform import TransformEngine


class TestJSONToYAML(unittest.TestCase):
    """JSON转YAML测试"""

    def test_simple_conversion(self) -> None:
        """测试简单JSON转YAML"""
        data = {"name": "Alice", "age": 25}
        result = TransformEngine.to_yaml(data)
        self.assertIn("name:", result)
        self.assertIn("Alice", result)
        self.assertIn("age:", result)
        self.assertIn("25", result)

    def test_nested_conversion(self) -> None:
        """测试嵌套结构转换"""
        data = {"parent": {"child": "value"}}
        result = TransformEngine.to_yaml(data)
        self.assertIn("parent:", result)
        self.assertIn("child:", result)


class TestJSONToCSV(unittest.TestCase):
    """JSON转CSV测试"""

    def test_simple_conversion(self) -> None:
        """测试简单JSON转CSV"""
        data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        result = TransformEngine.to_csv(data)
        self.assertIn("name,age", result)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)

    def test_single_dict(self) -> None:
        """测试单个字典转CSV"""
        data = {"name": "Alice", "age": 25}
        result = TransformEngine.to_csv(data)
        self.assertIn("name,age", result)


class TestJSONToTable(unittest.TestCase):
    """JSON转表格测试"""

    def test_simple_table(self) -> None:
        """测试简单表格生成"""
        data = [{"name": "Alice", "age": 25}]
        result = TransformEngine.to_table(data)
        self.assertIn("name", result)
        self.assertIn("age", result)
        self.assertIn("Alice", result)
        self.assertIn("25", result)


class TestBeautify(unittest.TestCase):
    """JSON美化测试"""

    def test_beautify(self) -> None:
        """测试JSON美化"""
        input_str = '{"name":"Alice","age":25}'
        result = TransformEngine.beautify(input_str)
        parsed = json.loads(result)
        self.assertEqual(parsed, {"name": "Alice", "age": 25})

    def test_minify(self) -> None:
        """测试JSON压缩"""
        input_str = '{\n  "name": "Alice",\n  "age": 25\n}'
        result = TransformEngine.minify(input_str)
        self.assertNotIn("\n", result)
        self.assertNotIn("  ", result)


class TestSortKeys(unittest.TestCase):
    """JSON键排序测试"""

    def test_sort_keys(self) -> None:
        """测试键名排序"""
        input_str = '{"zebra": 1, "apple": 2, "banana": 3}'
        result = TransformEngine.sort_keys(input_str)
        parsed = json.loads(result)
        keys = list(parsed.keys())
        self.assertEqual(keys, ["apple", "banana", "zebra"])


class TestFlatten(unittest.TestCase):
    """展平测试"""

    def test_flatten_simple(self) -> None:
        """测试简单展平"""
        data = {"a": {"b": {"c": 1}}}
        result = TransformEngine.flatten(data)
        self.assertEqual(result, {"a.b.c": 1})

    def test_flatten_mixed(self) -> None:
        """测试混合结构展平"""
        data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        result = TransformEngine.flatten(data)
        self.assertEqual(result["a"], 1)
        self.assertEqual(result["b.c"], 2)
        self.assertEqual(result["b.d.e"], 3)

    def test_flatten_custom_separator(self) -> None:
        """测试自定义分隔符展平"""
        data = {"a": {"b": 1}}
        result = TransformEngine.flatten(data, separator="/")
        self.assertEqual(result, {"a/b": 1})


class TestUnflatten(unittest.TestCase):
    """还原测试"""

    def test_unflatten_simple(self) -> None:
        """测试简单还原"""
        data = {"a.b.c": 1}
        result = TransformEngine.unflatten(data)
        self.assertEqual(result, {"a": {"b": {"c": 1}}})

    def test_flatten_unflatten_roundtrip(self) -> None:
        """测试展平-还原往返"""
        original = {"a": {"b": 1}, "c": {"d": {"e": 2}}, "f": 3}
        flattened = TransformEngine.flatten(original)
        unflattened = TransformEngine.unflatten(flattened)
        self.assertEqual(unflattened, original)


class TestStats(unittest.TestCase):
    """统计功能测试"""

    def test_dict_stats(self) -> None:
        """测试字典统计"""
        data = {"name": "Alice", "age": 25}
        stats = TransformEngine.stats(data)
        self.assertEqual(stats["type"], "dict")
        self.assertEqual(stats["key_count"], 2)

    def test_list_stats(self) -> None:
        """测试列表统计"""
        data = [1, 2, 3]
        stats = TransformEngine.stats(data)
        self.assertEqual(stats["type"], "list")
        self.assertEqual(stats["length"], 3)

    def test_string_stats(self) -> None:
        """测试字符串统计"""
        data = "hello"
        stats = TransformEngine.stats(data)
        self.assertEqual(stats["type"], "str")
        self.assertEqual(stats["length"], 5)


if __name__ == "__main__":
    unittest.main()
