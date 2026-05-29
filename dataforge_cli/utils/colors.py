"""
终端颜色工具模块
================
提供ANSI终端颜色控制码，用于在终端中输出彩色文本。
支持16色和8-bit 256色方案。
不依赖任何第三方库。

使用示例:
    from dataforge_cli.utils.colors import Colors

    print(Colors.red("错误信息"))
    print(Colors.green("成功信息"))
    print(Colors.bold(Colors.blue("加粗蓝色")))
"""


class Colors:
    """终端ANSI颜色控制工具类"""

    # ANSI控制码前缀和后缀
    _PREFIX = "\033["
    _SUFFIX = "m"
    _RESET = "\033[0m"

    # 前景色代码
    _FG_COLORS = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        "bright_black": 90,
        "bright_red": 91,
        "bright_green": 92,
        "bright_yellow": 93,
        "bright_blue": 94,
        "bright_magenta": 95,
        "bright_cyan": 96,
        "bright_white": 97,
    }

    # 背景色代码
    _BG_COLORS = {
        "bg_black": 40,
        "bg_red": 41,
        "bg_green": 42,
        "bg_yellow": 43,
        "bg_blue": 44,
        "bg_magenta": 45,
        "bg_cyan": 46,
        "bg_white": 47,
        "bg_bright_black": 100,
        "bg_bright_red": 101,
        "bg_bright_green": 102,
        "bg_bright_yellow": 103,
        "bg_bright_blue": 104,
        "bg_bright_magenta": 105,
        "bg_bright_cyan": 106,
        "bg_bright_white": 107,
    }

    # 样式代码
    _STYLES = {
        "bold": 1,
        "dim": 2,
        "italic": 3,
        "underline": 4,
        "blink": 5,
        "reverse": 7,
        "hidden": 8,
        "strikethrough": 9,
    }

    @classmethod
    def _build_code(cls, *codes: int) -> str:
        """构建ANSI控制码序列

        Args:
            codes: ANSI控制码数字序列

        Returns:
            完整的ANSI转义序列字符串
        """
        return f"{cls._PREFIX}{';'.join(str(c) for c in codes)}{cls._SUFFIX}"

    @classmethod
    def colorize(cls, text: str, *codes: int) -> str:
        """用ANSI控制码包裹文本

        Args:
            text: 要着色的文本
            codes: ANSI控制码数字序列

        Returns:
            带有ANSI颜色代码的文本
        """
        if not text:
            return text
        return f"{cls._build_code(*codes)}{text}{cls._RESET}"

    @classmethod
    def reset(cls) -> str:
        """返回重置所有样式的控制码"""
        return cls._RESET

    @classmethod
    def disable(cls) -> None:
        """禁用颜色输出（将所有颜色方法设为空操作）"""
        for name in list(cls._FG_COLORS.keys()) + list(cls._BG_COLORS.keys()) + list(cls._STYLES.keys()):
            setattr(cls, name, staticmethod(lambda text="": text))
        cls.colorize = staticmethod(lambda text="", *codes: text)
        cls.reset = staticmethod(lambda: "")

    @classmethod
    def enable(cls) -> None:
        """启用颜色输出（重新绑定所有颜色方法）"""
        # 重新绑定前景色方法
        for name, code in cls._FG_COLORS.items():
            setattr(cls, name, staticmethod(lambda text="", c=code: cls.colorize(text, c)))
        # 重新绑定背景色方法
        for name, code in cls._BG_COLORS.items():
            setattr(cls, name, staticmethod(lambda text="", c=code: cls.colorize(text, c)))
        # 重新绑定样式方法
        for name, code in cls._STYLES.items():
            setattr(cls, name, staticmethod(lambda text="", c=code: cls.colorize(text, c)))

    # 初始化时自动绑定所有颜色和样式方法
    @classmethod
    def _init_methods(cls):
        """初始化所有颜色和样式的快捷方法"""
        for name, code in cls._FG_COLORS.items():
            setattr(cls, name, staticmethod(lambda text="", c=code: cls.colorize(text, c)))
        for name, code in cls._BG_COLORS.items():
            setattr(cls, name, staticmethod(lambda text="", c=code: cls.colorize(text, c)))
        for name, code in cls._STYLES.items():
            setattr(cls, name, staticmethod(lambda text="", c=code: cls.colorize(text, c)))


# 自动初始化颜色方法
Colors._init_methods()


def style(text: str, fg: str = None, bg: str = None, bold: bool = False,
          dim: bool = False, underline: bool = False, italic: bool = False) -> str:
    """组合多种样式的便捷函数

    Args:
        text: 要着色的文本
        fg: 前景色名称（如 'red', 'green', 'blue' 等）
        bg: 背景色名称（如 'bg_red', 'bg_green' 等）
        bold: 是否加粗
        dim: 是否变暗
        underline: 是否下划线
        italic: 是否斜体

    Returns:
        带有组合样式的文本

    使用示例:
        style("警告信息", fg="yellow", bold=True)
        style("错误", fg="red", bg="bg_white", bold=True)
    """
    codes = []
    if bold:
        codes.append(Colors._STYLES["bold"])
    if dim:
        codes.append(Colors._STYLES["dim"])
    if underline:
        codes.append(Colors._STYLES["underline"])
    if italic:
        codes.append(Colors._STYLES["italic"])
    if fg and fg in Colors._FG_COLORS:
        codes.append(Colors._FG_COLORS[fg])
    if bg and bg in Colors._BG_COLORS:
        codes.append(Colors._BG_COLORS[bg])
    if not codes:
        return text
    return Colors.colorize(text, *codes)
