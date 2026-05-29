"""
深度合并引擎模块
================
提供JSON/YAML对象的深度合并功能，支持多种合并策略和冲突解决机制。

使用示例:
    from dataforge_cli.core.merge import MergeEngine

    # 深度合并两个字典
    result = MergeEngine.deep_merge(
        {"a": 1, "b": {"c": 2}},
        {"b": {"d": 3}, "e": 4}
    )
    # 结果: {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}

    # 使用特定策略合并
    result = MergeEngine.merge(
        base.json, override.json,
        array_strategy="append",
        conflict="ours"
    )
"""

import copy
import json
from typing import Any, Dict, List, Optional, Tuple


class MergeEngine:
    """深度合并引擎

    支持多种合并策略和冲突解决机制。
    """

    # 数组合并策略
    ARRAY_STRATEGIES = ["append", "replace", "merge-by-key", "prepend"]

    # 冲突解决策略
    CONFLICT_STRATEGIES = ["ours", "theirs", "manual", "error"]

    @staticmethod
    def deep_merge(base: Any, override: Any, array_strategy: str = "replace",
                   conflict: str = "theirs") -> Any:
        """深度合并两个数据对象

        Args:
            base: 基础数据
            override: 覆盖数据
            array_strategy: 数组合并策略
                - "append": 将override的数组元素追加到base数组末尾
                - "prepend": 将override的数组元素插入到base数组开头
                - "replace": 用override数组完全替换base数组
                - "merge-by-key": 按键值合并数组中的字典元素
            conflict: 冲突解决策略
                - "ours": 保留base的值
                - "theirs": 使用override的值
                - "manual": 返回冲突信息供手动解决
                - "error": 遇到冲突时抛出异常

        Returns:
            合并后的数据

        Raises:
            ValueError: 不支持的策略或遇到冲突（conflict="error"时）
        """
        if array_strategy not in MergeEngine.ARRAY_STRATEGIES:
            raise ValueError(f"不支持的数组合并策略: {array_strategy}，"
                             f"支持: {MergeEngine.ARRAY_STRATEGIES}")
        if conflict not in MergeEngine.CONFLICT_STRATEGIES:
            raise ValueError(f"不支持的冲突策略: {conflict}，"
                             f"支持: {MergeEngine.CONFLICT_STRATEGIES}")

        return MergeEngine._merge_recursive(base, override, array_strategy, conflict, "")

    @staticmethod
    def _merge_recursive(base: Any, override: Any, array_strategy: str,
                         conflict: str, path: str) -> Any:
        """递归合并数据

        Args:
            base: 基础数据
            override: 覆盖数据
            array_strategy: 数组合并策略
            conflict: 冲突解决策略
            path: 当前路径（用于冲突报告）

        Returns:
            合并后的数据
        """
        # 如果override为None，返回base
        if override is None:
            return copy.deepcopy(base)

        # 如果base为None，返回override
        if base is None:
            return copy.deepcopy(override)

        # 两个都是字典：深度合并
        if isinstance(base, dict) and isinstance(override, dict):
            result = copy.deepcopy(base)
            for key, value in override.items():
                new_path = f"{path}.{key}" if path else key
                if key in result:
                    # 键冲突
                    if isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = MergeEngine._merge_recursive(
                            result[key], value, array_strategy, conflict, new_path
                        )
                    elif isinstance(result[key], list) and isinstance(value, list):
                        result[key] = MergeEngine._merge_arrays(
                            result[key], value, array_strategy, conflict, new_path
                        )
                    else:
                        # 值冲突
                        result[key] = MergeEngine._resolve_conflict(
                            result[key], value, conflict, new_path
                        )
                else:
                    result[key] = copy.deepcopy(value)
            return result

        # 两个都是列表：按策略合并
        if isinstance(base, list) and isinstance(override, list):
            return MergeEngine._merge_arrays(base, override, array_strategy, conflict, path)

        # 类型不同或都是标量：按冲突策略处理
        return MergeEngine._resolve_conflict(base, override, conflict, path)

    @staticmethod
    def _merge_arrays(base: List, override: List, strategy: str,
                     conflict: str, path: str) -> List:
        """按策略合并数组

        Args:
            base: 基础数组
            override: 覆盖数组
            strategy: 合并策略
            conflict: 冲突策略
            path: 当前路径

        Returns:
            合并后的数组
        """
        if strategy == "replace":
            return copy.deepcopy(override)

        if strategy == "append":
            result = copy.deepcopy(base)
            result.extend(copy.deepcopy(override))
            return result

        if strategy == "prepend":
            result = copy.deepcopy(override)
            result.extend(copy.deepcopy(base))
            return result

        if strategy == "merge-by-key":
            # 按字典的某个键进行合并
            result = copy.deepcopy(base)
            for item in override:
                if isinstance(item, dict):
                    # 尝试找到匹配的键
                    merge_key = MergeEngine._find_merge_key(item, result)
                    if merge_key is not None:
                        # 找到匹配项，深度合并
                        for i, existing in enumerate(result):
                            if isinstance(existing, dict) and existing.get(merge_key) == item.get(merge_key):
                                result[i] = MergeEngine._merge_recursive(
                                    existing, item, strategy, conflict, f"{path}[{i}]"
                                )
                                break
                    else:
                        result.append(copy.deepcopy(item))
                else:
                    result.append(copy.deepcopy(item))
            return result

        return copy.deepcopy(override)

    @staticmethod
    def _find_merge_key(item: Dict, target_list: List) -> Optional[str]:
        """查找用于合并的键

        优先使用 'id', 'key', 'name' 等常见键名。

        Args:
            item: 要合并的字典
            target_list: 目标列表

        Returns:
            合并键名，如果找不到返回None
        """
        # 常见的合并键名（按优先级）
        common_keys = ["id", "key", "name", "slug", "code", "_id", "uuid"]

        for key in common_keys:
            if key in item:
                # 检查目标列表中是否有相同键值的项
                item_value = item[key]
                for target in target_list:
                    if isinstance(target, dict) and target.get(key) == item_value:
                        return key

        return None

    @staticmethod
    def _resolve_conflict(base: Any, override: Any, strategy: str,
                         path: str) -> Any:
        """解决值冲突

        Args:
            base: 基础值
            override: 覆盖值
            strategy: 冲突策略
            path: 冲突路径

        Returns:
            解决后的值

        Raises:
            ValueError: conflict="error"时
        """
        if base == override:
            return base

        if strategy == "ours":
            return base
        elif strategy == "theirs":
            return override
        elif strategy == "manual":
            return {
                "__conflict": True,
                "__path": path,
                "__base": base,
                "__override": override,
            }
        elif strategy == "error":
            raise ValueError(
                f"合并冲突于路径 '{path}': "
                f"base={base!r}, override={override!r}"
            )
        else:
            return override

    @staticmethod
    def merge_files(file_paths: List[str], array_strategy: str = "replace",
                    conflict: str = "theirs", format: Optional[str] = None) -> Any:
        """合并多个文件

        Args:
            file_paths: 文件路径列表
            array_strategy: 数组合并策略
            conflict: 冲突解决策略
            format: 文件格式（为None时自动检测）

        Returns:
            合并后的数据
        """
        from dataforge_cli.core.parser import Parser

        if not file_paths:
            return None

        result = Parser.parse_file(file_paths[0], format)
        for path in file_paths[1:]:
            data = Parser.parse_file(path, format)
            result = MergeEngine.deep_merge(result, data, array_strategy, conflict)

        return result

    @staticmethod
    def preview_merge(base: Any, override: Any, array_strategy: str = "replace",
                      conflict: str = "theirs") -> Dict[str, Any]:
        """预览合并结果（dry-run模式）

        不实际执行合并，而是返回合并预览信息，包括冲突列表。

        Args:
            base: 基础数据
            override: 覆盖数据
            array_strategy: 数组合并策略
            conflict: 冲突策略

        Returns:
            预览信息字典，包含:
            - "result": 合并结果
            - "conflicts": 冲突列表
            - "changes": 变更统计
        """
        conflicts: List[Dict[str, Any]] = []
        changes: Dict[str, int] = {"added": 0, "removed": 0, "modified": 0, "unchanged": 0}

        # 使用manual策略来收集所有冲突
        result = MergeEngine._merge_preview_recursive(
            base, override, array_strategy, conflict, "", conflicts, changes
        )

        return {
            "result": result,
            "conflicts": conflicts,
            "changes": changes,
        }

    @staticmethod
    def _merge_preview_recursive(base: Any, override: Any, array_strategy: str,
                                   conflict: str, path: str,
                                   conflicts: List[Dict[str, Any]],
                                   changes: Dict[str, int]) -> Any:
        """递归预览合并

        Args:
            base: 基础数据
            override: 覆盖数据
            array_strategy: 数组合并策略
            conflict: 冲突策略
            path: 当前路径
            conflicts: 冲突列表（累积）
            changes: 变更统计（累积）

        Returns:
            合并后的数据
        """
        if override is None:
            return copy.deepcopy(base)

        if base is None:
            changes["added"] += 1
            return copy.deepcopy(override)

        if isinstance(base, dict) and isinstance(override, dict):
            result = copy.deepcopy(base)
            for key, value in override.items():
                new_path = f"{path}.{key}" if path else key
                if key not in result:
                    changes["added"] += 1
                    result[key] = copy.deepcopy(value)
                else:
                    if isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = MergeEngine._merge_preview_recursive(
                            result[key], value, array_strategy, conflict,
                            new_path, conflicts, changes
                        )
                    elif isinstance(result[key], list) and isinstance(value, list):
                        result[key] = MergeEngine._merge_arrays(
                            result[key], value, array_strategy, conflict, new_path
                        )
                        changes["modified"] += 1
                    elif result[key] != value:
                        conflicts.append({
                            "path": new_path,
                            "base": result[key],
                            "override": value,
                        })
                        changes["modified"] += 1
                        result[key] = MergeEngine._resolve_conflict(
                            result[key], value, conflict, new_path
                        )
                    else:
                        changes["unchanged"] += 1
            return result

        if isinstance(base, list) and isinstance(override, list):
            if base != override:
                changes["modified"] += 1
            return MergeEngine._merge_arrays(base, override, array_strategy, conflict, path)

        if base != override:
            conflicts.append({
                "path": path,
                "base": base,
                "override": override,
            })
            changes["modified"] += 1
            return MergeEngine._resolve_conflict(base, override, conflict, path)

        changes["unchanged"] += 1
        return base
