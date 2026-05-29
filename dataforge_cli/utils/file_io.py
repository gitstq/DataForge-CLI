"""
文件读写工具模块
================
提供安全的文件读写操作，支持自动检测文件编码和格式。
不依赖任何第三方库。

使用示例:
    from dataforge_cli.utils.file_io import FileIO

    # 读取文件
    data = FileIO.read("data.json")

    # 写入文件
    FileIO.write("output.json", content)

    # 检测文件格式
    fmt = FileIO.detect_format("data.yaml")  # 返回 "yaml"
"""

import json
import os
import sys
from typing import Any, Optional, Tuple


class FileIO:
    """文件读写工具类，提供安全的文件操作方法"""

    # 支持的文件格式及其扩展名映射
    FORMAT_EXTENSIONS: dict = {
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".csv": "csv",
    }

    # 支持的编码列表（按优先级排序）
    ENCODINGS: list = ["utf-8", "utf-8-sig", "gbk", "gb2312", "latin-1"]

    @staticmethod
    def detect_format(filepath: str) -> Optional[str]:
        """根据文件扩展名检测文件格式

        Args:
            filepath: 文件路径

        Returns:
            格式名称字符串（如 'json', 'yaml', 'toml', 'csv'），
            如果无法识别则返回 None
        """
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        return FileIO.FORMAT_EXTENSIONS.get(ext)

    @staticmethod
    def _detect_encoding(filepath: str) -> str:
        """尝试检测文件编码

        通过依次尝试不同编码来读取文件，找到第一个能成功解码的编码。

        Args:
            filepath: 文件路径

        Returns:
            检测到的编码名称

        Raises:
            FileNotFoundError: 文件不存在
            UnicodeDecodeError: 所有编码都无法解码文件
        """
        for encoding in FileIO.ENCODINGS:
            try:
                with open(filepath, "r", encoding=encoding) as f:
                    f.read(4096)  # 读取前4KB来检测编码
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        # 如果所有编码都失败，回退到utf-8（可能会抛出异常）
        return "utf-8"

    @staticmethod
    def read(filepath: str, encoding: Optional[str] = None) -> str:
        """读取文本文件内容

        Args:
            filepath: 文件路径
            encoding: 指定编码，如果为None则自动检测

        Returns:
            文件文本内容

        Raises:
            FileNotFoundError: 文件不存在
            UnicodeDecodeError: 无法解码文件
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        if encoding is None:
            encoding = FileIO._detect_encoding(filepath)

        with open(filepath, "r", encoding=encoding) as f:
            return f.read()

    @staticmethod
    def read_bytes(filepath: str) -> bytes:
        """以二进制模式读取文件

        Args:
            filepath: 文件路径

        Returns:
            文件的二进制内容

        Raises:
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        with open(filepath, "rb") as f:
            return f.read()

    @staticmethod
    def write(filepath: str, content: str, encoding: str = "utf-8",
               ensure_dir: bool = False) -> None:
        """写入文本文件

        Args:
            filepath: 文件路径
            content: 要写入的内容
            encoding: 文件编码，默认为utf-8
            ensure_dir: 是否自动创建父目录

        Raises:
            OSError: 写入文件失败
        """
        if ensure_dir:
            parent_dir = os.path.dirname(filepath)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

        with open(filepath, "w", encoding=encoding) as f:
            f.write(content)

    @staticmethod
    def write_bytes(filepath: str, content: bytes, ensure_dir: bool = False) -> None:
        """以二进制模式写入文件

        Args:
            filepath: 文件路径
            content: 要写入的二进制内容
            ensure_dir: 是否自动创建父目录
        """
        if ensure_dir:
            parent_dir = os.path.dirname(filepath)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(content)

    @staticmethod
    def read_json(filepath: str, encoding: Optional[str] = None) -> Any:
        """读取JSON文件并解析为Python对象

        Args:
            filepath: 文件路径
            encoding: 文件编码

        Returns:
            解析后的Python对象（dict/list等）
        """
        content = FileIO.read(filepath, encoding)
        return json.loads(content)

    @staticmethod
    def write_json(filepath: str, data: Any, indent: int = 2,
                   ensure_ascii: bool = False, sort_keys: bool = False,
                   ensure_dir: bool = False) -> None:
        """将Python对象写入JSON文件

        Args:
            filepath: 文件路径
            data: 要序列化的Python对象
            indent: 缩进空格数
            ensure_ascii: 是否转义非ASCII字符
            sort_keys: 是否按键名排序
            ensure_dir: 是否自动创建父目录
        """
        content = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii,
                             sort_keys=sort_keys, default=str)
        FileIO.write(filepath, content, ensure_dir=ensure_dir)

    @staticmethod
    def exists(filepath: str) -> bool:
        """检查文件是否存在

        Args:
            filepath: 文件路径

        Returns:
            文件是否存在
        """
        return os.path.exists(filepath)

    @staticmethod
    def get_size(filepath: str) -> int:
        """获取文件大小（字节数）

        Args:
            filepath: 文件路径

        Returns:
            文件大小（字节）
        """
        return os.path.getsize(filepath)

    @staticmethod
    def get_extension(filepath: str) -> str:
        """获取文件扩展名（小写，包含点号）

        Args:
            filepath: 文件路径

        Returns:
            文件扩展名，如 '.json'
        """
        _, ext = os.path.splitext(filepath)
        return ext.lower()

    @staticmethod
    def resolve_path(filepath: str) -> str:
        """解析文件路径为绝对路径

        Args:
            filepath: 文件路径（可以是相对路径）

        Returns:
            解析后的绝对路径
        """
        return os.path.abspath(filepath)

    @staticmethod
    def is_stdin() -> bool:
        """检查是否有来自标准输入的数据（管道输入）

        Returns:
            如果标准输入有数据且不是终端，返回True
        """
        return not sys.stdin.isatty()

    @staticmethod
    def read_stdin() -> str:
        """从标准输入读取所有数据

        Returns:
            标准输入的文本内容
        """
        return sys.stdin.read()
