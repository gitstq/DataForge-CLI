"""
JMESPath风格查询引擎模块
==========================
实现类JMESPath的查询语法，用于从JSON/YAML数据中提取信息。

支持的查询语法:
    - 点号访问: data.users[0].name
    - 数组索引: users[0], users[-1]
    - 数组切片: users[0:3]
    - 通配符: users[*].name
    - 过滤器: users[?age > 18]
    - 管道: users | [0].name
    - 多选: users[].name, age
    - 聚合: length(users), sum(users[].age)
    - 排序: sort_by(users, age)

使用示例:
    from dataforge_cli.core.query import QueryEngine

    data = {"users": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 18}]}
    engine = QueryEngine(data)

    # 点号访问
    result = engine.query("users[0].name")  # "Alice"

    # 通配符
    result = engine.query("users[*].name")  # ["Alice", "Bob"]

    # 过滤器
    result = engine.query("users[?age > 18]")  # [{"name": "Alice", "age": 25}]

    # 聚合
    result = engine.query("length(users)")  # 2
"""

import operator
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class QueryEngine:
    """JMESPath风格查询引擎

    提供类JMESPath的查询语法，用于从嵌套数据结构中提取信息。
    """

    # 比较运算符映射
    _COMPARISON_OPS: Dict[str, Callable] = {
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le,
        "=": operator.eq,
    }

    # 聚合函数映射
    _AGGREGATE_FUNCS: Dict[str, Callable] = {
        "length": lambda x: len(x) if hasattr(x, "__len__") else 0,
        "count": lambda x: len(x) if hasattr(x, "__len__") else 0,
        "sum": lambda x: sum(x) if x else 0,
        "avg": lambda x: sum(x) / len(x) if x else 0,
        "min": lambda x: min(x) if x else None,
        "max": lambda x: max(x) if x else None,
        "first": lambda x: x[0] if x else None,
        "last": lambda x: x[-1] if x else None,
        "keys": lambda x: list(x.keys()) if isinstance(x, dict) else [],
        "values": lambda x: list(x.values()) if isinstance(x, dict) else [],
        "type": lambda x: type(x).__name__,
        "flatten": lambda x: QueryEngine._flatten(x),
        "reverse": lambda x: list(reversed(x)) if isinstance(x, list) else x,
        "unique": lambda x: list(dict.fromkeys(x)) if isinstance(x, list) else x,
        "sort": lambda x: sorted(x) if isinstance(x, list) else x,
        "join": lambda x: ",".join(str(i) for i in x) if isinstance(x, list) else str(x),
        "to_string": lambda x: str(x),
        "to_number": lambda x: QueryEngine._to_number(x),
    }

    def __init__(self, data: Any):
        """初始化查询引擎

        Args:
            data: 要查询的数据（通常是dict或list）
        """
        self.data = data

    def query(self, expression: str) -> Any:
        """执行查询表达式

        Args:
            expression: JMESPath风格查询表达式

        Returns:
            查询结果

        Raises:
            ValueError: 查询语法错误

        使用示例:
            engine = QueryEngine({"users": [{"name": "Alice"}]})
            engine.query("users[0].name")  # "Alice"
        """
        expression = expression.strip()
        if not expression:
            return self.data

        # 处理管道操作
        if "|" in expression:
            return self._execute_pipeline(expression)

        # 处理函数调用
        if self._is_function_call(expression):
            return self._execute_function(expression)

        # 处理多选表达式 users[].name, age
        if "," in expression and "[" in expression:
            return self._execute_multi_select(expression)

        # 处理普通路径表达式
        return self._resolve_path(expression, self.data)

    def _execute_pipeline(self, expression: str) -> Any:
        """执行管道操作

        管道操作符 | 将前一个查询的结果传递给下一个查询。

        Args:
            expression: 包含管道的表达式

        Returns:
            管道最终结果
        """
        # 分割管道（注意不要分割函数参数中的逗号）
        parts = self._split_pipeline(expression)
        result = self.data
        for part in parts:
            part = part.strip()
            if not part:
                continue
            result = self._resolve_path(part, result)
        return result

    def _split_pipeline(self, expression: str) -> List[str]:
        """分割管道表达式

        Args:
            expression: 管道表达式

        Returns:
            分割后的部分列表
        """
        parts: List[str] = []
        current = ""
        depth = 0
        in_single = False
        in_double = False

        for ch in expression:
            if ch == '"' and not in_single:
                in_double = not in_double
                current += ch
            elif ch == "'" and not in_double:
                in_single = not in_single
                current += ch
            elif ch in ("(", "[", "{") and not in_single and not in_double:
                depth += 1
                current += ch
            elif ch in (")", "]", "}") and not in_single and not in_double:
                depth -= 1
                current += ch
            elif ch == "|" and depth == 0 and not in_single and not in_double:
                parts.append(current)
                current = ""
            else:
                current += ch

        if current.strip():
            parts.append(current)

        return parts

    def _is_function_call(self, expression: str) -> bool:
        """判断表达式是否为函数调用

        Args:
            expression: 查询表达式

        Returns:
            是否为函数调用
        """
        return bool(re.match(r'^[a-zA-Z_]\w*\s*\(', expression))

    def _execute_function(self, expression: str) -> Any:
        """执行函数调用

        支持内置聚合函数和排序函数。

        Args:
            expression: 函数调用表达式

        Returns:
            函数执行结果
        """
        # 解析函数名和参数
        match = re.match(r'^(\w+)\s*\((.*)\)$', expression, re.DOTALL)
        if not match:
            raise ValueError(f"无效的函数调用语法: {expression}")

        func_name = match.group(1)
        args_str = match.group(2).strip()

        # 特殊函数：sort_by
        if func_name == "sort_by":
            return self._execute_sort_by(args_str)

        # 特殊函数：contains
        if func_name == "contains":
            return self._execute_contains(args_str)

        # 特殊函数：not_null / max_by / min_by
        if func_name in ("not_null", "max_by", "min_by", "starts_with", "ends_with"):
            return self._execute_special_function(func_name, args_str)

        # 聚合函数
        if func_name in self._AGGREGATE_FUNCS:
            # 解析参数
            arg_value = self._resolve_path(args_str, self.data)
            return self._AGGREGATE_FUNCS[func_name](arg_value)

        raise ValueError(f"未知函数: {func_name}")

    def _execute_sort_by(self, args_str: str) -> Any:
        """执行sort_by函数

        Args:
            args_str: 函数参数字符串

        Returns:
            排序后的列表
        """
        # 解析参数: sort_by(path, key)
        parts = self._split_function_args(args_str)
        if len(parts) != 2:
            raise ValueError(f"sort_by需要2个参数，得到{len(parts)}个")

        data = self._resolve_path(parts[0].strip(), self.data)
        sort_key = parts[1].strip().strip("'\"")

        if not isinstance(data, list):
            return data

        try:
            return sorted(data, key=lambda x: x.get(sort_key, None) if isinstance(x, dict) else x)
        except TypeError:
            return data

    def _execute_contains(self, args_str: str) -> bool:
        """执行contains函数

        Args:
            args_str: 函数参数字符串

        Returns:
            是否包含
        """
        parts = self._split_function_args(args_str)
        if len(parts) != 2:
            raise ValueError(f"contains需要2个参数，得到{len(parts)}个")

        collection = self._resolve_path(parts[0].strip(), self.data)
        item = self._resolve_path(parts[1].strip(), self.data)

        if isinstance(collection, (list, tuple, str)):
            return item in collection
        if isinstance(collection, dict):
            return item in collection
        return False

    def _execute_special_function(self, func_name: str, args_str: str) -> Any:
        """执行特殊函数

        Args:
            func_name: 函数名
            args_str: 参数字符串

        Returns:
            函数结果
        """
        parts = self._split_function_args(args_str)

        if func_name == "not_null":
            for part in parts:
                val = self._resolve_path(part.strip(), self.data)
                if val is not None:
                    return val
            return None

        if func_name == "max_by":
            if len(parts) != 2:
                raise ValueError("max_by需要2个参数")
            data = self._resolve_path(parts[0].strip(), self.data)
            key = parts[1].strip().strip("'\"")
            if isinstance(data, list):
                return max(data, key=lambda x: x.get(key, None) if isinstance(x, dict) else x)
            return data

        if func_name == "min_by":
            if len(parts) != 2:
                raise ValueError("min_by需要2个参数")
            data = self._resolve_path(parts[0].strip(), self.data)
            key = parts[1].strip().strip("'\"")
            if isinstance(data, list):
                return min(data, key=lambda x: x.get(key, None) if isinstance(x, dict) else x)
            return data

        if func_name == "starts_with":
            if len(parts) != 2:
                raise ValueError("starts_with需要2个参数")
            s = self._resolve_path(parts[0].strip(), self.data)
            prefix = self._resolve_path(parts[1].strip(), self.data)
            return str(s).startswith(str(prefix)) if s is not None else False

        if func_name == "ends_with":
            if len(parts) != 2:
                raise ValueError("ends_with需要2个参数")
            s = self._resolve_path(parts[0].strip(), self.data)
            suffix = self._resolve_path(parts[1].strip(), self.data)
            return str(s).endswith(str(suffix)) if s is not None else False

        raise ValueError(f"未知函数: {func_name}")

    def _split_function_args(self, args_str: str) -> List[str]:
        """分割函数参数（处理嵌套括号）

        Args:
            args_str: 参数字符串

        Returns:
            参数列表
        """
        args: List[str] = []
        current = ""
        depth = 0
        in_single = False
        in_double = False

        for ch in args_str:
            if ch == '"' and not in_single:
                in_double = not in_double
                current += ch
            elif ch == "'" and not in_double:
                in_single = not in_single
                current += ch
            elif ch in ("(", "[", "{") and not in_single and not in_double:
                depth += 1
                current += ch
            elif ch in (")", "]", "}") and not in_single and not in_double:
                depth -= 1
                current += ch
            elif ch == "," and depth == 0 and not in_single and not in_double:
                args.append(current)
                current = ""
            else:
                current += ch

        if current.strip():
            args.append(current)

        return args

    def _execute_multi_select(self, expression: str) -> Any:
        """执行多选查询

        处理类似 users[].name, age 的多选表达式。

        Args:
            expression: 多选表达式

        Returns:
            多选结果
        """
        # 查找 [] 位置
        bracket_end = expression.index("]")
        base_path = expression[:bracket_end + 1]
        fields_str = expression[bracket_end + 1:].strip()

        if fields_str.startswith(","):
            fields_str = fields_str[1:].strip()

        base_data = self._resolve_path(base_path, self.data)

        if not isinstance(base_data, list):
            return base_data

        # 多选字段
        fields = [f.strip() for f in fields_str.split(",")]
        result = []
        for item in base_data:
            row = {}
            for field in fields:
                field = field.strip()
                if field:
                    row[field] = self._resolve_path(field, item)
            result.append(row)
        return result

    def _resolve_path(self, path: str, data: Any) -> Any:
        """解析路径表达式

        支持点号访问、数组索引、切片、通配符、过滤器。

        Args:
            path: 路径表达式
            data: 当前数据上下文

        Returns:
            路径对应的值
        """
        if data is None:
            return None

        path = path.strip()
        if not path or path == ".":
            return data

        # 处理函数调用
        if self._is_function_call(path):
            return self._execute_function_on(path, data)

        # 处理根级别的数组索引 [0], [*], [?expr], [start:end]
        # 只有当整个路径就是一个方括号表达式时才直接处理
        if path.startswith("[") and self._is_single_bracket(path):
            return self._resolve_bracket(path, data)

        # 分割路径为段
        segments = self._split_path(path)

        current = data
        idx = 0
        while idx < len(segments):
            if current is None:
                return None
            segment = segments[idx]
            current = self._resolve_segment(segment, current)
            # 如果通配符/过滤器返回了列表，且还有后续段，需要对每个元素继续解析
            if isinstance(current, list) and idx < len(segments) - 1:
                # 只在当前段是通配符或过滤器时自动展开
                is_wildcard_or_filter = (
                    segment == "[*]" or
                    (segment.startswith("[?") and segment.endswith("]"))
                )
                if is_wildcard_or_filter:
                    next_segment = segments[idx + 1]
                    current = [self._resolve_segment(next_segment, item) for item in current]
                    idx += 2  # 跳过当前段和已展开的下一个段
                    continue
            idx += 1

        return current

    def _execute_function_on(self, expression: str, data: Any) -> Any:
        """在指定数据上执行函数

        Args:
            expression: 函数调用表达式
            data: 输入数据

        Returns:
            函数结果
        """
        match = re.match(r'^(\w+)\s*\((.*)\)$', expression, re.DOTALL)
        if not match:
            return None

        func_name = match.group(1)
        args_str = match.group(2).strip()

        if func_name == "sort_by":
            parts = self._split_function_args(args_str)
            if len(parts) != 2:
                return data
            sort_key = parts[1].strip().strip("'\"")
            if isinstance(data, list):
                try:
                    return sorted(data, key=lambda x: x.get(sort_key, None) if isinstance(x, dict) else x)
                except TypeError:
                    return data
            return data

        if func_name in self._AGGREGATE_FUNCS:
            return self._AGGREGATE_FUNCS[func_name](data)

        return data

    def _split_path(self, path: str) -> List[str]:
        """分割路径为段列表

        将 "users[0].name.age" 分割为 ["users[0]", "name", "age"]

        Args:
            path: 路径字符串

        Returns:
            路径段列表
        """
        segments: List[str] = []
        current = ""
        i = 0

        while i < len(path):
            ch = path[i]

            if ch == ".":
                if current:
                    segments.append(current)
                    current = ""
                i += 1
            elif ch == "[":
                if current:
                    segments.append(current)
                    current = ""
                # 找到匹配的 ]
                depth = 1
                j = i + 1
                while j < len(path) and depth > 0:
                    if path[j] == "[":
                        depth += 1
                    elif path[j] == "]":
                        depth -= 1
                    j += 1
                segments.append(path[i:j])
                i = j
            elif ch == '"':
                # 引号包裹的键名
                j = i + 1
                while j < len(path) and path[j] != '"':
                    if path[j] == "\\":
                        j += 1
                    j += 1
                current += path[i:j + 1]
                i = j + 1
            else:
                current += ch
                i += 1

        if current:
            segments.append(current)

        return segments

    def _resolve_segment(self, segment: str, data: Any) -> Any:
        """解析单个路径段

        Args:
            segment: 路径段
            data: 当前数据

        Returns:
            解析后的值
        """
        if data is None:
            return None

        # 数组/字典索引: [0], [*], [?expr], [start:end]
        if segment.startswith("[") and segment.endswith("]"):
            return self._resolve_bracket(segment, data)

        # 点号访问
        if isinstance(data, dict):
            # 通配符 * 返回所有值
            if segment == "*":
                return list(data.values())
            # 尝试直接键名
            if segment in data:
                return data[segment]
            # 尝试去除引号
            key = segment.strip("'\"")
            if key in data:
                return data[key]
            return None

        if isinstance(data, (list, tuple)):
            # 尝试数字索引
            try:
                idx = int(segment)
                if -len(data) <= idx < len(data):
                    return data[idx]
            except (ValueError, IndexError):
                pass
            return None

        return None

    def _is_single_bracket(self, path: str) -> bool:
        """判断路径是否只包含一个方括号表达式

        Args:
            path: 路径字符串

        Returns:
            是否为单个方括号表达式
        """
        depth = 0
        for i, ch in enumerate(path):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0 and i == len(path) - 1:
                    return True
        return False

    def _resolve_bracket(self, bracket: str, data: Any) -> Any:
        """解析方括号表达式

        支持的格式:
        - [0] 数字索引
        - [-1] 负数索引
        - [*] 通配符
        - [?expr] 过滤器
        - [0:3] 切片

        Args:
            bracket: 方括号表达式（含方括号）
            data: 当前数据

        Returns:
            解析后的值
        """
        inner = bracket[1:-1].strip()

        # 通配符 [*]
        if inner == "*":
            if isinstance(data, (list, tuple)):
                return list(data)
            if isinstance(data, dict):
                return list(data.values())
            return data

        # 过滤器 [?expr]
        if inner.startswith("?"):
            return self._resolve_filter(inner[1:], data)

        # 切片 [start:end] 或 [start:end:step]
        if ":" in inner:
            return self._resolve_slice(inner, data)

        # 数字索引
        try:
            idx = int(inner)
            if isinstance(data, (list, tuple)):
                if -len(data) <= idx < len(data):
                    return data[idx]
                return None
        except ValueError:
            pass

        # 字符串键名
        key = inner.strip("'\"")
        if isinstance(data, dict) and key in data:
            return data[key]

        return None

    def _resolve_filter(self, filter_expr: str, data: Any) -> Any:
        """解析过滤器表达式

        支持的格式:
        - age > 18
        - name == "Alice"
        - type == "admin"

        Args:
            filter_expr: 过滤器表达式（不含?前缀）
            data: 当前数据（应为列表）

        Returns:
            过滤后的列表
        """
        if not isinstance(data, list):
            return []

        # 解析比较表达式
        result = []
        for item in data:
            if self._evaluate_filter(filter_expr, item):
                result.append(item)

        return result

    def _evaluate_filter(self, filter_expr: str, item: Any) -> bool:
        """评估单个过滤条件

        Args:
            filter_expr: 过滤表达式
            item: 当前数据项

        Returns:
            是否满足条件
        """
        # 尝试匹配比较运算符
        for op in [">=", "<=", "!=", "==", ">", "<", "="]:
            # 使用正则匹配，避免在字符串内误匹配
            pattern = rf'^(.+?)\s*{re.escape(op)}\s*(.+)$'
            match = re.match(pattern, filter_expr)
            if match:
                left_expr = match.group(1).strip()
                right_expr = match.group(2).strip()

                left_val = self._resolve_path(left_expr, item)
                right_val = self._parse_literal(right_expr)

                # 如果右侧不是字面量，尝试从item中解析
                if right_val is None and right_expr:
                    right_val = self._resolve_path(right_expr, item)

                if left_val is None or right_val is None:
                    # 处理None比较
                    if op == "==" or op == "=":
                        return left_val == right_val
                    if op == "!=":
                        return left_val != right_val
                    return False

                try:
                    cmp_func = self._COMPARISON_OPS.get(op, operator.eq)
                    return cmp_func(left_val, right_val)
                except (TypeError, ValueError):
                    return False

        # 尝试布尔值检查（如 exists）
        if filter_expr.strip() == "exists()":
            return item is not None

        # 尝试存在性检查
        val = self._resolve_path(filter_expr.strip(), item)
        return bool(val)

    def _parse_literal(self, value: str) -> Any:
        """解析字面量值

        Args:
            value: 字面量字符串

        Returns:
            解析后的Python值
        """
        value = value.strip()

        # 布尔值
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False

        # null
        if value.lower() == "null" or value == "~":
            return None

        # 字符串（引号包裹）
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        # 数字
        try:
            if "." in value or "e" in value.lower():
                return float(value)
            return int(value)
        except ValueError:
            pass

        return None

    def _resolve_slice(self, slice_expr: str, data: Any) -> Any:
        """解析切片表达式

        Args:
            slice_expr: 切片表达式（如 "0:3", "1:", ":3", "::2"）
            data: 当前数据

        Returns:
            切片后的列表
        """
        if not isinstance(data, (list, tuple)):
            return data

        parts = slice_expr.split(":")
        start = int(parts[0]) if parts[0].strip() else None
        end = int(parts[1]) if len(parts) > 1 and parts[1].strip() else None
        step = int(parts[2]) if len(parts) > 2 and parts[2].strip() else None

        return list(data[start:end:step])

    @staticmethod
    def _flatten(data: Any) -> List[Any]:
        """展平嵌套列表

        Args:
            data: 可能嵌套的列表

        Returns:
            展平后的列表
        """
        result: List[Any] = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, list):
                    result.extend(QueryEngine._flatten(item))
                else:
                    result.append(item)
        return result

    @staticmethod
    def _to_number(value: Any) -> Any:
        """尝试将值转为数字

        Args:
            value: 输入值

        Returns:
            数字或原始值
        """
        if isinstance(value, (int, float)):
            return value
        try:
            if "." in str(value):
                return float(value)
            return int(value)
        except (ValueError, TypeError):
            return None
