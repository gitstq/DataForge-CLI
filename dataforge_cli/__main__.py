"""
DataForge-CLI 入口点
====================
允许通过 python -m dataforge_cli 运行。
"""

from dataforge_cli.cli import main

if __name__ == "__main__":
    import sys
    sys.exit(main())
