"""
数据解析器测试模块
==================
测试JSON、YAML、TOML、CSV解析器的功能。
"""

import json
import os
import sys
import unittest

# 确保能导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dataforge_cli.core.parser import Parser


class TestJSONParser(unittest.TestCase):
    """JSON解析器测试"""

    def test_parse_simple_object(self) -> None:
        """测试简单JSON对象解析"""
        result = Parser.parse('{"key": "value"}', format="json")
        self.assertEqual(result, {"key": "value"})

    def test_parse_nested_object(self) -> None:
        """测试嵌套JSON对象解析"""
        text = '{"a": {"b": {"c": 1}}}'
        result = Parser.parse(text, format="json")
        self.assertEqual(result, {"a": {"b": {"c": 1}}})

    def test_parse_array(self) -> None:
        """测试JSON数组解析"""
        result = Parser.parse('[1, 2, 3]', format="json")
        self.assertEqual(result, [1, 2, 3])

    def test_parse_mixed_types(self) -> None:
        """测试混合类型JSON解析"""
        text = '{"str": "hello", "num": 42, "bool": true, "null": null}'
        result = Parser.parse(text, format="json")
        self.assertEqual(result["str"], "hello")
        self.assertEqual(result["num"], 42)
        self.assertTrue(result["bool"])
        self.assertIsNone(result["null"])

    def test_parse_error(self) -> None:
        """测试JSON解析错误"""
        with self.assertRaises(ValueError):
            Parser.parse('{"invalid": }', format="json")

    def test_serialize_json(self) -> None:
        """测试JSON序列化"""
        result = Parser.serialize({"key": "value"}, format="json")
        parsed = json.loads(result)
        self.assertEqual(parsed, {"key": "value"})


class TestYAMLParser(unittest.TestCase):
    """YAML解析器测试"""

    def test_parse_simple_mapping(self) -> None:
        """测试简单YAML映射"""
        text = "key: value"
        result = Parser.parse(text, format="yaml")
        self.assertEqual(result, {"key": "value"})

    def test_parse_nested_mapping(self) -> None:
        """测试嵌套YAML映射"""
        text = "parent:\n  child: value"
        result = Parser.parse(text, format="yaml")
        self.assertEqual(result, {"parent": {"child": "value"}})

    def test_parse_sequence(self) -> None:
        """测试YAML序列"""
        text = "items:\n  - apple\n  - banana\n  - cherry"
        result = Parser.parse(text, format="yaml")
        self.assertEqual(result["items"], ["apple", "banana", "cherry"])

    def test_parse_scalar_types(self) -> None:
        """测试YAML标量类型"""
        text = "integer: 42\nfloat: 3.14\nbool_true: true\nbool_false: false\nnull_val: null"
        result = Parser.parse(text, format="yaml")
        self.assertEqual(result["integer"], 42)
        self.assertEqual(result["float"], 3.14)
        self.assertTrue(result["bool_true"])
        self.assertFalse(result["bool_false"])
        self.assertIsNone(result["null_val"])

    def test_parse_comments(self) -> None:
        """测试YAML注释"""
        text = "key: value # 这是注释"
        result = Parser.parse(text, format="yaml")
        self.assertEqual(result, {"key": "value"})

    def test_parse_flow_sequence(self) -> None:
        """测试YAML流式序列"""
        text = "items: [a, b, c]"
        result = Parser.parse(text, format="yaml")
        self.assertEqual(result["items"], ["a", "b", "c"])

    def test_parse_flow_mapping(self) -> None:
        """测试YAML流式映射"""
        text = "data: {name: Alice, age: 25}"
        result = Parser.parse(text, format="yaml")
        self.assertEqual(result["data"]["name"], "Alice")
        self.assertEqual(result["data"]["age"], 25)

    def test_serialize_yaml(self) -> None:
        """测试YAML序列化"""
        data = {"name": "Alice", "items": [1, 2, 3]}
        result = Parser.serialize_yaml(data)
        self.assertIn("name:", result)
        self.assertIn("Alice", result)

    def test_parse_quoted_string(self) -> None:
        """测试YAML引号字符串"""
        text = 'key: "value with spaces"'
        result = Parser.parse(text, format="yaml")
        self.assertEqual(result, {"key": "value with spaces"})


class TestTOMLParser(unittest.TestCase):
    """TOML解析器测试"""

    def test_parse_simple_key_value(self) -> None:
        """测试简单TOML键值对"""
        text = 'key = "value"'
        result = Parser.parse(text, format="toml")
        self.assertEqual(result, {"key": "value"})

    def test_parse_integer(self) -> None:
        """测试TOML整数"""
        text = "port = 8080"
        result = Parser.parse(text, format="toml")
        self.assertEqual(result, {"port": 8080})

    def test_parse_float(self) -> None:
        """测试TOML浮点数"""
        text = "pi = 3.14"
        result = Parser.parse(text, format="toml")
        self.assertEqual(result["pi"], 3.14)

    def test_parse_boolean(self) -> None:
        """测试TOML布尔值"""
        text = "debug = true\nverbose = false"
        result = Parser.parse(text, format="toml")
        self.assertTrue(result["debug"])
        self.assertFalse(result["verbose"])

    def test_parse_section(self) -> None:
        """测试TOML表"""
        text = '[server]\nhost = "localhost"\nport = 8080'
        result = Parser.parse(text, format="toml")
        self.assertEqual(result["server"]["host"], "localhost")
        self.assertEqual(result["server"]["port"], 8080)

    def test_parse_nested_section(self) -> None:
        """测试TOML嵌套表"""
        text = '[server.database]\nhost = "localhost"\nport = 5432'
        result = Parser.parse(text, format="toml")
        self.assertEqual(result["server"]["database"]["host"], "localhost")

    def test_parse_array(self) -> None:
        """测试TOML数组"""
        text = 'ports = [8080, 8081, 8082]'
        result = Parser.parse(text, format="toml")
        self.assertEqual(result["ports"], [8080, 8081, 8082])

    def test_parse_comments(self) -> None:
        """测试TOML注释"""
        text = 'key = "value" # 注释'
        result = Parser.parse(text, format="toml")
        self.assertEqual(result, {"key": "value"})

    def test_serialize_toml(self) -> None:
        """测试TOML序列化"""
        data = {"name": "test", "server": {"port": 8080}}
        result = Parser.serialize_toml(data)
        self.assertIn("name", result)
        self.assertIn("[server]", result)


class TestCSVParser(unittest.TestCase):
    """CSV解析器测试"""

    def test_parse_simple_csv(self) -> None:
        """测试简单CSV解析"""
        text = "name,age\nAlice,25\nBob,30"
        result = Parser.parse_csv(text)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Alice")
        self.assertEqual(result[0]["age"], "25")

    def test_parse_csv_no_header(self) -> None:
        """测试无表头CSV解析"""
        text = "Alice,25\nBob,30"
        result = Parser.parse_csv(text, has_header=False)
        self.assertEqual(result[0]["col_0"], "Alice")

    def test_serialize_csv(self) -> None:
        """测试CSV序列化"""
        data = [{"name": "Alice", "age": 25}]
        result = Parser.serialize_csv(data)
        self.assertIn("name,age", result)
        self.assertIn("Alice", result)


class TestFormatDetection(unittest.TestCase):
    """格式自动检测测试"""

    def test_detect_json(self) -> None:
        """测试JSON格式检测"""
        self.assertEqual(Parser.detect_format('{"key": "value"}'), "json")

    def test_detect_json_array(self) -> None:
        """测试JSON数组格式检测"""
        self.assertEqual(Parser.detect_format('[1, 2, 3]'), "json")

    def test_detect_toml(self) -> None:
        """测试TOML格式检测"""
        self.assertEqual(Parser.detect_format('[section]\nkey = "value"'), "toml")

    def test_detect_csv(self) -> None:
        """测试CSV格式检测"""
        text = "name,age\nAlice,25\nBob,30"
        self.assertEqual(Parser.detect_format(text), "csv")


if __name__ == "__main__":
    unittest.main()
