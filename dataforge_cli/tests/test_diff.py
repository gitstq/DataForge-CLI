"""
差异对比引擎测试模块
====================
测试递归对比、JSON Patch生成等功能。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dataforge_cli.core.diff import DiffEngine


class TestBasicDiff(unittest.TestCase):
    """基本差异对比测试"""

    def test_identical_data(self) -> None:
        """测试相同数据"""
        data = {"key": "value"}
        result = DiffEngine.diff(data, data)
        self.assertTrue(result["is_equal"])
        self.assertEqual(len(result["added"]), 0)
        self.assertEqual(len(result["removed"]), 0)
        self.assertEqual(len(result["modified"]), 0)

    def test_added_key(self) -> None:
        """测试新增键"""
        old = {"a": 1}
        new = {"a": 1, "b": 2}
        result = DiffEngine.diff(old, new)
        self.assertFalse(result["is_equal"])
        self.assertEqual(len(result["added"]), 1)
        self.assertEqual(result["added"][0]["path"], "b")

    def test_removed_key(self) -> None:
        """测试删除键"""
        old = {"a": 1, "b": 2}
        new = {"a": 1}
        result = DiffEngine.diff(old, new)
        self.assertFalse(result["is_equal"])
        self.assertEqual(len(result["removed"]), 1)
        self.assertEqual(result["removed"][0]["path"], "b")

    def test_modified_value(self) -> None:
        """测试修改值"""
        old = {"key": "old_value"}
        new = {"key": "new_value"}
        result = DiffEngine.diff(old, new)
        self.assertFalse(result["is_equal"])
        self.assertEqual(len(result["modified"]), 1)
        self.assertEqual(result["modified"][0]["path"], "key")
        self.assertEqual(result["modified"][0]["old"], "old_value")
        self.assertEqual(result["modified"][0]["new"], "new_value")

    def test_nested_diff(self) -> None:
        """测试嵌套差异"""
        old = {"a": {"b": 1, "c": 2}}
        new = {"a": {"b": 1, "c": 3}}
        result = DiffEngine.diff(old, new)
        self.assertFalse(result["is_equal"])
        self.assertEqual(len(result["modified"]), 1)
        self.assertEqual(result["modified"][0]["path"], "a.c")


class TestArrayDiff(unittest.TestCase):
    """数组差异测试"""

    def test_array_added_item(self) -> None:
        """测试数组新增元素"""
        old = {"items": [1, 2]}
        new = {"items": [1, 2, 3]}
        result = DiffEngine.diff(old, new)
        self.assertEqual(len(result["added"]), 1)
        self.assertEqual(result["added"][0]["path"], "items[2]")

    def test_array_removed_item(self) -> None:
        """测试数组删除元素"""
        old = {"items": [1, 2, 3]}
        new = {"items": [1, 2]}
        result = DiffEngine.diff(old, new)
        self.assertEqual(len(result["removed"]), 1)

    def test_array_modified_item(self) -> None:
        """测试数组修改元素"""
        old = {"items": [1, 2, 3]}
        new = {"items": [1, 5, 3]}
        result = DiffEngine.diff(old, new)
        self.assertEqual(len(result["modified"]), 1)
        self.assertEqual(result["modified"][0]["path"], "items[1]")


class TestIgnorePaths(unittest.TestCase):
    """忽略路径测试"""

    def test_ignore_single_path(self) -> None:
        """测试忽略单个路径"""
        old = {"a": 1, "b": 2}
        new = {"a": 1, "b": 3}
        result = DiffEngine.diff(old, new, ignore_paths=["b"])
        self.assertTrue(result["is_equal"])

    def test_ignore_wildcard(self) -> None:
        """测试忽略通配符路径"""
        old = {"meta": {"timestamp": "old"}, "data": {"value": 1}}
        new = {"meta": {"timestamp": "new"}, "data": {"value": 1}}
        result = DiffEngine.diff(old, new, ignore_paths=["meta.*"])
        self.assertTrue(result["is_equal"])


class TestDiffOutput(unittest.TestCase):
    """差异输出测试"""

    def test_diff_summary(self) -> None:
        """测试差异摘要"""
        old = {"a": 1}
        new = {"a": 2, "b": 3}
        result = DiffEngine.diff(old, new)
        summary = DiffEngine.diff_summary(result)
        self.assertIn("新增", summary)
        self.assertIn("修改", summary)

    def test_diff_detail(self) -> None:
        """测试差异详情"""
        old = {"a": 1}
        new = {"a": 2}
        result = DiffEngine.diff(old, new)
        detail = DiffEngine.diff_detail(result)
        self.assertIn("~", detail)


class TestJSONPatch(unittest.TestCase):
    """JSON Patch测试"""

    def test_add_operation(self) -> None:
        """测试add操作"""
        old = {"a": 1}
        new = {"a": 1, "b": 2}
        patches = DiffEngine.json_patch(old, new)
        add_ops = [p for p in patches if p["op"] == "add"]
        self.assertEqual(len(add_ops), 1)
        self.assertEqual(add_ops[0]["path"], "/b")
        self.assertEqual(add_ops[0]["value"], 2)

    def test_remove_operation(self) -> None:
        """测试remove操作"""
        old = {"a": 1, "b": 2}
        new = {"a": 1}
        patches = DiffEngine.json_patch(old, new)
        remove_ops = [p for p in patches if p["op"] == "remove"]
        self.assertEqual(len(remove_ops), 1)

    def test_replace_operation(self) -> None:
        """测试replace操作"""
        old = {"a": 1}
        new = {"a": 2}
        patches = DiffEngine.json_patch(old, new)
        replace_ops = [p for p in patches if p["op"] == "replace"]
        self.assertEqual(len(replace_ops), 1)
        self.assertEqual(replace_ops[0]["value"], 2)

    def test_apply_patch(self) -> None:
        """测试应用补丁"""
        data = {"a": 1}
        patches = [{"op": "add", "path": "/b", "value": 2}]
        result = DiffEngine.apply_patch(data, patches)
        self.assertEqual(result, {"a": 1, "b": 2})


class TestTypeChange(unittest.TestCase):
    """类型变更测试"""

    def test_type_change(self) -> None:
        """测试类型变更检测"""
        old = {"value": "123"}
        new = {"value": 123}
        result = DiffEngine.diff(old, new)
        self.assertFalse(result["is_equal"])
        self.assertEqual(len(result["modified"]), 1)
        self.assertEqual(result["modified"][0]["type"], "type_change")


if __name__ == "__main__":
    unittest.main()
