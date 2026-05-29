"""
格式化输出引擎模块
====================
提供多种格式的数据输出，包括彩色JSON、彩色YAML、表格、树形、
Markdown表格和HTML表格。

使用示例:
    from dataforge_cli.core.formatter import Formatter

    data = {"name": "Alice", "age": 25, "items": [1, 2, 3]}

    # 彩色JSON输出
    print(Formatter.format_json(data, color=True))

    # 表格输出
    print(Formatter.format_table([{"name": "Alice", "age": 25}]))

    # 树形输出
    print(Formatter.format_tree(data))

    # Markdown表格
    print(Formatter.format_markdown_table([{"name": "Alice", "age": 25}]))
"""

import json
from typing import Any, Dict, List, Optional


class Formatter:
    """格式化输出引擎

    提供多种格式的数据展示功能。
    """

    @staticmethod
    def format_json(data: Any, indent: int = 2, color: bool = True,
                    sort_keys: bool = False) -> str:
        """格式化JSON输出（支持彩色）

        Args:
            data: 要格式化的数据
            indent: 缩进空格数
            color: 是否启用颜色
            sort_keys: 是否按键名排序

        Returns:
            格式化后的JSON字符串
        """
        if not color:
            return json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=sort_keys)

        json_str = json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=sort_keys)
        return Formatter._colorize_json(json_str)

    @staticmethod
    def _colorize_json(json_str: str) -> str:
        """为JSON字符串添加颜色

        Args:
            json_str: JSON字符串

        Returns:
            带ANSI颜色代码的JSON字符串
        """
        from dataforge_cli.utils.colors import Colors

        result: List[str] = []
        i = 0
        in_string = False
        string_char = ""

        while i < len(json_str):
            ch = json_str[i]

            if in_string:
                if ch == "\\" and i + 1 < len(json_str):
                    result.append(Colors.cyan(ch + json_str[i + 1]))
                    i += 2
                    continue
                if ch == string_char:
                    result.append(Colors.cyan(ch))
                    in_string = False
                    i += 1
                    continue
                result.append(Colors.cyan(ch))
                i += 1
                continue

            # 非字符串内容
            if ch in (" ", "\t", "\n", "\r"):
                result.append(ch)
                i += 1
                continue

            if ch == '"':
                in_string = True
                string_char = '"'
                result.append(Colors.green(ch))
                i += 1
                continue

            if ch == "'":
                in_string = True
                string_char = "'"
                result.append(Colors.green(ch))
                i += 1
                continue

            if ch in ("{", "}", "[", "]"):
                result.append(Colors.yellow(ch))
                i += 1
                continue

            if ch == ":":
                result.append(Colors.magenta(ch))
                i += 1
                continue

            if ch == ",":
                result.append(Colors.yellow(ch))
                i += 1
                continue

            # 数字和布尔值
            if ch in ("t", "f", "n") or ch.isdigit() or ch == "-":
                # 读取完整的token
                j = i
                while j < len(json_str) and json_str[j] not in (' ', '\t', '\n', '\r', ',', '}', ']', ':'):
                    j += 1
                token = json_str[i:j]
                if token in ("true", "false"):
                    result.append(Colors.blue(token))
                elif token == "null":
                    result.append(Colors.dim(token))
                else:
                    result.append(Colors.blue(token))
                i = j
                continue

            result.append(ch)
            i += 1

        return "".join(result)

    @staticmethod
    def format_yaml(data: Any, indent: int = 2, color: bool = True) -> str:
        """格式化YAML输出（支持彩色）

        Args:
            data: 要格式化的数据
            indent: 缩进空格数
            color: 是否启用颜色

        Returns:
            格式化后的YAML字符串
        """
        from dataforge_cli.core.parser import Parser

        yaml_str = Parser.serialize_yaml(data, indent=indent)

        if not color:
            return yaml_str

        return Formatter._colorize_yaml(yaml_str)

    @staticmethod
    def _colorize_yaml(yaml_str: str) -> str:
        """为YAML字符串添加颜色

        Args:
            yaml_str: YAML字符串

        Returns:
            带ANSI颜色代码的YAML字符串
        """
        from dataforge_cli.utils.colors import Colors

        lines = yaml_str.split("\n")
        result: List[str] = []

        for line in lines:
            if ":" in line:
                colon_idx = line.index(":")
                key_part = line[:colon_idx]
                value_part = line[colon_idx + 1:].strip()

                colored_line = Colors.magenta(key_part) + ":"
                if value_part:
                    colored_line += " " + Formatter._colorize_yaml_value(value_part)
                result.append(colored_line)
            elif line.startswith("- "):
                value = line[2:]
                result.append(Colors.yellow("-") + " " + Formatter._colorize_yaml_value(value))
            elif line.startswith("-"):
                result.append(Colors.yellow(line))
            else:
                result.append(line)

        return "\n".join(result)

    @staticmethod
    def _colorize_yaml_value(value: str) -> str:
        """为YAML值添加颜色

        Args:
            value: YAML值字符串

        Returns:
            带颜色的值字符串
        """
        from dataforge_cli.utils.colors import Colors

        value = value.strip()

        if not value:
            return value

        # 布尔值
        if value.lower() in ("true", "false", "yes", "no", "on", "off"):
            return Colors.blue(value)

        # null
        if value.lower() in ("null", "~", ""):
            return Colors.dim(value)

        # 数字
        try:
            float(value)
            return Colors.blue(value)
        except ValueError:
            pass

        # 引号字符串
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return Colors.green(value)

        # 普通字符串
        return Colors.green(value)

    @staticmethod
    def format_table(data: List[Dict[str, Any]], title: str = "",
                     max_col_width: int = 50, color: bool = True) -> str:
        """格式化终端表格输出

        Args:
            data: 字典列表
            title: 表格标题
            max_col_width: 列最大宽度
            color: 是否启用颜色

        Returns:
            表格格式字符串
        """
        if not data:
            return "(空数据)"

        # 确保数据是字典列表
        if isinstance(data, dict):
            data = [data]

        # 收集所有键
        headers: List[str] = []
        for row in data:
            if isinstance(row, dict):
                for key in row:
                    if key not in headers:
                        headers.append(key)

        if not headers:
            return "(无列数据)"

        # 计算列宽
        col_widths: Dict[str, int] = {}
        for h in headers:
            max_val_len = max(
                len(str(row.get(h, ""))) for row in data if isinstance(row, dict)
            ) if data else 0
            col_widths[h] = min(max(len(str(h)), max_val_len), max_col_width)

        lines: List[str] = []

        # 标题
        if title:
            if color:
                from dataforge_cli.utils.colors import Colors
                lines.append(f"  {Colors.bold(title)}")
            else:
                lines.append(f"  {title}")
            lines.append("")

        # 分隔线
        sep = "+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+"
        lines.append(sep)

        # 表头
        if color:
            from dataforge_cli.utils.colors import Colors
            header_line = "|" + "|".join(
                f" {Colors.bold(Colors.bright_cyan(str(h).ljust(col_widths[h])))} "
                for h in headers
            ) + "|"
        else:
            header_line = "|" + "|".join(
                f" {str(h).ljust(col_widths[h])} " for h in headers
            ) + "|"
        lines.append(header_line)
        lines.append(sep)

        # 数据行
        for row in data:
            if isinstance(row, dict):
                cells = []
                for h in headers:
                    val = str(row.get(h, ""))
                    if len(val) > max_col_width:
                        val = val[:max_col_width - 3] + "..."
                    cells.append(val.ljust(col_widths[h]))
                lines.append("|" + "|".join(f" {c} " for c in cells) + "|")

        lines.append(sep)

        # 行数统计
        if color:
            from dataforge_cli.utils.colors import Colors
            lines.append(Colors.dim(f"  共 {len(data)} 行"))
        else:
            lines.append(f"  共 {len(data)} 行")

        return "\n".join(lines)

    @staticmethod
    def format_tree(data: Any, prefix: str = "", color: bool = True) -> str:
        """格式化树形输出

        Args:
            data: 要展示的数据
            prefix: 行前缀（内部递归使用）
            color: 是否启用颜色

        Returns:
            树形格式字符串
        """
        lines: List[str] = []
        Formatter._build_tree(data, "", "", lines, color)
        return "\n".join(lines)

    @staticmethod
    def _build_tree(data: Any, prefix: str, connector: str,
                    lines: List[str], color: bool) -> None:
        """递归构建树形结构

        Args:
            data: 当前数据
            prefix: 前缀
            connector: 连接符
            lines: 输出行列表
            color: 是否启用颜色
        """
        if color:
            from dataforge_cli.utils.colors import Colors as C
        else:
            # 创建一个空操作的Colors替代
            class _NoColor:
                @staticmethod
                def __getattr__(self, name):
                    return lambda text="": text
            C = _NoColor()

        if isinstance(data, dict):
            items = list(data.items())
            for i, (key, value) in enumerate(items):
                is_last = i == len(items) - 1
                branch = "└── " if is_last else "├── "
                new_prefix = prefix + ("    " if is_last else "│   ")

                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}{connector}{C.yellow(branch)}{C.magenta(key)}")
                    Formatter._build_tree(value, new_prefix, "", lines, color)
                else:
                    val_str = Formatter._format_tree_value(value, color)
                    lines.append(f"{prefix}{connector}{C.yellow(branch)}{C.magenta(key)}: {val_str}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                is_last = i == len(data) - 1
                branch = "└── " if is_last else "├── "
                new_prefix = prefix + ("    " if is_last else "│   ")

                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}{connector}{C.yellow(branch)}[{C.blue(str(i))}]")
                    Formatter._build_tree(item, new_prefix, "", lines, color)
                else:
                    val_str = Formatter._format_tree_value(item, color)
                    lines.append(f"{prefix}{connector}{C.yellow(branch)}{C.blue(str(i))}: {val_str}")
        else:
            val_str = Formatter._format_tree_value(data, color)
            lines.append(f"{prefix}{connector}{val_str}")

    @staticmethod
    def _format_tree_value(value: Any, color: bool) -> str:
        """格式化树形节点的值

        Args:
            value: 节点值
            color: 是否启用颜色

        Returns:
            格式化后的值字符串
        """
        if color:
            from dataforge_cli.utils.colors import Colors
        else:
            class _NoColor:
                @staticmethod
                def __getattr__(self, name):
                    return lambda text="": text
            Colors = _NoColor()

        if value is None:
            return Colors.dim("null")
        if isinstance(value, bool):
            return Colors.blue(str(value).lower())
        if isinstance(value, (int, float)):
            return Colors.blue(str(value))
        if isinstance(value, str):
            return Colors.green(f'"{value}"')
        return str(value)

    @staticmethod
    def format_markdown_table(data: List[Dict[str, Any]],
                              title: str = "") -> str:
        """格式化Markdown表格

        Args:
            data: 字典列表
            title: 表格标题

        Returns:
            Markdown表格字符串
        """
        if not data:
            return "(空数据)"

        if isinstance(data, dict):
            data = [data]

        # 收集所有键
        headers: List[str] = []
        for row in data:
            if isinstance(row, dict):
                for key in row:
                    if key not in headers:
                        headers.append(key)

        if not headers:
            return "(无列数据)"

        lines: List[str] = []

        if title:
            lines.append(f"## {title}")
            lines.append("")

        # 表头
        lines.append("| " + " | ".join(str(h) for h in headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")

        # 数据行
        for row in data:
            if isinstance(row, dict):
                cells = []
                for h in headers:
                    val = row.get(h, "")
                    if isinstance(val, (dict, list)):
                        val = json.dumps(val, ensure_ascii=False)
                    cells.append(str(val).replace("|", "\\|").replace("\n", " "))
                lines.append("| " + " | ".join(cells) + " |")

        return "\n".join(lines)

    @staticmethod
    def format_html_table(data: List[Dict[str, Any]],
                          title: str = "",
                          table_class: str = "data-table") -> str:
        """格式化HTML表格

        Args:
            data: 字典列表
            title: 表格标题
            table_class: 表格CSS类名

        Returns:
            HTML表格字符串
        """
        if not data:
            return "<p>(空数据)</p>"

        if isinstance(data, dict):
            data = [data]

        # 收集所有键
        headers: List[str] = []
        for row in data:
            if isinstance(row, dict):
                for key in row:
                    if key not in headers:
                        headers.append(key)

        if not headers:
            return "<p>(无列数据)</p>"

        lines: List[str] = []

        if title:
            lines.append(f"<h3>{title}</h3>")

        lines.append(f'<table class="{table_class}">')

        # 表头
        lines.append("  <thead>")
        lines.append("    <tr>")
        for h in headers:
            lines.append(f"      <th>{h}</th>")
        lines.append("    </tr>")
        lines.append("  </thead>")

        # 数据行
        lines.append("  <tbody>")
        for i, row in enumerate(data):
            row_class = "even" if i % 2 == 0 else "odd"
            lines.append(f'    <tr class="{row_class}">')
            if isinstance(row, dict):
                for h in headers:
                    val = row.get(h, "")
                    if isinstance(val, (dict, list)):
                        val = json.dumps(val, ensure_ascii=False)
                    escaped = str(val).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    lines.append(f"      <td>{escaped}</td>")
            lines.append("    </tr>")
        lines.append("  </tbody>")

        lines.append("</table>")
        return "\n".join(lines)

    @staticmethod
    def format_stats(data: Any) -> str:
        """格式化数据统计信息

        Args:
            data: 输入数据

        Returns:
            格式化的统计信息字符串
        """
        from dataforge_cli.core.transform import TransformEngine

        stats = TransformEngine.stats(data)

        lines: List[str] = [
            "数据统计信息",
            "-" * 30,
        ]

        for key, value in stats.items():
            if isinstance(value, list):
                if len(value) > 10:
                    lines.append(f"  {key}: [{', '.join(str(v) for v in value[:10])}, ...] ({len(value)} 项)")
                else:
                    lines.append(f"  {key}: {value}")
            else:
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)
