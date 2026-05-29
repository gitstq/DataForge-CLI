"""
DataForge-CLI - 轻量级终端JSON/YAML数据智能处理与转换引擎

一个纯Python零依赖的CLI工具，提供数据解析、查询、转换、合并、
差异对比、模板渲染、验证和格式化等功能。

使用示例:
    # 查询JSON数据
    python -m dataforge_cli query data.json "users[0].name"

    # 格式转换
    python -m dataforge_cli convert data.json --to yaml

    # 合并文件
    python -m dataforge_cli merge a.json b.json --output merged.json

    # 差异对比
    python -m dataforge_cli diff old.json new.json

    # 模板渲染
    python -m dataforge_cli template report.tpl --data data.json

    # 数据验证
    python -m dataforge_cli validate data.json --schema schema.json

    # 启动TUI仪表盘
    python -m dataforge_cli tui
"""

__version__ = "1.0.0"
__author__ = "DataForge Team"
__description__ = "轻量级终端JSON/YAML数据智能处理与转换引擎"
