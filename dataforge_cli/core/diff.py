"""
差异对比引擎模块
==================
递归对比两个JSON/YAML对象，输出添加/删除/修改的路径。
支持颜色高亮差异、JSON Patch格式输出和忽略路径模式。

使用示例:
    from dataforge_cli.core.diff import DiffEngine

    # 基本对比
    result = DiffEngine.diff(
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30, "city": "Beijing"}
    )
    # 结果包含添加、删除、修改的信息

    # JSON Patch格式
    patches = DiffEngine.json_patch(old_data, new_data)

    # 彩色输出
    print(DiffEngine.diff_colorized(old_data, new_data))
"""

import copy
import json
from typing import Any, Dict, List, Optional, Tuple


class DiffEngine:
    """差异对比引擎

    递归对比两个数据结构，生成详细的差异报告。
    """

    @staticmethod
    def diff(old_data: Any, new_data: Any, ignore_paths: Optional[List[str]] = None,
             path: str = "") -> Dict[str, Any]:
        """对比两个数据对象

        Args:
            old_data: 旧数据
            new_data: 新数据
            ignore_paths: 要忽略的路径列表（支持通配符*）
            path: 当前路径（内部递归使用）

        Returns:
            差异结果字典，包含:
            - "added": 新增的路径和值
            - "removed": 删除的路径和值
            - "modified": 修改的路径及新旧值
            - "unchanged": 未变更的路径数
            - "is_equal": 是否完全相同
        """
        if ignore_paths is None:
            ignore_paths = []

        result: Dict[str, Any] = {
            "added": [],
            "removed": [],
            "modified": [],
            "unchanged": 0,
            "is_equal": True,
        }

        DiffEngine._diff_recursive(old_data, new_data, path, ignore_paths, result)

        result["is_equal"] = (
            len(result["added"]) == 0 and
            len(result["removed"]) == 0 and
            len(result["modified"]) == 0
        )

        return result

    @staticmethod
    def _diff_recursive(old_data: Any, new_data: Any, path: str,
                         ignore_paths: List[str], result: Dict[str, Any]) -> None:
        """递归对比数据

        Args:
            old_data: 旧数据
            new_data: 新数据
            path: 当前路径
            ignore_paths: 忽略路径列表
            result: 结果累积字典
        """
        # 检查是否在忽略路径中
        if DiffEngine._should_ignore(path, ignore_paths):
            return

        # 两者都为None或相等
        if old_data == new_data:
            result["unchanged"] += 1
            return

        # 类型不同
        if type(old_data) != type(new_data):
            result["modified"].append({
                "path": path or "$",
                "old": old_data,
                "new": new_data,
                "type": "type_change",
            })
            return

        # 两个都是字典
        if isinstance(old_data, dict) and isinstance(new_data, dict):
            all_keys = set(list(old_data.keys()) + list(new_data.keys()))

            for key in sorted(all_keys):
                new_path = f"{path}.{key}" if path else key

                if key not in old_data:
                    # 新增键
                    result["added"].append({
                        "path": new_path,
                        "value": new_data[key],
                    })
                elif key not in new_data:
                    # 删除键
                    result["removed"].append({
                        "path": new_path,
                        "value": old_data[key],
                    })
                else:
                    # 递归对比值
                    DiffEngine._diff_recursive(
                        old_data[key], new_data[key], new_path, ignore_paths, result
                    )
            return

        # 两个都是列表
        if isinstance(old_data, list) and isinstance(new_data, list):
            max_len = max(len(old_data), len(new_data))

            for i in range(max_len):
                new_path = f"{path}[{i}]"

                if i >= len(old_data):
                    # 新增元素
                    result["added"].append({
                        "path": new_path,
                        "value": new_data[i],
                    })
                elif i >= len(new_data):
                    # 删除元素
                    result["removed"].append({
                        "path": new_path,
                        "value": old_data[i],
                    })
                else:
                    # 递归对比元素
                    DiffEngine._diff_recursive(
                        old_data[i], new_data[i], new_path, ignore_paths, result
                    )
            return

        # 标量值不同
        result["modified"].append({
            "path": path or "$",
            "old": old_data,
            "new": new_data,
            "type": "value_change",
        })

    @staticmethod
    def _should_ignore(path: str, ignore_paths: List[str]) -> bool:
        """检查路径是否应该被忽略

        Args:
            path: 当前路径
            ignore_paths: 忽略路径模式列表

        Returns:
            是否应该忽略
        """
        for pattern in ignore_paths:
            # 支持通配符匹配
            if "*" in pattern:
                regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
                import re
                if re.match(f"^{regex_pattern}$", path):
                    return True
            elif path == pattern or path.startswith(pattern + ".") or path.startswith(pattern + "["):
                return True
        return False

    @staticmethod
    def diff_summary(diff_result: Dict[str, Any]) -> str:
        """生成差异摘要文本

        Args:
            diff_result: diff()方法返回的结果

        Returns:
            差异摘要字符串
        """
        added_count = len(diff_result.get("added", []))
        removed_count = len(diff_result.get("removed", []))
        modified_count = len(diff_result.get("modified", []))
        unchanged_count = diff_result.get("unchanged", 0)

        lines = [
            f"差异摘要:",
            f"  新增: {added_count} 项",
            f"  删除: {removed_count} 项",
            f"  修改: {modified_count} 项",
            f"  未变: {unchanged_count} 项",
        ]

        if diff_result.get("is_equal"):
            lines.append("  结论: 数据完全相同")
        else:
            total = added_count + removed_count + modified_count
            lines.append(f"  结论: 共 {total} 处差异")

        return "\n".join(lines)

    @staticmethod
    def diff_detail(diff_result: Dict[str, Any], max_value_length: int = 100) -> str:
        """生成详细的差异报告文本

        Args:
            diff_result: diff()方法返回的结果
            max_value_length: 值的最大显示长度

        Returns:
            详细差异报告字符串
        """
        lines: List[str] = []

        # 新增项
        for item in diff_result.get("added", []):
            val_str = DiffEngine._truncate(json.dumps(item["value"], ensure_ascii=False, default=str), max_value_length)
            lines.append(f"+ {item['path']}: {val_str}")

        # 删除项
        for item in diff_result.get("removed", []):
            val_str = DiffEngine._truncate(json.dumps(item["value"], ensure_ascii=False, default=str), max_value_length)
            lines.append(f"- {item['path']}: {val_str}")

        # 修改项
        for item in diff_result.get("modified", []):
            old_str = DiffEngine._truncate(json.dumps(item["old"], ensure_ascii=False, default=str), max_value_length)
            new_str = DiffEngine._truncate(json.dumps(item["new"], ensure_ascii=False, default=str), max_value_length)
            lines.append(f"~ {item['path']}:")
            lines.append(f"  旧值: {old_str}")
            lines.append(f"  新值: {new_str}")

        return "\n".join(lines)

    @staticmethod
    def diff_colorized(diff_result: Dict[str, Any],
                       max_value_length: int = 100) -> str:
        """生成带颜色的差异报告

        Args:
            diff_result: diff()方法返回的结果
            max_value_length: 值的最大显示长度

        Returns:
            带ANSI颜色代码的差异报告字符串
        """
        from dataforge_cli.utils.colors import Colors

        lines: List[str] = []

        # 新增项（绿色）
        for item in diff_result.get("added", []):
            val_str = DiffEngine._truncate(json.dumps(item["value"], ensure_ascii=False, default=str), max_value_length)
            lines.append(f"{Colors.green('+')} {Colors.green(item['path'])}: {Colors.green(val_str)}")

        # 删除项（红色）
        for item in diff_result.get("removed", []):
            val_str = DiffEngine._truncate(json.dumps(item["value"], ensure_ascii=False, default=str), max_value_length)
            lines.append(f"{Colors.red('-')} {Colors.red(item['path'])}: {Colors.red(val_str)}")

        # 修改项（黄色）
        for item in diff_result.get("modified", []):
            old_str = DiffEngine._truncate(json.dumps(item["old"], ensure_ascii=False, default=str), max_value_length)
            new_str = DiffEngine._truncate(json.dumps(item["new"], ensure_ascii=False, default=str), max_value_length)
            lines.append(f"{Colors.yellow('~')} {Colors.yellow(item['path'])}:")
            lines.append(f"  {Colors.red('旧值')}: {old_str}")
            lines.append(f"  {Colors.green('新值')}: {new_str}")

        return "\n".join(lines)

    @staticmethod
    def json_patch(old_data: Any, new_data: Any) -> List[Dict[str, Any]]:
        """生成JSON Patch格式的差异

        遵循 RFC 6902 (JSON Patch) 标准。

        Args:
            old_data: 旧数据
            new_data: 新数据

        Returns:
            JSON Patch操作列表
        """
        patches: List[Dict[str, Any]] = []
        DiffEngine._generate_patch_recursive(old_data, new_data, "", patches)
        return patches

    @staticmethod
    def _generate_patch_recursive(old_data: Any, new_data: Any, path: str,
                                  patches: List[Dict[str, Any]]) -> None:
        """递归生成JSON Patch

        Args:
            old_data: 旧数据
            new_data: 新数据
            path: 当前JSON指针路径
            patches: 补丁列表（累积）
        """
        json_pointer = "/" + path.replace(".", "/").replace("[", "/").replace("]", "") if path else ""

        if old_data == new_data:
            return

        if type(old_data) != type(new_data):
            patches.append({"op": "replace", "path": json_pointer, "value": new_data})
            return

        if isinstance(old_data, dict) and isinstance(new_data, dict):
            # 处理删除的键
            for key in old_data:
                if key not in new_data:
                    patches.append({"op": "remove", "path": json_pointer + "/" + key})

            # 处理新增和修改的键
            for key in new_data:
                new_pointer = json_pointer + "/" + key
                if key not in old_data:
                    patches.append({"op": "add", "path": new_pointer, "value": new_data[key]})
                else:
                    DiffEngine._generate_patch_recursive(
                        old_data[key], new_data[key], f"{path}.{key}" if path else key, patches
                    )
            return

        if isinstance(old_data, list) and isinstance(new_data, list):
            # 对于列表，简单处理：如果长度或内容不同则替换
            if old_data != new_data:
                patches.append({"op": "replace", "path": json_pointer, "value": new_data})
            return

        # 标量值不同
        patches.append({"op": "replace", "path": json_pointer, "value": new_data})

    @staticmethod
    def _truncate(text: str, max_length: int) -> str:
        """截断文本到指定长度

        Args:
            text: 输入文本
            max_length: 最大长度

        Returns:
            截断后的文本
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    @staticmethod
    def apply_patch(data: Any, patches: List[Dict[str, Any]]) -> Any:
        """应用JSON Patch到数据上

        Args:
            data: 原始数据
            patches: JSON Patch操作列表

        Returns:
            修改后的数据

        Raises:
            ValueError: Patch操作失败
        """
        result = copy.deepcopy(data)
        for patch in patches:
            op = patch.get("op")
            path = patch.get("path", "")
            value = patch.get("value")

            # 将JSON指针转为路径
            parts = path.strip("/").split("/") if path != "" else []

            if op == "add":
                DiffEngine._patch_add(result, parts, value)
            elif op == "remove":
                DiffEngine._patch_remove(result, parts)
            elif op == "replace":
                DiffEngine._patch_replace(result, parts, value)
            elif op == "move":
                DiffEngine._patch_move(result, parts, patch.get("from", "").strip("/").split("/"))
            elif op == "copy":
                src_parts = patch.get("from", "").strip("/").split("/")
                src_val = DiffEngine._patch_get(result, src_parts)
                DiffEngine._patch_add(result, parts, copy.deepcopy(src_val))
            else:
                raise ValueError(f"未知的Patch操作: {op}")

        return result

    @staticmethod
    def _patch_get(data: Any, parts: List[str]) -> Any:
        """按路径获取值"""
        current = data
        for part in parts:
            if not part:
                continue
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    current = current[int(part)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        return current

    @staticmethod
    def _patch_add(data: Any, parts: List[str], value: Any) -> None:
        """按路径添加值"""
        if not parts:
            return
        current = data
        for part in parts[:-1]:
            if isinstance(current, dict):
                current = current.setdefault(part, {})
            elif isinstance(current, list):
                try:
                    current = current[int(part)]
                except (ValueError, IndexError):
                    return

        last = parts[-1]
        if isinstance(current, dict):
            current[last] = value
        elif isinstance(current, list):
            try:
                idx = int(last)
                current.insert(idx, value)
            except (ValueError, IndexError):
                pass

    @staticmethod
    def _patch_remove(data: Any, parts: List[str]) -> None:
        """按路径删除值"""
        if not parts:
            return
        current = data
        for part in parts[:-1]:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    current = current[int(part)]
                except (ValueError, IndexError):
                    return
            else:
                return

        last = parts[-1]
        if isinstance(current, dict) and last in current:
            del current[last]
        elif isinstance(current, list):
            try:
                del current[int(last)]
            except (ValueError, IndexError):
                pass

    @staticmethod
    def _patch_replace(data: Any, parts: List[str], value: Any) -> None:
        """按路径替换值"""
        if not parts:
            return
        current = data
        for part in parts[:-1]:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    current = current[int(part)]
                except (ValueError, IndexError):
                    return
            else:
                return

        last = parts[-1]
        if isinstance(current, dict) and last in current:
            current[last] = value
        elif isinstance(current, list):
            try:
                current[int(last)] = value
            except (ValueError, IndexError):
                pass
