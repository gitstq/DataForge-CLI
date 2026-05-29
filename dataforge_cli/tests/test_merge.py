"""
合并引擎测试模块
================
测试深度合并、数组合并策略、冲突解决等功能。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dataforge_cli.core.merge import MergeEngine


class TestDeepMerge(unittest.TestCase):
    """深度合并测试"""

    def test_simple_merge(self) -> None:
        """测试简单合并"""
        base = {"a": 1}
        override = {"b": 2}
        result = MergeEngine.deep_merge(base, override)
        self.assertEqual(result, {"a": 1, "b": 2})

    def test_nested_merge(self) -> None:
        """测试嵌套合并"""
        base = {"a": {"b": 1}}
        override = {"a": {"c": 2}}
        result = MergeEngine.deep_merge(base, override)
        self.assertEqual(result, {"a": {"b": 1, "c": 2}})

    def test_override_value(self) -> None:
        """测试值覆盖"""
        base = {"key": "old_value"}
        override = {"key": "new_value"}
        result = MergeEngine.deep_merge(base, override)
        self.assertEqual(result["key"], "new_value")

    def test_none_override(self) -> None:
        """测试None覆盖"""
        base = {"key": "value"}
        result = MergeEngine.deep_merge(base, None)
        self.assertEqual(result, {"key": "value"})

    def test_none_base(self) -> None:
        """测试None基础"""
        override = {"key": "value"}
        result = MergeEngine.deep_merge(None, override)
        self.assertEqual(result, {"key": "value"})


class TestArrayStrategy(unittest.TestCase):
    """数组合并策略测试"""

    def test_replace_strategy(self) -> None:
        """测试替换策略"""
        base = {"items": [1, 2, 3]}
        override = {"items": [4, 5]}
        result = MergeEngine.deep_merge(base, override, array_strategy="replace")
        self.assertEqual(result["items"], [4, 5])

    def test_append_strategy(self) -> None:
        """测试追加策略"""
        base = {"items": [1, 2]}
        override = {"items": [3, 4]}
        result = MergeEngine.deep_merge(base, override, array_strategy="append")
        self.assertEqual(result["items"], [1, 2, 3, 4])

    def test_prepend_strategy(self) -> None:
        """测试前置策略"""
        base = {"items": [1, 2]}
        override = {"items": [3, 4]}
        result = MergeEngine.deep_merge(base, override, array_strategy="prepend")
        self.assertEqual(result["items"], [3, 4, 1, 2])

    def test_merge_by_key_strategy(self) -> None:
        """测试按键合并策略"""
        base = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
        override = {"users": [{"id": 1, "age": 25}]}
        result = MergeEngine.deep_merge(base, override, array_strategy="merge-by-key")
        self.assertEqual(len(result["users"]), 2)
        self.assertEqual(result["users"][0]["id"], 1)
        self.assertEqual(result["users"][0]["name"], "Alice")
        self.assertEqual(result["users"][0]["age"], 25)


class TestConflictResolution(unittest.TestCase):
    """冲突解决测试"""

    def test_ours_strategy(self) -> None:
        """测试保留基础值策略"""
        base = {"key": "base_value"}
        override = {"key": "override_value"}
        result = MergeEngine.deep_merge(base, override, conflict="ours")
        self.assertEqual(result["key"], "base_value")

    def test_theirs_strategy(self) -> None:
        """测试使用覆盖值策略"""
        base = {"key": "base_value"}
        override = {"key": "override_value"}
        result = MergeEngine.deep_merge(base, override, conflict="theirs")
        self.assertEqual(result["key"], "override_value")

    def test_manual_strategy(self) -> None:
        """测试手动冲突策略"""
        base = {"key": "base_value"}
        override = {"key": "override_value"}
        result = MergeEngine.deep_merge(base, override, conflict="manual")
        self.assertIn("__conflict", result["key"])
        self.assertEqual(result["key"]["__base"], "base_value")
        self.assertEqual(result["key"]["__override"], "override_value")

    def test_error_strategy(self) -> None:
        """测试错误冲突策略"""
        base = {"key": "base_value"}
        override = {"key": "override_value"}
        with self.assertRaises(ValueError):
            MergeEngine.deep_merge(base, override, conflict="error")

    def test_no_conflict_same_value(self) -> None:
        """测试相同值无冲突"""
        base = {"key": "same_value"}
        override = {"key": "same_value"}
        result = MergeEngine.deep_merge(base, override, conflict="error")
        self.assertEqual(result["key"], "same_value")


class TestPreviewMerge(unittest.TestCase):
    """合并预览测试"""

    def test_preview_merge(self) -> None:
        """测试合并预览"""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        preview = MergeEngine.preview_merge(base, override)

        self.assertIn("result", preview)
        self.assertIn("conflicts", preview)
        self.assertIn("changes", preview)
        self.assertEqual(preview["changes"]["added"], 1)  # c
        self.assertEqual(preview["changes"]["modified"], 1)  # b


class TestInvalidStrategy(unittest.TestCase):
    """无效策略测试"""

    def test_invalid_array_strategy(self) -> None:
        """测试无效的数组合并策略"""
        with self.assertRaises(ValueError):
            MergeEngine.deep_merge({}, {}, array_strategy="invalid")

    def test_invalid_conflict_strategy(self) -> None:
        """测试无效的冲突策略"""
        with self.assertRaises(ValueError):
            MergeEngine.deep_merge({}, {}, conflict="invalid")


if __name__ == "__main__":
    unittest.main()
