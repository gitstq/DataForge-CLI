"""
模板渲染引擎模块
================
提供简单的模板渲染功能，支持变量替换、循环、条件、包含和过滤器。

支持的语法:
    - {{ variable }} - 变量替换
    - {% for item in list %} ... {% endfor %} - 循环
    - {% if condition %} ... {% elif %} ... {% else %} ... {% endif %} - 条件
    - {% include "file" %} - 包含文件
    - {{ expression | filter }} - 过滤器
    - {# comment #} - 注释

使用示例:
    from dataforge_cli.core.template import TemplateEngine

    # 基本变量替换
    tpl = TemplateEngine("Hello, {{ name }}!")
    result = tpl.render({"name": "World"})  # "Hello, World!"

    # 循环
    tpl = TemplateEngine("{% for item in items %}- {{ item }}\\n{% endfor %}")
    result = tpl.render({"items": ["a", "b", "c"]})

    # 过滤器
    tpl = TemplateEngine("{{ name | upper }}")
    result = tpl.render({"name": "hello"})  # "HELLO"
"""

import os
import re
from typing import Any, Callable, Dict, List, Optional, Tuple


class TemplateEngine:
    """模板渲染引擎

    支持变量替换、循环、条件、包含和过滤器。
    """

    # 内置过滤器映射
    FILTERS: Dict[str, Callable] = {
        "upper": lambda x: str(x).upper(),
        "lower": lambda x: str(x).lower(),
        "capitalize": lambda x: str(x).capitalize(),
        "title": lambda x: str(x).title(),
        "strip": lambda x: str(x).strip(),
        "lstrip": lambda x: str(x).lstrip(),
        "rstrip": lambda x: str(x).rstrip(),
        "default": lambda x, d="": x if x is not None else d,
        "d": lambda x, d="": x if x is not None else d,
        "length": lambda x: len(x) if hasattr(x, "__len__") else 0,
        "len": lambda x: len(x) if hasattr(x, "__len__") else 0,
        "count": lambda x: len(x) if hasattr(x, "__len__") else 0,
        "join": lambda x, sep=",": sep.join(str(i) for i in x) if isinstance(x, (list, tuple)) else str(x),
        "sort": lambda x: sorted(x) if isinstance(x, list) else x,
        "reverse": lambda x: list(reversed(x)) if isinstance(x, list) else str(x)[::-1],
        "unique": lambda x: list(dict.fromkeys(x)) if isinstance(x, list) else x,
        "first": lambda x: x[0] if isinstance(x, (list, tuple)) and x else None,
        "last": lambda x: x[-1] if isinstance(x, (list, tuple)) and x else None,
        "truncate": lambda x, n=50: str(x)[:n] + "..." if len(str(x)) > n else str(x),
        "round": lambda x, n=2: round(float(x), n) if x is not None else None,
        "int": lambda x: int(float(x)) if x is not None else 0,
        "float": lambda x: float(x) if x is not None else 0.0,
        "str": lambda x: str(x) if x is not None else "",
        "string": lambda x: str(x) if x is not None else "",
        "abs": lambda x: abs(x) if x is not None else None,
        "max": lambda x: max(x) if isinstance(x, (list, tuple)) and x else None,
        "min": lambda x: min(x) if isinstance(x, (list, tuple)) and x else None,
        "sum": lambda x: sum(x) if isinstance(x, (list, tuple)) else 0,
        "avg": lambda x: sum(x) / len(x) if isinstance(x, (list, tuple)) and x else 0,
        "replace": lambda x, old="", new="": str(x).replace(old, new),
        "split": lambda x, sep=" ": str(x).split(sep),
        "trim": lambda x: str(x).strip(),
        "b64encode": lambda x: TemplateEngine._b64_encode(str(x)),
        "b64decode": lambda x: TemplateEngine._b64_decode(str(x)),
        "json": lambda x: __import__("json").dumps(x, ensure_ascii=False),
        "yaml": lambda x: __import__("dataforge_cli.core.parser", fromlist=["Parser"]).Parser.serialize_yaml(x),
        "pprint": lambda x: __import__("json").dumps(x, indent=2, ensure_ascii=False),
        "indent": lambda x, n=2: (" " * n).join(str(x).split("\n")),
        "center": lambda x, w=40: str(x).center(w),
        "ljust": lambda x, w=40: str(x).ljust(w),
        "rjust": lambda x, w=40: str(x).rjust(w),
        "list": lambda x: list(x) if not isinstance(x, list) else x,
        "dict": lambda x: dict(x) if not isinstance(x, dict) else x,
        "keys": lambda x: list(x.keys()) if isinstance(x, dict) else [],
        "values": lambda x: list(x.values()) if isinstance(x, dict) else [],
        "items": lambda x: list(x.items()) if isinstance(x, dict) else [],
        "type": lambda x: type(x).__name__,
        "bool": lambda x: bool(x),
        "not": lambda x: not x,
        "yesno": lambda x: "yes" if x else "no",
        "pluralize": lambda x, s="", p="s": p if (isinstance(x, (list, tuple)) and len(x) != 1) or (isinstance(x, (int, float)) and x != 1) else s,
    }

    def __init__(self, template: str, template_dir: Optional[str] = None):
        """初始化模板引擎

        Args:
            template: 模板字符串
            template_dir: 模板文件目录（用于{% include %}指令）
        """
        self.template = template
        self.template_dir = template_dir
        self._custom_filters: Dict[str, Callable] = {}

    def add_filter(self, name: str, func: Callable) -> None:
        """添加自定义过滤器

        Args:
            name: 过滤器名称
            func: 过滤器函数
        """
        self._custom_filters[name] = func

    def render(self, data: Dict[str, Any], **extra_context) -> str:
        """渲染模板

        Args:
            data: 模板数据上下文
            **extra_context: 额外的上下文变量

        Returns:
            渲染后的字符串
        """
        context = dict(data)
        context.update(extra_context)

        # 先处理注释
        result = self._remove_comments(self.template)

        # 处理包含指令
        result = self._process_includes(result)

        # 处理控制结构（循环和条件）
        result = self._process_control_structures(result, context)

        # 处理变量替换（最后处理，避免替换控制结构中的变量）
        result = self._process_variables(result, context)

        return result

    def render_file(self, filepath: str, data: Dict[str, Any], **extra_context) -> str:
        """从文件加载模板并渲染

        Args:
            filepath: 模板文件路径
            data: 模板数据上下文
            **extra_context: 额外的上下文变量

        Returns:
            渲染后的字符串
        """
        from dataforge_cli.utils.file_io import FileIO

        template = FileIO.read(filepath)
        self.template = template
        if self.template_dir is None:
            self.template_dir = os.path.dirname(os.path.abspath(filepath))

        return self.render(data, **extra_context)

    def _remove_comments(self, text: str) -> str:
        """移除模板注释 {# comment #}

        Args:
            text: 模板文本

        Returns:
            去除注释后的文本
        """
        return re.sub(r'\{#.*?#\}', '', text, flags=re.DOTALL)

    def _process_includes(self, text: str) -> str:
        """处理包含指令 {% include "file" %}

        Args:
            text: 模板文本

        Returns:
            处理包含后的文本
        """
        def replace_include(match: re.Match) -> str:
            filename = match.group(1).strip().strip("\"'")
            if self.template_dir:
                filepath = os.path.join(self.template_dir, filename)
            else:
                filepath = filename

            try:
                from dataforge_cli.utils.file_io import FileIO
                return FileIO.read(filepath)
            except FileNotFoundError:
                return f"<!-- 包含文件未找到: {filename} -->"

        return re.sub(r'\{%\s*include\s+[\'"](.+?)[\'"]\s*%\}', replace_include, text)

    def _process_control_structures(self, text: str, context: Dict[str, Any]) -> str:
        """处理控制结构（for循环和if条件）

        Args:
            text: 模板文本
            context: 数据上下文

        Returns:
            处理后的文本
        """
        result = text

        # 处理for循环
        while "{%" in result:
            new_result = self._process_for_loops(result, context)
            if new_result == result:
                break
            result = new_result

        # 处理if条件
        while "{%" in result:
            new_result = self._process_if_conditions(result, context)
            if new_result == result:
                break
            result = new_result

        return result

    def _process_for_loops(self, text: str, context: Dict[str, Any]) -> str:
        """处理for循环结构

        Args:
            text: 模板文本
            context: 数据上下文

        Returns:
            处理后的文本
        """
        pattern = r'\{%\s*for\s+(\w+)\s+in\s+(.+?)\s*%\}(.*?)\{%\s*endfor\s*%\}'
        match = re.search(pattern, text, re.DOTALL)

        if not match:
            return text

        var_name = match.group(1)
        iterable_expr = match.group(2).strip()
        body = match.group(3)

        # 获取可迭代对象
        iterable = self._evaluate_expression(iterable_expr, context)

        if not iterable:
            return text[:match.start()] + text[match.end():]

        # 渲染循环体
        rendered_parts: List[str] = []
        for i, item in enumerate(iterable):
            loop_context = dict(context)
            loop_context[var_name] = item
            loop_context["loop"] = {
                "index": i + 1,
                "index0": i,
                "first": i == 0,
                "last": i == len(iterable) - 1,
                "length": len(iterable),
                "revindex": len(iterable) - i,
                "revindex0": len(iterable) - i - 1,
            }
            rendered_body = self._process_variables(body, loop_context)
            rendered_parts.append(rendered_body)

        return text[:match.start()] + "".join(rendered_parts) + text[match.end():]

    def _process_if_conditions(self, text: str, context: Dict[str, Any]) -> str:
        """处理if条件结构

        Args:
            text: 模板文本
            context: 数据上下文

        Returns:
            处理后的文本
        """
        # 匹配 if/elif/else/endif 结构
        pattern = (
            r'\{%\s*if\s+(.+?)\s*%\}'
            r'(.*?)'
            r'(?:'
            r'\{%\s*elif\s+(.+?)\s*%\}(.*?)'
            r')*'
            r'(?:\{%\s*else\s*%\}(.*?))?'
            r'\{%\s*endif\s*%\}'
        )

        match = re.search(pattern, text, re.DOTALL)
        if not match:
            return text

        # 提取所有条件和内容
        full_match = match.group(0)
        conditions: List[Tuple[str, str]] = []

        # 提取if条件
        if_condition = match.group(1).strip()
        if_body = match.group(2)
        conditions.append((if_condition, if_body))

        # 提取elif条件
        elif_pattern = r'\{%\s*elif\s+(.+?)\s*%\}(.*?)(?=\{%\s*(?:elif|else|endif)\s*%\})'
        elif_matches = re.findall(elif_pattern, full_match, re.DOTALL)
        for cond, body in elif_matches:
            conditions.append((cond.strip(), body))

        # 提取else内容
        else_pattern = r'\{%\s*else\s*%\}(.*?)(?=\{%\s*endif\s*%\})'
        else_match = re.search(else_pattern, full_match, re.DOTALL)
        else_body = else_match.group(1) if else_match else ""

        # 评估条件
        result_body = ""
        for condition, body in conditions:
            if self._evaluate_condition(condition, context):
                result_body = body
                break
        else:
            result_body = else_body

        return text[:match.start()] + result_body + text[match.end():]

    def _process_variables(self, text: str, context: Dict[str, Any]) -> str:
        """处理变量替换 {{ variable }} 和 {{ expression | filter }}

        Args:
            text: 模板文本
            context: 数据上下文

        Returns:
            替换后的文本
        """
        pattern = r'\{\{(.*?)\}\}'

        def replace_var(match: re.Match) -> str:
            expr = match.group(1).strip()

            # 处理过滤器
            value = self._apply_filters(expr, context)
            if value is None:
                return ""

            return str(value)

        return re.sub(pattern, replace_var, text)

    def _apply_filters(self, expr: str, context: Dict[str, Any]) -> Any:
        """应用过滤器链

        Args:
            expr: 表达式（可能包含过滤器）
            context: 数据上下文

        Returns:
            过滤后的值
        """
        # 分割表达式和过滤器
        parts = expr.split("|")

        # 第一部分是变量表达式
        value = self._evaluate_expression(parts[0].strip(), context)

        # 应用过滤器链
        for filter_expr in parts[1:]:
            filter_expr = filter_expr.strip()
            value = self._apply_single_filter(value, filter_expr)

        return value

    def _apply_single_filter(self, value: Any, filter_expr: str) -> Any:
        """应用单个过滤器

        Args:
            value: 输入值
            filter_expr: 过滤器表达式（如 "upper", "truncate:50", "default:N/A"）

        Returns:
            过滤后的值
        """
        # 解析过滤器名和参数
        if ":" in filter_expr:
            filter_name, args_str = filter_expr.split(":", 1)
            filter_name = filter_name.strip()
            args = [a.strip().strip("\"'") for a in args_str.split(",")]
        else:
            filter_name = filter_expr.strip()
            args = []

        # 查找过滤器函数
        all_filters = {**self.FILTERS, **self._custom_filters}
        filter_func = all_filters.get(filter_name)

        if filter_func is None:
            return value

        try:
            if args:
                return filter_func(value, *args)
            return filter_func(value)
        except (TypeError, ValueError):
            return value

    def _evaluate_expression(self, expr: str, context: Dict[str, Any]) -> Any:
        """评估表达式，获取值

        支持点号访问、数组索引、字面量。

        Args:
            expr: 表达式字符串
            context: 数据上下文

        Returns:
            表达式的值
        """
        expr = expr.strip()

        # 字符串字面量
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # 数字字面量
        try:
            if "." in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # 布尔字面量
        if expr.lower() == "true":
            return True
        if expr.lower() == "false":
            return False
        if expr.lower() in ("null", "none"):
            return None

        # 变量访问（支持点号和索引）
        return self._resolve_variable(expr, context)

    def _resolve_variable(self, expr: str, context: Dict[str, Any]) -> Any:
        """解析变量路径

        将 "user.name" 或 "users[0].name" 解析为对应的值。

        Args:
            expr: 变量路径表达式
            context: 数据上下文

        Returns:
            变量的值
        """
        # 分割路径
        parts = re.split(r'\.(?![^\[]*\])', expr)

        current: Any = context
        for part in parts:
            if current is None:
                return None

            # 处理数组索引
            if "[" in part:
                key, _, index_str = part.partition("[")
                index_str = index_str.rstrip("]")

                if key:
                    if isinstance(current, dict):
                        current = current.get(key)
                    else:
                        return None

                if current is None:
                    return None

                try:
                    idx = int(index_str)
                    if isinstance(current, (list, tuple)) and -len(current) <= idx < len(current):
                        current = current[idx]
                    else:
                        return None
                except ValueError:
                    # 字符串键
                    if isinstance(current, dict):
                        current = current.get(index_str)
                    else:
                        return None
            else:
                if isinstance(current, dict):
                    current = current.get(part)
                elif isinstance(current, (list, tuple)):
                    try:
                        current = current[int(part)]
                    except (ValueError, IndexError):
                        return None
                else:
                    return None

        return current

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """评估条件表达式

        支持简单的比较运算和布尔值。

        Args:
            condition: 条件表达式
            context: 数据上下文

        Returns:
            条件是否为真
        """
        condition = condition.strip()

        # 比较运算符
        for op in [">=", "<=", "!=", "==", ">", "<"]:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    left = self._evaluate_expression(parts[0].strip(), context)
                    right = self._evaluate_expression(parts[1].strip(), context)
                    try:
                        if op == ">=":
                            return left >= right
                        elif op == "<=":
                            return left <= right
                        elif op == "!=":
                            return left != right
                        elif op == "==":
                            return left == right
                        elif op == ">":
                            return left > right
                        elif op == "<":
                            return left < right
                    except TypeError:
                        return False

        # not 运算
        if condition.startswith("not "):
            value = self._evaluate_expression(condition[4:].strip(), context)
            return not bool(value)

        # 布尔值检查
        value = self._evaluate_expression(condition, context)
        return bool(value)

    @staticmethod
    def _b64_encode(text: str) -> str:
        """Base64编码"""
        import base64
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def _b64_decode(text: str) -> str:
        """Base64解码"""
        import base64
        try:
            return base64.b64decode(text.encode()).decode()
        except Exception:
            return text
