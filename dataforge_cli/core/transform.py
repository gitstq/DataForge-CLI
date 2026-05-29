"""
数据转换引擎模块
================
支持JSON、YAML、TOML、CSV之间的格式转换，以及JSON的minify/beautify、
key排序、flatten/unflatten等操作。

使用示例:
    from dataforge_cli.core.transform import TransformEngine

    # JSON转YAML
    yaml_str = TransformEngine.convert(data, "json", "yaml")

    # JSON beautify
    pretty = TransformEngine.beautify('{"key":"value"}')

    # JSON flatten
    flat = TransformEngine.flatten({"a": {"b": {"c": 1}}})
    # 结果: {"a.b.c": 1}
"""

import csv
import io
import json
from typing import Any, Dict, List, Optional, Union


class TransformEngine:
    """数据格式转换引擎

    提供多种数据格式之间的转换功能，以及JSON数据的处理工具。
    """

    @staticmethod
    def convert(data: Any, from_format: str, to_format: str, **kwargs) -> Any:
        """在格式之间转换数据

        Args:
            data: 输入数据（Python对象或字符串）
            from_format: 源格式（json/yaml/toml/csv）
            to_format: 目标格式（json/yaml/toml/csv/table）
            **kwargs: 转换选项

        Returns:
            转换后的数据（字符串或Python对象）

        Raises:
            ValueError: 不支持的格式
        """
        from_format = from_format.lower()
        to_format = to_format.lower()

        # 如果输入是字符串，先解析为Python对象
        if isinstance(data, str):
            from dataforge_cli.core.parser import Parser
            data = Parser.parse(data, from_format)

        # 执行转换
        if to_format == "json":
            return TransformEngine.to_json(data, **kwargs)
        elif to_format == "yaml":
            return TransformEngine.to_yaml(data, **kwargs)
        elif to_format == "toml":
            return TransformEngine.to_toml(data)
        elif to_format == "csv":
            return TransformEngine.to_csv(data, **kwargs)
        elif to_format == "table":
            return TransformEngine.to_table(data, **kwargs)
        else:
            raise ValueError(f"不支持的目标格式: {to_format}")

    @staticmethod
    def to_json(data: Any, indent: int = 2, ensure_ascii: bool = False,
                sort_keys: bool = False, minify: bool = False) -> str:
        """将数据转换为JSON字符串

        Args:
            data: Python对象
            indent: 缩进空格数（minify时忽略）
            ensure_ascii: 是否转义非ASCII字符
            sort_keys: 是否按键名排序
            minify: 是否压缩输出

        Returns:
            JSON格式字符串
        """
        if minify:
            return json.dumps(data, ensure_ascii=ensure_ascii, sort_keys=sort_keys,
                              separators=(",", ":"), default=str)
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii,
                          sort_keys=sort_keys, default=str)

    @staticmethod
    def to_yaml(data: Any, indent: int = 2) -> str:
        """将数据转换为YAML字符串

        Args:
            data: Python对象
            indent: 缩进空格数

        Returns:
            YAML格式字符串
        """
        from dataforge_cli.core.parser import Parser
        return Parser.serialize_yaml(data, indent=indent)

    @staticmethod
    def to_toml(data: Any) -> str:
        """将数据转换为TOML字符串

        Args:
            data: Python对象（必须是字典）

        Returns:
            TOML格式字符串
        """
        from dataforge_cli.core.parser import Parser
        return Parser.serialize_toml(data)

    @staticmethod
    def to_csv(data: Any, delimiter: str = ",", flatten: bool = True,
               include_headers: bool = True) -> str:
        """将数据转换为CSV字符串

        Args:
            data: Python对象（字典列表或字典）
            delimiter: 分隔符
            flatten: 是否展平嵌套结构
            include_headers: 是否包含表头

        Returns:
            CSV格式字符串
        """
        # 确保数据是列表形式
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            return str(data)

        if not data:
            return ""

        # 展平嵌套结构
        if flatten:
            data = [TransformEngine.flatten_dict(item, separator=".") for item in data]

        # 收集所有键
        headers: List[str] = []
        for row in data:
            if isinstance(row, dict):
                for key in row:
                    if key not in headers:
                        headers.append(key)

        if not headers:
            return ""

        output = io.StringIO()
        writer = csv.writer(output, delimiter=delimiter)

        if include_headers:
            writer.writerow(headers)

        for row in data:
            if isinstance(row, dict):
                writer.writerow([TransformEngine._csv_value(row.get(h, "")) for h in headers])
            else:
                writer.writerow([str(row)])

        return output.getvalue()

    @staticmethod
    def to_table(data: Any, title: str = "", max_col_width: int = 50) -> str:
        """将数据转换为终端表格字符串

        Args:
            data: Python对象（字典列表）
            title: 表格标题
            max_col_width: 列最大宽度

        Returns:
            表格格式字符串
        """
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            return str(data)

        if not data:
            return "(空数据)"

        # 收集所有键
        headers: List[str] = []
        for row in data:
            if isinstance(row, dict):
                for key in row:
                    if key not in headers:
                        headers.append(key)

        if not headers:
            return "(无列数据)"

        # 计算每列宽度
        col_widths: Dict[str, int] = {}
        for h in headers:
            col_widths[h] = min(max(len(str(h)), max(len(str(row.get(h, ""))) for row in data if isinstance(row, dict))), max_col_width)

        # 构建表格行
        lines: List[str] = []

        # 标题
        if title:
            lines.append(f"  {title}")
            lines.append("")

        # 分隔线
        sep = "+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+"
        lines.append(sep)

        # 表头
        header_line = "|" + "|".join(f" {str(h).ljust(col_widths[h])} " for h in headers) + "|"
        lines.append(header_line)
        lines.append(sep)

        # 数据行
        for row in data:
            if isinstance(row, dict):
                row_line = "|" + "|".join(
                    f" {str(row.get(h, ''))[:max_col_width].ljust(col_widths[h])} "
                    for h in headers
                ) + "|"
                lines.append(row_line)

        lines.append(sep)
        return "\n".join(lines)

    @staticmethod
    def _csv_value(value: Any) -> str:
        """将值转为CSV安全的字符串

        Args:
            value: 输入值

        Returns:
            CSV安全的字符串
        """
        if value is None:
            return ""
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    # ==================== JSON 处理工具 ====================

    @staticmethod
    def beautify(json_str: str, indent: int = 2, sort_keys: bool = False) -> str:
        """美化JSON字符串

        Args:
            json_str: 压缩的JSON字符串
            indent: 缩进空格数
            sort_keys: 是否按键名排序

        Returns:
            格式化后的JSON字符串
        """
        data = json.loads(json_str)
        return json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=sort_keys)

    @staticmethod
    def minify(json_str: str) -> str:
        """压缩JSON字符串

        Args:
            json_str: JSON字符串

        Returns:
            压缩后的JSON字符串
        """
        data = json.loads(json_str)
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def sort_keys(json_str: str, indent: int = 2) -> str:
        """对JSON键名进行排序

        Args:
            json_str: JSON字符串
            indent: 缩进空格数

        Returns:
            键名排序后的JSON字符串
        """
        data = json.loads(json_str)
        return json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=True)

    # ==================== Flatten / Unflatten ====================

    @staticmethod
    def flatten(data: Any, separator: str = ".") -> Dict[str, Any]:
        """展平嵌套字典

        将 {"a": {"b": {"c": 1}}} 展平为 {"a.b.c": 1}

        Args:
            data: 嵌套的字典
            separator: 路径分隔符

        Returns:
            展平后的字典
        """
        if not isinstance(data, dict):
            return {"": data}

        result: Dict[str, Any] = {}
        TransformEngine._flatten_recursive(data, "", separator, result)
        return result

    @staticmethod
    def _flatten_recursive(data: Any, prefix: str, separator: str,
                           result: Dict[str, Any]) -> None:
        """递归展平字典

        Args:
            data: 当前数据
            prefix: 当前路径前缀
            separator: 路径分隔符
            result: 结果字典
        """
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{prefix}{separator}{key}" if prefix else str(key)
                if isinstance(value, dict) and value:
                    TransformEngine._flatten_recursive(value, new_key, separator, result)
                elif isinstance(value, list):
                    # 数组项也展平
                    for i, item in enumerate(value):
                        array_key = f"{new_key}[{i}]"
                        if isinstance(item, (dict, list)):
                            TransformEngine._flatten_recursive(item, array_key, separator, result)
                        else:
                            result[array_key] = item
                else:
                    result[new_key] = value
        elif isinstance(data, list):
            for i, item in enumerate(data):
                array_key = f"{prefix}[{i}]" if prefix else f"[{i}]"
                if isinstance(item, (dict, list)):
                    TransformEngine._flatten_recursive(item, array_key, separator, result)
                else:
                    result[array_key] = item
        else:
            result[prefix] = data

    @staticmethod
    def flatten_dict(data: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
        """展平字典（不处理数组索引）

        Args:
            data: 嵌套字典
            separator: 路径分隔符

        Returns:
            展平后的字典
        """
        result: Dict[str, Any] = {}
        TransformEngine._flatten_dict_recursive(data, "", separator, result)
        return result

    @staticmethod
    def _flatten_dict_recursive(data: Any, prefix: str, separator: str,
                                 result: Dict[str, Any]) -> None:
        """递归展平字典（仅字典层级）

        Args:
            data: 当前数据
            prefix: 路径前缀
            separator: 分隔符
            result: 结果字典
        """
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{prefix}{separator}{key}" if prefix else str(key)
                if isinstance(value, dict):
                    TransformEngine._flatten_dict_recursive(value, new_key, separator, result)
                else:
                    result[new_key] = value
        else:
            result[prefix] = data

    @staticmethod
    def unflatten(data: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
        """将展平的字典还原为嵌套结构

        将 {"a.b.c": 1} 还原为 {"a": {"b": {"c": 1}}}

        Args:
            data: 展平的字典
            separator: 路径分隔符

        Returns:
            嵌套的字典
        """
        result: Dict[str, Any] = {}
        for key, value in data.items():
            # 处理数组索引路径 a[0].b
            parts = TransformEngine._parse_path_parts(key, separator)
            current = result
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    # 判断下一部分是否为数组索引
                    next_part = parts[i + 1]
                    if isinstance(next_part, int):
                        current[part] = []
                    else:
                        current[part] = {}
                current = current[part]

            last_part = parts[-1]
            if isinstance(last_part, int):
                # 确保父级是列表
                if not isinstance(current, list):
                    current = []
                while len(current) <= last_part:
                    current.append(None)
                current[last_part] = value
            else:
                current[last_part] = value

        return result

    @staticmethod
    def _parse_path_parts(key: str, separator: str) -> List[Union[str, int]]:
        """解析路径为部分列表

        将 "a.b[0].c" 解析为 ["a", "b", 0, "c"]

        Args:
            key: 路径字符串
            separator: 分隔符

        Returns:
            路径部分列表（字符串或整数）
        """
        parts: List[Union[str, int]] = []
        # 先按数组索引分割
        segments = re.split(r'[\[\]]', key) if hasattr(__builtins__, '__import__') else key.replace("[", "|").replace("]", "|").split("|")

        # 使用正则分割
        import re
        tokens = re.split(r'[\[\].]', key)

        for token in tokens:
            if not token:
                continue
            try:
                parts.append(int(token))
            except ValueError:
                parts.append(token)

        return parts

    # ==================== 数据统计 ====================

    @staticmethod
    def stats(data: Any) -> Dict[str, Any]:
        """收集数据的统计信息

        Args:
            data: 输入数据

        Returns:
            统计信息字典
        """
        result: Dict[str, Any] = {
            "type": type(data).__name__,
        }

        if isinstance(data, dict):
            result["key_count"] = len(data)
            result["keys"] = list(data.keys())
            result["depth"] = TransformEngine._calc_depth(data)
            types = set(type(v).__name__ for v in data.values())
            result["value_types"] = list(types)
        elif isinstance(data, list):
            result["length"] = len(data)
            if data:
                types = set(type(v).__name__ for v in data)
                result["item_types"] = list(types)
                result["depth"] = TransformEngine._calc_depth(data)
        elif isinstance(data, str):
            result["length"] = len(data)
            result["char_count"] = len(data)
            result["line_count"] = data.count("\n") + 1

        return result

    @staticmethod
    def _calc_depth(data: Any, current: int = 0) -> int:
        """计算数据的嵌套深度

        Args:
            data: 输入数据
            current: 当前深度

        Returns:
            最大嵌套深度
        """
        if isinstance(data, dict):
            if not data:
                return current
            return max(TransformEngine._calc_depth(v, current + 1) for v in data.values())
        elif isinstance(data, list):
            if not data:
                return current
            return max(TransformEngine._calc_depth(v, current + 1) for v in data)
        return current
