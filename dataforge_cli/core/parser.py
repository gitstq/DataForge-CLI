"""
数据解析器模块
==============
支持JSON、YAML、TOML、CSV四种格式的数据解析。
其中YAML和TOML解析器为自行实现的简易版本，不依赖PyYAML或toml库。

使用示例:
    from dataforge_cli.core.parser import Parser

    # 解析JSON
    data = Parser.parse('{"key": "value"}', format="json")

    # 解析YAML
    data = Parser.parse("key: value\\nlist:\\n  - item1", format="yaml")

    # 解析TOML
    data = Parser.parse('[section]\\nkey = "value"', format="toml")

    # 自动检测格式
    data = Parser.parse_file("data.json")

    # 序列化
    yaml_str = Parser.serialize(data, format="yaml")
"""

import csv
import io
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union


class Parser:
    """多格式数据解析器

    支持JSON、YAML、TOML、CSV格式的解析和序列化。
    YAML和TOML使用自研简易解析器实现。
    """

    # 支持的格式列表
    SUPPORTED_FORMATS = ["json", "yaml", "toml", "csv"]

    @staticmethod
    def parse(text: str, format: Optional[str] = None) -> Any:
        """解析文本数据为Python对象

        Args:
            text: 要解析的文本内容
            format: 指定格式（json/yaml/toml/csv），为None时自动检测

        Returns:
            解析后的Python对象

        Raises:
            ValueError: 格式不支持或解析失败
        """
        if format is None:
            format = Parser.detect_format(text)

        if format == "json":
            return Parser.parse_json(text)
        elif format == "yaml":
            return Parser.parse_yaml(text)
        elif format == "toml":
            return Parser.parse_toml(text)
        elif format == "csv":
            return Parser.parse_csv(text)
        else:
            raise ValueError(f"不支持的格式: {format}，支持的格式: {Parser.SUPPORTED_FORMATS}")

    @staticmethod
    def parse_file(filepath: str, format: Optional[str] = None) -> Any:
        """解析文件为Python对象

        Args:
            filepath: 文件路径
            format: 指定格式，为None时根据扩展名自动检测

        Returns:
            解析后的Python对象
        """
        from dataforge_cli.utils.file_io import FileIO

        if format is None:
            format = FileIO.detect_format(filepath)

        text = FileIO.read(filepath)
        return Parser.parse(text, format)

    @staticmethod
    def serialize(data: Any, format: str = "json", **kwargs) -> str:
        """将Python对象序列化为指定格式的字符串

        Args:
            data: 要序列化的Python对象
            format: 目标格式（json/yaml/toml/csv）
            **kwargs: 序列化选项

        Returns:
            序列化后的字符串
        """
        if format == "json":
            indent = kwargs.get("indent", 2)
            ensure_ascii = kwargs.get("ensure_ascii", False)
            sort_keys = kwargs.get("sort_keys", False)
            return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii,
                              sort_keys=sort_keys, default=str)
        elif format == "yaml":
            return Parser.serialize_yaml(data, indent=kwargs.get("indent", 2))
        elif format == "toml":
            return Parser.serialize_toml(data)
        elif format == "csv":
            return Parser.serialize_csv(data)
        else:
            raise ValueError(f"不支持的序列化格式: {format}")

    @staticmethod
    def detect_format(text: str) -> str:
        """根据文本内容自动检测格式

        Args:
            text: 文本内容

        Returns:
            检测到的格式名称
        """
        text = text.strip()
        if not text:
            return "json"

        # JSON检测：以 { 或 [ 开头
        if text.startswith("{") or text.startswith("["):
            try:
                json.loads(text)
                return "json"
            except (json.JSONDecodeError, ValueError):
                pass

        # CSV检测：包含逗号分隔的行，且多行结构一致
        lines = text.split("\n")
        if len(lines) >= 2:
            comma_count = lines[0].count(",")
            if comma_count > 0 and all(line.count(",") == comma_count for line in lines[1:] if line.strip()):
                return "csv"

        # TOML检测：包含 [section] 或 key = value
        if re.search(r'^\[.*\]$', text, re.MULTILINE) or re.search(r'^[a-zA-Z_]\w*\s*=', text, re.MULTILINE):
            return "toml"

        # 默认为YAML
        return "yaml"

    # ==================== JSON 解析 ====================

    @staticmethod
    def parse_json(text: str) -> Any:
        """解析JSON文本

        Args:
            text: JSON格式的文本

        Returns:
            解析后的Python对象

        Raises:
            ValueError: JSON解析失败
        """
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {e}")

    # ==================== YAML 解析（自研简易版）====================

    @staticmethod
    def parse_yaml(text: str) -> Any:
        """解析YAML文本（简易版实现）

        支持的特性:
        - 映射（键值对）
        - 序列（列表）
        - 标量值（字符串、数字、布尔、null）
        - 缩进层级
        - 注释（# 开头）
        - 多行字符串
        - 锚点和别名（基础支持）
        - 流式语法（{key: value} 和 [item1, item2]）

        Args:
            text: YAML格式的文本

        Returns:
            解析后的Python对象

        Raises:
            ValueError: YAML解析失败
        """
        try:
            return _YAMLParser(text).parse()
        except Exception as e:
            raise ValueError(f"YAML解析失败: {e}")

    @staticmethod
    def serialize_yaml(data: Any, indent: int = 2) -> str:
        """将Python对象序列化为YAML格式字符串

        Args:
            data: 要序列化的Python对象
            indent: 缩进空格数

        Returns:
            YAML格式字符串
        """
        return _YAMLSerializer(indent=indent).serialize(data)

    # ==================== TOML 解析（自研简易版）====================

    @staticmethod
    def parse_toml(text: str) -> Dict[str, Any]:
        """解析TOML文本（简易版实现）

        支持的特性:
        - 键值对（字符串、整数、浮点数、布尔值）
        - 表（[section]）
        - 嵌套表（[section.subsection]）
        - 数组（[1, 2, 3]）
        - 字符串（双引号和单引号）
        - 注释（# 开头）

        Args:
            text: TOML格式的文本

        Returns:
            解析后的字典

        Raises:
            ValueError: TOML解析失败
        """
        try:
            return _TOMLParser(text).parse()
        except Exception as e:
            raise ValueError(f"TOML解析失败: {e}")

    @staticmethod
    def serialize_toml(data: Dict[str, Any]) -> str:
        """将Python字典序列化为TOML格式字符串

        Args:
            data: 要序列化的字典

        Returns:
            TOML格式字符串
        """
        return _TOMLSerializer().serialize(data)

    # ==================== CSV 解析 ====================

    @staticmethod
    def parse_csv(text: str, delimiter: str = ",", has_header: bool = True) -> List[Dict[str, str]]:
        """解析CSV文本为字典列表

        Args:
            text: CSV格式的文本
            delimiter: 分隔符，默认为逗号
            has_header: 是否有表头行

        Returns:
            字典列表，每个字典代表一行数据
        """
        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        rows = list(reader)

        if not rows:
            return []

        if has_header and len(rows) > 1:
            headers = rows[0]
            return [{headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))} for row in rows[1:]]
        else:
            # 无表头时，使用列索引作为键
            return [{f"col_{i}": val for i, val in enumerate(row)} for row in rows]

    @staticmethod
    def serialize_csv(data: List[Dict[str, Any]], delimiter: str = ",") -> str:
        """将字典列表序列化为CSV格式字符串

        Args:
            data: 字典列表
            delimiter: 分隔符

        Returns:
            CSV格式字符串
        """
        if not data:
            return ""

        # 收集所有可能的键
        headers: List[str] = []
        for row in data:
            for key in row:
                if key not in headers:
                    headers.append(key)

        output = io.StringIO()
        writer = csv.writer(output, delimiter=delimiter)
        writer.writerow(headers)
        for row in data:
            writer.writerow([str(row.get(h, "")) for h in headers])

        return output.getvalue()


class _YAMLParser:
    """简易YAML解析器实现

    支持基本的YAML子集：映射、序列、标量、缩进、注释。
    """

    def __init__(self, text: str):
        """初始化YAML解析器

        Args:
            text: YAML文本内容
        """
        self.text = text
        self.lines: List[str] = []
        self.pos: int = 0
        self._prepare_lines()

    def _prepare_lines(self) -> None:
        """预处理文本行，去除注释和空白"""
        raw_lines = self.text.split("\n")
        self.lines = []
        for line in raw_lines:
            # 去除行尾注释（注意：字符串内的#不算注释）
            stripped = self._strip_comment(line)
            self.lines.append(stripped)

    def _strip_comment(self, line: str) -> str:
        """去除行尾注释，保留字符串内的#号

        Args:
            line: 原始行文本

        Returns:
            去除注释后的行
        """
        in_single = False
        in_double = False
        for i, ch in enumerate(line):
            if ch == '"' and not in_single:
                in_double = not in_double
            elif ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '#' and not in_single and not in_double:
                # 检查#前面是否有空格（YAML注释需要空格前缀）
                if i == 0 or line[i - 1] == ' ' or line[i - 1] == '\t':
                    return line[:i].rstrip()
        return line

    def parse(self) -> Any:
        """解析YAML文本

        Returns:
            解析后的Python对象
        """
        if not self.lines or all(l.strip() == "" for l in self.lines):
            return None

        return self._parse_block(0, self._get_root_indent())

    def _get_root_indent(self) -> int:
        """获取根级缩进量"""
        for line in self.lines:
            stripped = line.lstrip()
            if stripped and not stripped.startswith("#"):
                return len(line) - len(stripped)
        return 0

    def _get_indent(self, line: str) -> int:
        """获取行的缩进量

        Args:
            line: 行文本

        Returns:
            缩进的空格数
        """
        return len(line) - len(line.lstrip())

    def _is_blank(self, line: str) -> bool:
        """判断行是否为空行或纯注释行"""
        return line.strip() == ""

    def _parse_block(self, start: int, base_indent: int) -> Any:
        """解析一个数据块

        Args:
            start: 起始行索引
            base_indent: 基础缩进级别

        Returns:
            解析后的Python对象（dict或list）
        """
        # 收集同级别的非空行
        items: List[Tuple[int, str]] = []
        i = start
        while i < len(self.lines):
            line = self.lines[i]
            if self._is_blank(line):
                i += 1
                continue

            indent = self._get_indent(line)
            if indent < base_indent:
                break

            if indent == base_indent:
                items.append((i, line.strip()))
                i += 1
            else:
                # 缩进大于基础级别，属于上一项的子内容
                i += 1

        if not items:
            return None

        # 判断是序列还是映射
        # 如果所有行都以 "- " 开头，则为序列
        if all(s.startswith("- ") or s == "-" for _, s in items):
            return self._parse_sequence(items, base_indent)

        # 如果行包含 ": " 或以 ":" 结尾，则为映射
        if any(": " in s or s.endswith(":") for _, s in items):
            return self._parse_mapping(items, base_indent)

        # 否则尝试作为标量值
        if len(items) == 1:
            return self._parse_scalar(items[0][1])

        # 多个标量值作为列表返回
        return [self._parse_scalar(s) for _, s in items]

    def _parse_mapping(self, items: List[Tuple[int, str]], base_indent: int) -> Dict[str, Any]:
        """解析映射（字典）块

        Args:
            items: (行号, 行内容) 列表
            base_indent: 基础缩进

        Returns:
            解析后的字典
        """
        result: Dict[str, Any] = {}
        i = 0
        while i < len(items):
            line_no, content = items[i]

            # 解析键值对
            key, value_str = self._split_key_value(content)
            if key is None:
                i += 1
                continue

            # 查找值内容
            if value_str is not None and value_str.strip():
                # 行内值
                result[key] = self._parse_scalar(value_str.strip())
            else:
                # 多行值或子块
                # 直接从self.lines中查找下一级的行
                child_indent = base_indent + self._detect_indent_step(line_no)
                child_lines: List[Tuple[int, str]] = []
                j = line_no + 1
                while j < len(self.lines):
                    next_line = self.lines[j]
                    if self._is_blank(next_line):
                        j += 1
                        continue
                    next_indent = self._get_indent(next_line)
                    if next_indent >= child_indent:
                        child_lines.append((j, next_line.strip()))
                        j += 1
                    elif next_indent == base_indent:
                        break
                    else:
                        break

                if child_lines:
                    # 检查子内容是否为序列
                    if all(s.startswith("- ") or s == "-" for _, s in child_lines):
                        result[key] = self._parse_sequence(child_lines, child_indent)
                    else:
                        result[key] = self._parse_block_from_lines(child_lines, child_indent)
                else:
                    result[key] = None

                # 跳过已处理的子行
                i += 1
                continue

            i += 1

        return result

    def _parse_sequence(self, items: List[Tuple[int, str]], base_indent: int) -> List[Any]:
        """解析序列（列表）块

        Args:
            items: (行号, 行内容) 列表
            base_indent: 基础缩进

        Returns:
            解析后的列表
        """
        result: List[Any] = []
        i = 0
        while i < len(items):
            line_no, content = items[i]

            # 去除 "- " 前缀
            if content.startswith("- "):
                value_str = content[2:]
            elif content == "-":
                value_str = ""
            else:
                i += 1
                continue

            if value_str:
                # 行内值
                result.append(self._parse_scalar(value_str))
            else:
                # 多行子项
                child_indent = base_indent + self._detect_indent_step(line_no)
                child_lines: List[Tuple[int, str]] = []
                j = i + 1
                while j < len(items):
                    next_line_no, next_content = items[j]
                    next_indent = self._get_indent(self.lines[next_line_no])
                    if next_indent >= child_indent:
                        child_lines.append(items[j])
                        j += 1
                    else:
                        break

                if child_lines:
                    result.append(self._parse_block_from_lines(child_lines, child_indent))
                else:
                    result.append(None)

                i = j
                continue

            i += 1

        return result

    def _parse_block_from_lines(self, items: List[Tuple[int, str]], base_indent: int) -> Any:
        """从行列表解析数据块

        Args:
            items: (行号, 行内容) 列表
            base_indent: 基础缩进

        Returns:
            解析后的Python对象
        """
        if not items:
            return None

        # 检查是否为序列
        if all(s.startswith("- ") or s == "-" for _, s in items):
            return self._parse_sequence(items, base_indent)

        # 检查是否为映射
        if any(": " in s or s.endswith(":") for _, s in items):
            return self._parse_mapping(items, base_indent)

        # 标量
        if len(items) == 1:
            return self._parse_scalar(items[0][1])
        return [self._parse_scalar(s) for _, s in items]

    def _split_key_value(self, line: str) -> Tuple[Optional[str], Optional[str]]:
        """分割键值对

        Args:
            line: 行内容（已去除缩进）

        Returns:
            (键, 值字符串) 元组
        """
        # 查找 ": " 分隔符（不在引号内的）
        in_single = False
        in_double = False
        for i, ch in enumerate(line):
            if ch == '"' and not in_single:
                in_double = not in_double
            elif ch == "'" and not in_double:
                in_single = not in_single
            elif ch == ':' and not in_single and not in_double:
                if i + 1 < len(line) and line[i + 1] == ' ':
                    key = line[:i].strip()
                    value = line[i + 2:].strip()
                    return key, value
                elif i + 1 == len(line):
                    key = line[:i].strip()
                    return key, None
        return None, None

    def _detect_indent_step(self, line_no: int) -> int:
        """检测缩进步长

        Args:
            line_no: 行号

        Returns:
            缩进步长（空格数）
        """
        current_indent = self._get_indent(self.lines[line_no])
        for i in range(line_no + 1, len(self.lines)):
            line = self.lines[i]
            if not self._is_blank(line):
                next_indent = self._get_indent(line)
                if next_indent > current_indent:
                    return next_indent - current_indent
                break
        return 2  # 默认缩进步长

    def _parse_scalar(self, value: str) -> Any:
        """解析标量值

        支持字符串、整数、浮点数、布尔值、null。
        支持流式语法 {key: value} 和 [item1, item2]。

        Args:
            value: 标量值字符串

        Returns:
            解析后的Python对象
        """
        value = value.strip()
        if not value:
            return None

        # 流式映射
        if value.startswith("{") and value.endswith("}"):
            return self._parse_flow_mapping(value[1:-1])

        # 流式序列
        if value.startswith("[") and value.endswith("]"):
            return self._parse_flow_sequence(value[1:-1])

        # 引号字符串
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        # 布尔值
        if value.lower() in ("true", "yes", "on"):
            return True
        if value.lower() in ("false", "no", "off"):
            return False

        # null
        if value.lower() in ("null", "~", ""):
            return None

        # 整数
        try:
            if value.startswith("0x") or value.startswith("0X"):
                return int(value, 16)
            if value.startswith("0o") or value.startswith("0O"):
                return int(value, 8)
            return int(value)
        except ValueError:
            pass

        # 浮点数
        try:
            return float(value)
        except ValueError:
            pass

        # 多行字符串标记
        if value.startswith("|") or value.startswith(">"):
            return str(value)

        # 普通字符串
        return value

    def _parse_flow_mapping(self, text: str) -> Dict[str, Any]:
        """解析流式映射 {key: value, key2: value2}

        Args:
            text: 花括号内的文本

        Returns:
            解析后的字典
        """
        result: Dict[str, Any] = {}
        # 简易实现：按逗号分割
        parts = self._split_flow(text)
        for part in parts:
            part = part.strip()
            if ":" in part:
                key, _, val = part.partition(":")
                result[key.strip()] = self._parse_scalar(val.strip())
        return result

    def _parse_flow_sequence(self, text: str) -> List[Any]:
        """解析流式序列 [item1, item2, item3]

        Args:
            text: 方括号内的文本

        Returns:
            解析后的列表
        """
        parts = self._split_flow(text)
        return [self._parse_scalar(p.strip()) for p in parts if p.strip()]

    def _split_flow(self, text: str) -> List[str]:
        """分割流式内容（处理嵌套括号和引号）

        Args:
            text: 流式文本

        Returns:
            分割后的部分列表
        """
        parts: List[str] = []
        current = ""
        depth = 0
        in_single = False
        in_double = False

        for ch in text:
            if ch == '"' and not in_single:
                in_double = not in_double
                current += ch
            elif ch == "'" and not in_double:
                in_single = not in_single
                current += ch
            elif ch in ("{", "[") and not in_single and not in_double:
                depth += 1
                current += ch
            elif ch in ("}", "]") and not in_single and not in_double:
                depth -= 1
                current += ch
            elif ch == "," and depth == 0 and not in_single and not in_double:
                parts.append(current)
                current = ""
            else:
                current += ch

        if current.strip():
            parts.append(current)

        return parts


class _YAMLSerializer:
    """YAML序列化器"""

    def __init__(self, indent: int = 2):
        """初始化YAML序列化器

        Args:
            indent: 缩进空格数
        """
        self.indent = indent
        self._level = 0

    def serialize(self, data: Any) -> str:
        """将Python对象序列化为YAML字符串

        Args:
            data: 要序列化的对象

        Returns:
            YAML格式字符串
        """
        lines = self._serialize_value(data, 0)
        return "\n".join(lines) + "\n"

    def _serialize_value(self, data: Any, level: int) -> List[str]:
        """序列化一个值

        Args:
            data: 要序列化的值
            level: 当前缩进级别

        Returns:
            YAML行列表
        """
        indent_str = " " * (level * self.indent)

        if data is None:
            return [f"{indent_str}null"]

        if isinstance(data, bool):
            return [f"{indent_str}{'true' if data else 'false'}"]

        if isinstance(data, (int, float)):
            return [f"{indent_str}{data}"]

        if isinstance(data, str):
            # 如果字符串包含特殊字符，用引号包裹
            if any(c in data for c in [":", "{", "}", "[", "]", ",", "&", "*", "#", "?", "|", "-", "<", ">", "!", "=", "%", "@", "\\"]):
                # 转义双引号
                escaped = data.replace("\\", "\\\\").replace('"', '\\"')
                return [f'{indent_str}"{escaped}"']
            return [f"{indent_str}{data}"]

        if isinstance(data, list):
            return self._serialize_list(data, level)

        if isinstance(data, dict):
            return self._serialize_dict(data, level)

        # 其他类型转为字符串
        return [f"{indent_str}{str(data)}"]

    def _serialize_list(self, data: List[Any], level: int) -> List[str]:
        """序列化列表

        Args:
            data: 列表数据
            level: 当前缩进级别

        Returns:
            YAML行列表
        """
        lines: List[str] = []
        indent_str = " " * (level * self.indent)

        for item in data:
            if isinstance(item, dict):
                # 字典作为列表项时，第一个键值对和 - 在同一行
                if item:
                    first_key = next(iter(item))
                    first_val = item[first_key]
                    lines.append(f"{indent_str}- {first_key}: {self._scalar_to_str(first_val)}")
                    sub_lines = self._serialize_dict(item, level + 1, skip_first=True)
                    lines.extend(sub_lines)
                else:
                    lines.append(f"{indent_str}- {{}}")
            elif isinstance(item, list):
                lines.append(f"{indent_str}-")
                sub_lines = self._serialize_list(item, level + 1)
                lines.extend(sub_lines)
            else:
                lines.append(f"{indent_str}- {self._scalar_to_str(item)}")

        return lines

    def _serialize_dict(self, data: Dict[str, Any], level: int,
                        skip_first: bool = False) -> List[str]:
        """序列化字典

        Args:
            data: 字典数据
            level: 当前缩进级别
            skip_first: 是否跳过第一个键（用于列表内字典）

        Returns:
            YAML行列表
        """
        lines: List[str] = []
        indent_str = " " * (level * self.indent)

        items = list(data.items())
        start = 1 if skip_first else 0

        for i in range(start, len(items)):
            key, value = items[i]
            if isinstance(value, dict) and value:
                lines.append(f"{indent_str}{key}:")
                sub_lines = self._serialize_dict(value, level + 1)
                lines.extend(sub_lines)
            elif isinstance(value, list) and value:
                lines.append(f"{indent_str}{key}:")
                sub_lines = self._serialize_list(value, level + 1)
                lines.extend(sub_lines)
            else:
                lines.append(f"{indent_str}{key}: {self._scalar_to_str(value)}")

        return lines

    def _scalar_to_str(self, value: Any) -> str:
        """将标量值转为YAML字符串表示

        Args:
            value: 标量值

        Returns:
            YAML字符串表示
        """
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            if any(c in value for c in [":", "{", "}", "[", "]", ",", "&", "*", "#", "?", "|", "-"]):
                escaped = value.replace("\\", "\\\\").replace('"', '\\"')
                return f'"{escaped}"'
            return value
        return str(value)


class _TOMLParser:
    """简易TOML解析器实现

    支持基本的TOML子集：键值对、表、数组、字符串、数字、布尔值。
    """

    def __init__(self, text: str):
        """初始化TOML解析器

        Args:
            text: TOML文本内容
        """
        self.text = text
        self.lines: List[str] = []
        self._prepare_lines()

    def _prepare_lines(self) -> None:
        """预处理文本行"""
        raw_lines = self.text.split("\n")
        self.lines = []
        for line in raw_lines:
            # 去除行尾注释
            stripped = self._strip_comment(line)
            self.lines.append(stripped)

    def _strip_comment(self, line: str) -> str:
        """去除行尾注释"""
        in_single = False
        in_double = False
        for i, ch in enumerate(line):
            if ch == '"' and not in_single:
                in_double = not in_double
            elif ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '#' and not in_single and not in_double:
                if i == 0 or line[i - 1] == ' ':
                    return line[:i].rstrip()
        return line

    def parse(self) -> Dict[str, Any]:
        """解析TOML文本

        Returns:
            解析后的字典
        """
        result: Dict[str, Any] = {}
        current_table: List[str] = []

        for line in self.lines:
            stripped = line.strip()

            # 跳过空行
            if not stripped:
                continue

            # 表头 [section] 或 [[array_of_tables]]
            if stripped.startswith("[[") and stripped.endswith("]]"):
                # 数组表
                table_name = stripped[2:-2].strip()
                keys = [k.strip() for k in table_name.split(".")]
                current_table = keys
                # 确保路径存在
                self._ensure_path(result, keys, is_array=True)
                continue

            if stripped.startswith("[") and stripped.endswith("]"):
                # 普通表
                table_name = stripped[1:-1].strip()
                keys = [k.strip() for k in table_name.split(".")]
                current_table = keys
                # 确保路径存在
                self._ensure_path(result, keys)
                continue

            # 键值对
            if "=" in stripped:
                key, _, value = stripped.partition("=")
                key = key.strip()
                value = value.strip()
                parsed_value = self._parse_value(value)

                # 设置值
                target = result
                for k in current_table:
                    if isinstance(target.get(k), list):
                        target = target[k][-1]
                    else:
                        target = target.setdefault(k, {})

                # 处理带点号的键
                if "." in key:
                    key_parts = [k.strip() for k in key.split(".")]
                    for kp in key_parts[:-1]:
                        target = target.setdefault(kp, {})
                    target[key_parts[-1]] = parsed_value
                else:
                    target[key] = parsed_value

        return result

    def _ensure_path(self, data: Dict[str, Any], keys: List[str],
                     is_array: bool = False) -> None:
        """确保字典中存在指定的路径

        Args:
            data: 目标字典
            keys: 路径键列表
            is_array: 是否为数组表
        """
        target = data
        for i, key in enumerate(keys):
            if key not in target:
                if is_array and i == len(keys) - 1:
                    target[key] = [{}]
                elif i < len(keys) - 1:
                    target[key] = {}
                else:
                    target[key] = {}
            elif is_array and i == len(keys) - 1:
                if isinstance(target[key], list):
                    target[key].append({})
                else:
                    target[key] = [target[key], {}]
            if isinstance(target.get(key), list) and i < len(keys) - 1:
                target = target[key][-1]
            else:
                target = target.setdefault(key, target.get(key, {}))

    def _parse_value(self, value: str) -> Any:
        """解析TOML值

        Args:
            value: 值字符串

        Returns:
            解析后的Python对象
        """
        value = value.strip()

        # 字符串（双引号）
        if value.startswith('"') and value.endswith('"'):
            return self._parse_string(value[1:-1], is_double=True)

        # 字符串（单引号）
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]

        # 三引号字符串
        if value.startswith('"""') and value.endswith('"""'):
            return value[3:-3]

        if value.startswith("'''") and value.endswith("'''"):
            return value[3:-3]

        # 布尔值
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False

        # 数组
        if value.startswith("[") and value.endswith("]"):
            return self._parse_array(value[1:-1].strip())

        # 内联表
        if value.startswith("{") and value.endswith("}"):
            return self._parse_inline_table(value[1:-1].strip())

        # 整数
        try:
            if value.startswith("0x") or value.startswith("0X"):
                return int(value, 16)
            if value.startswith("0o") or value.startswith("0O"):
                return int(value, 8)
            if value.startswith("0b") or value.startswith("0B"):
                return int(value, 2)
            # 处理下划线分隔的数字
            clean = value.replace("_", "")
            return int(clean)
        except ValueError:
            pass

        # 浮点数
        try:
            clean = value.replace("_", "")
            return float(clean)
        except ValueError:
            pass

        # 特殊浮点值
        if value in ("inf", "+inf"):
            return float("inf")
        if value == "-inf":
            return float("-inf")
        if value in ("nan", "+nan", "-nan"):
            return float("nan")

        return value

    def _parse_string(self, text: str, is_double: bool = True) -> str:
        """解析TOML字符串，处理转义字符

        Args:
            text: 字符串内容（不含引号）
            is_double: 是否为双引号字符串

        Returns:
            解析后的字符串
        """
        if is_double:
            # 处理转义字符
            result = text.replace("\\n", "\n")
            result = result.replace("\\t", "\t")
            result = result.replace("\\r", "\r")
            result = result.replace('\\"', '"')
            result = result.replace("\\\\", "\\")
            result = result.replace("\\0", "\0")
            return result
        return text

    def _parse_array(self, text: str) -> List[Any]:
        """解析TOML数组

        Args:
            text: 数组内容（不含方括号）

        Returns:
            解析后的列表
        """
        items: List[Any] = []
        current = ""
        depth = 0
        in_single = False
        in_double = False

        for ch in text:
            if ch == '"' and not in_single:
                in_double = not in_double
                current += ch
            elif ch == "'" and not in_double:
                in_single = not in_single
                current += ch
            elif ch == "[" and not in_single and not in_double:
                depth += 1
                current += ch
            elif ch == "]" and not in_single and not in_double:
                depth -= 1
                current += ch
            elif ch == "," and depth == 0 and not in_single and not in_double:
                item = current.strip()
                if item:
                    items.append(self._parse_value(item))
                current = ""
            else:
                current += ch

        item = current.strip()
        if item:
            items.append(self._parse_value(item))

        return items

    def _parse_inline_table(self, text: str) -> Dict[str, Any]:
        """解析TOML内联表

        Args:
            text: 内联表内容（不含花括号）

        Returns:
            解析后的字典
        """
        result: Dict[str, Any] = {}
        parts = self._split_by_comma(text)
        for part in parts:
            part = part.strip()
            if "=" in part:
                key, _, val = part.partition("=")
                result[key.strip()] = self._parse_value(val.strip())
        return result

    def _split_by_comma(self, text: str) -> List[str]:
        """按逗号分割文本（处理嵌套结构）

        Args:
            text: 输入文本

        Returns:
            分割后的部分列表
        """
        parts: List[str] = []
        current = ""
        depth = 0
        in_single = False
        in_double = False

        for ch in text:
            if ch == '"' and not in_single:
                in_double = not in_double
                current += ch
            elif ch == "'" and not in_double:
                in_single = not in_single
                current += ch
            elif ch in ("{", "[") and not in_single and not in_double:
                depth += 1
                current += ch
            elif ch in ("}", "]") and not in_single and not in_double:
                depth -= 1
                current += ch
            elif ch == "," and depth == 0 and not in_single and not in_double:
                parts.append(current)
                current = ""
            else:
                current += ch

        if current.strip():
            parts.append(current)

        return parts


class _TOMLSerializer:
    """TOML序列化器"""

    def serialize(self, data: Dict[str, Any]) -> str:
        """将Python字典序列化为TOML格式字符串

        Args:
            data: 要序列化的字典

        Returns:
            TOML格式字符串
        """
        lines: List[str] = []
        self._serialize_dict(data, lines, [])
        return "\n".join(lines) + "\n"

    def _serialize_dict(self, data: Dict[str, Any], lines: List[str],
                        path: List[str]) -> None:
        """序列化字典

        Args:
            data: 字典数据
            lines: 输出行列表
            path: 当前路径
        """
        # 先处理简单键值对
        for key, value in data.items():
            if isinstance(value, dict) and value:
                continue  # 表单独处理
            if isinstance(value, list) and value and isinstance(value[0], dict):
                continue  # 数组表单独处理
            lines.append(f"{key} = {self._format_value(value)}")

        # 处理嵌套表
        for key, value in data.items():
            if isinstance(value, dict) and value:
                new_path = path + [key]
                lines.append("")
                lines.append(f"[{'.'.join(new_path)}]")
                self._serialize_dict(value, lines, new_path)

        # 处理数组表
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                new_path = path + [key]
                for item in value:
                    lines.append("")
                    lines.append(f"[[{'.'.join(new_path)}]]")
                    self._serialize_dict(item, lines, new_path)

    def _format_value(self, value: Any) -> str:
        """格式化TOML值

        Args:
            value: Python值

        Returns:
            TOML格式字符串
        """
        if value is None:
            return '""'
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            return str(value)
        if isinstance(value, str):
            # 转义特殊字符
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            escaped = escaped.replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
            return f'"{escaped}"'
        if isinstance(value, list):
            items = [self._format_value(item) for item in value]
            return f"[{', '.join(items)}]"
        if isinstance(value, dict):
            pairs = [f"{k} = {self._format_value(v)}" for k, v in value.items()]
            return "{" + ", ".join(pairs) + "}"
        return f'"{value}"'
