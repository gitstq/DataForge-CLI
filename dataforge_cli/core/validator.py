"""
JSON Schema验证器模块
=======================
提供简易的JSON Schema验证功能，支持常用的schema关键字。

支持的schema关键字:
    - type: 类型检查
    - required: 必填字段
    - properties: 对象属性定义
    - items: 数组元素定义
    - minimum/maximum: 数值范围
    - minLength/maxLength: 字符串长度范围
    - pattern: 正则模式
    - enum: 枚举值
    - const: 常量值
    - additionalProperties: 是否允许额外属性
    - minItems/maxItems: 数组长度范围
    - uniqueItems: 数组元素是否唯一
    - format: 格式验证（email, uri, datetime等）

使用示例:
    from dataforge_cli.core.validator import Validator

    schema = {
        "type": "object",
        "required": ["name", "age"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0}
        }
    }

    validator = Validator(schema)
    result = validator.validate({"name": "Alice", "age": 25})
    # result.valid == True
"""

import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class Validator:
    """JSON Schema简易验证器

    支持常用的JSON Schema Draft-07子集。
    """

    # 类型映射
    TYPE_MAP: Dict[str, Tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
        "null": (type(None),),
    }

    # 格式验证正则
    FORMAT_PATTERNS: Dict[str, str] = {
        "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        "uri": r'^https?://[^\s/$.?#].[^\s]*$',
        "url": r'^https?://[^\s/$.?#].[^\s]*$',
        "datetime": r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',
        "date": r'^\d{4}-\d{2}-\d{2}$',
        "time": r'^\d{2}:\d{2}:\d{2}$',
        "ipv4": r'^(\d{1,3}\.){3}\d{1,3}$',
        "ipv6": r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$',
        "hostname": r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$',
        "alpha": r'^[a-zA-Z]+$',
        "alphanumeric": r'^[a-zA-Z0-9]+$',
        "hex": r'^[0-9a-fA-F]+$',
        "uuid": r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$',
    }

    def __init__(self, schema: Dict[str, Any]):
        """初始化验证器

        Args:
            schema: JSON Schema定义
        """
        self.schema = schema
        self._custom_rules: Dict[str, Callable] = {}

    def add_rule(self, name: str, func: Callable) -> None:
        """添加自定义验证规则

        Args:
            name: 规则名称
            func: 验证函数，签名为 func(value, schema, path) -> List[str]
                  返回错误消息列表，空列表表示通过
        """
        self._custom_rules[name] = func

    def validate(self, data: Any) -> Dict[str, Any]:
        """验证数据是否符合schema

        Args:
            data: 要验证的数据

        Returns:
            验证结果字典，包含:
            - "valid": 是否通过验证
            - "errors": 错误列表
            - "warnings": 警告列表
        """
        errors: List[str] = []
        warnings: List[str] = []

        self._validate_recursive(data, self.schema, "", errors, warnings)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def validate_file(self, filepath: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """验证文件中的数据

        Args:
            filepath: 数据文件路径
            schema: Schema定义（为None时使用初始化时的schema）

        Returns:
            验证结果字典
        """
        from dataforge_cli.core.parser import Parser

        data = Parser.parse_file(filepath)
        schema = schema or self.schema
        return Validator(schema).validate(data)

    def generate_report(self, data: Any) -> str:
        """生成验证报告

        Args:
            data: 要验证的数据

        Returns:
            格式化的验证报告字符串
        """
        result = self.validate(data)

        lines: List[str] = ["=" * 50, "验证报告", "=" * 50, ""]

        if result["valid"]:
            lines.append("状态: 通过")
        else:
            lines.append(f"状态: 未通过 ({len(result['errors'])} 个错误)")

        if result["errors"]:
            lines.append("")
            lines.append("错误列表:")
            for i, error in enumerate(result["errors"], 1):
                lines.append(f"  {i}. {error}")

        if result["warnings"]:
            lines.append("")
            lines.append("警告列表:")
            for i, warning in enumerate(result["warnings"], 1):
                lines.append(f"  {i}. {warning}")

        lines.append("")
        lines.append("=" * 50)

        return "\n".join(lines)

    def _validate_recursive(self, data: Any, schema: Dict[str, Any],
                            path: str, errors: List[str],
                            warnings: List[str]) -> None:
        """递归验证数据

        Args:
            data: 当前数据
            schema: 当前schema
            path: 当前路径
            errors: 错误列表（累积）
            warnings: 警告列表（累积）
        """
        # 自定义规则
        for rule_name, rule_func in self._custom_rules.items():
            if rule_name in schema:
                rule_errors = rule_func(data, schema, path)
                errors.extend(rule_errors)

        # type 验证
        if "type" in schema:
            self._validate_type(data, schema["type"], path, errors)

        # enum 验证
        if "enum" in schema:
            self._validate_enum(data, schema["enum"], path, errors)

        # const 验证
        if "const" in schema:
            self._validate_const(data, schema["const"], path, errors)

        # 根据数据类型进行特定验证
        if isinstance(data, dict):
            self._validate_object(data, schema, path, errors, warnings)
        elif isinstance(data, list):
            self._validate_array(data, schema, path, errors, warnings)
        elif isinstance(data, str):
            self._validate_string(data, schema, path, errors)
        elif isinstance(data, (int, float)) and not isinstance(data, bool):
            self._validate_number(data, schema, path, errors)

        # format 验证
        if "format" in schema and isinstance(data, str):
            self._validate_format(data, schema["format"], path, errors)

    def _validate_type(self, data: Any, expected_type: Union[str, List[str]],
                       path: str, errors: List[str]) -> None:
        """验证数据类型

        Args:
            data: 数据
            expected_type: 期望类型（字符串或列表）
            path: 路径
            errors: 错误列表
        """
        if isinstance(expected_type, list):
            # 多类型
            type_match = any(
                self._check_type(data, t) for t in expected_type
            )
            if not type_match:
                display_path = path or "$"
                errors.append(
                    f"[{display_path}] 类型错误: 期望 {expected_type}，"
                    f"实际为 {type(data).__name__}"
                )
        else:
            if not self._check_type(data, expected_type):
                display_path = path or "$"
                errors.append(
                    f"[{display_path}] 类型错误: 期望 {expected_type}，"
                    f"实际为 {type(data).__name__}"
                )

    def _check_type(self, data: Any, expected_type: str) -> bool:
        """检查数据是否匹配指定类型

        Args:
            data: 数据
            expected_type: 期望类型名称

        Returns:
            是否匹配
        """
        if expected_type not in self.TYPE_MAP:
            return True  # 未知类型跳过检查

        expected_types = self.TYPE_MAP[expected_type]

        # 特殊处理：bool是int的子类，需要排除
        if expected_type == "integer" and isinstance(data, bool):
            return False
        if expected_type == "number" and isinstance(data, bool):
            return False

        return isinstance(data, expected_types)

    def _validate_enum(self, data: Any, enum_values: List[Any],
                       path: str, errors: List[str]) -> None:
        """验证枚举值

        Args:
            data: 数据
            enum_values: 允许的值列表
            path: 路径
            errors: 错误列表
        """
        if data not in enum_values:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 枚举值错误: 值 {data!r} 不在允许列表 {enum_values} 中"
            )

    def _validate_const(self, data: Any, const_value: Any,
                        path: str, errors: List[str]) -> None:
        """验证常量值

        Args:
            data: 数据
            const_value: 期望的常量值
            path: 路径
            errors: 错误列表
        """
        if data != const_value:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 常量值错误: 期望 {const_value!r}，实际为 {data!r}"
            )

    def _validate_object(self, data: Dict[str, Any], schema: Dict[str, Any],
                          path: str, errors: List[str], warnings: List[str]) -> None:
        """验证对象（字典）

        Args:
            data: 字典数据
            schema: Schema定义
            path: 路径
            errors: 错误列表
            warnings: 警告列表
        """
        # required 验证
        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    display_path = f"{path}.{field}" if path else field
                    errors.append(f"[{display_path}] 必填字段缺失: {field}")

        # properties 验证
        if "properties" in schema:
            for key, prop_schema in schema["properties"].items():
                if key in data:
                    new_path = f"{path}.{key}" if path else key
                    self._validate_recursive(
                        data[key], prop_schema, new_path, errors, warnings
                    )

        # additionalProperties 验证
        if "additionalProperties" in schema:
            allowed_keys = set(schema.get("properties", {}).keys())
            for key in data:
                if key not in allowed_keys:
                    if schema["additionalProperties"] is False:
                        display_path = f"{path}.{key}" if path else key
                        warnings.append(
                            f"[{display_path}] 额外属性不允许: {key}"
                        )
                    elif isinstance(schema["additionalProperties"], dict):
                        new_path = f"{path}.{key}" if path else key
                        self._validate_recursive(
                            data[key], schema["additionalProperties"],
                            new_path, errors, warnings
                        )

        # minProperties / maxProperties
        if "minProperties" in schema and len(data) < schema["minProperties"]:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 属性数量不足: 最少 {schema['minProperties']} 个，"
                f"实际 {len(data)} 个"
            )

        if "maxProperties" in schema and len(data) > schema["maxProperties"]:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 属性数量超限: 最多 {schema['maxProperties']} 个，"
                f"实际 {len(data)} 个"
            )

    def _validate_array(self, data: List[Any], schema: Dict[str, Any],
                        path: str, errors: List[str], warnings: List[str]) -> None:
        """验证数组

        Args:
            data: 列表数据
            schema: Schema定义
            path: 路径
            errors: 错误列表
            warnings: 警告列表
        """
        # items 验证
        if "items" in schema:
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                if isinstance(schema["items"], dict):
                    self._validate_recursive(
                        item, schema["items"], new_path, errors, warnings
                    )
                elif isinstance(schema["items"], list):
                    # 元组验证：每个位置有不同schema
                    if i < len(schema["items"]):
                        self._validate_recursive(
                            item, schema["items"][i], new_path, errors, warnings
                        )

        # minItems / maxItems
        if "minItems" in schema and len(data) < schema["minItems"]:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 数组长度不足: 最少 {schema['minItems']} 个，"
                f"实际 {len(data)} 个"
            )

        if "maxItems" in schema and len(data) > schema["maxItems"]:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 数组长度超限: 最多 {schema['maxItems']} 个，"
                f"实际 {len(data)} 个"
            )

        # uniqueItems
        if schema.get("uniqueItems") and len(data) != len(set(str(x) for x in data)):
            display_path = path or "$"
            errors.append(f"[{display_path}] 数组元素不唯一")

    def _validate_string(self, data: str, schema: Dict[str, Any],
                         path: str, errors: List[str]) -> None:
        """验证字符串

        Args:
            data: 字符串数据
            schema: Schema定义
            path: 路径
            errors: 错误列表
        """
        # minLength
        if "minLength" in schema and len(data) < schema["minLength"]:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 字符串长度不足: 最少 {schema['minLength']} 个字符，"
                f"实际 {len(data)} 个"
            )

        # maxLength
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 字符串长度超限: 最多 {schema['maxLength']} 个字符，"
                f"实际 {len(data)} 个"
            )

        # pattern
        if "pattern" in schema:
            if not re.search(schema["pattern"], data):
                display_path = path or "$"
                errors.append(
                    f"[{display_path}] 字符串不匹配模式: {schema['pattern']}"
                )

    def _validate_number(self, data: Union[int, float], schema: Dict[str, Any],
                         path: str, errors: List[str]) -> None:
        """验证数字

        Args:
            data: 数字数据
            schema: Schema定义
            path: 路径
            errors: 错误列表
        """
        # minimum
        if "minimum" in schema and data < schema["minimum"]:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 数值过小: 最小 {schema['minimum']}，实际 {data}"
            )

        # maximum
        if "maximum" in schema and data > schema["maximum"]:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 数值过大: 最大 {schema['maximum']}，实际 {data}"
            )

        # exclusiveMinimum
        if "exclusiveMinimum" in schema and data <= schema["exclusiveMinimum"]:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 数值不满足排他最小值: 必须 > {schema['exclusiveMinimum']}，实际 {data}"
            )

        # exclusiveMaximum
        if "exclusiveMaximum" in schema and data >= schema["exclusiveMaximum"]:
            display_path = path or "$"
            errors.append(
                f"[{display_path}] 数值不满足排他最大值: 必须 < {schema['exclusiveMaximum']}，实际 {data}"
            )

        # multipleOf
        if "multipleOf" in schema:
            if schema["multipleOf"] != 0 and data % schema["multipleOf"] != 0:
                display_path = path or "$"
                errors.append(
                    f"[{display_path}] 数值不是 {schema['multipleOf']} 的倍数"
                )

    def _validate_format(self, data: str, format_name: str,
                         path: str, errors: List[str]) -> None:
        """验证字符串格式

        Args:
            data: 字符串数据
            format_name: 格式名称
            path: 路径
            errors: 错误列表
        """
        if format_name in self.FORMAT_PATTERNS:
            pattern = self.FORMAT_PATTERNS[format_name]
            if not re.match(pattern, data):
                display_path = path or "$"
                errors.append(
                    f"[{display_path}] 格式验证失败: 不符合 {format_name} 格式"
                )
