"""
TUI交互式仪表盘模块
====================
使用终端控制码实现的简易TUI仪表盘，不依赖rich/textual等第三方库。

功能面板:
    - 文件浏览器面板
    - 数据预览面板
    - 查询输入面板
    - 状态栏

使用示例:
    from dataforge_cli.tui.dashboard import Dashboard

    # 启动仪表盘
    dashboard = Dashboard()
    dashboard.run()
"""

import json
import os
import sys
import termios
import tty
from typing import Any, Dict, List, Optional, Tuple


class Dashboard:
    """TUI交互式仪表盘

    使用终端控制码实现的多面板交互界面。
    支持文件浏览、数据预览和查询功能。
    """

    # ANSI 终端控制码
    ESC = "\033"
    CSI = "\033["
    CLEAR_SCREEN = "\033[2J"
    CLEAR_LINE = "\033[2K"
    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    REVERSE = "\033[7m"

    # 颜色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLACK = "\033[40m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"

    def __init__(self, directory: str = "."):
        """初始化仪表盘

        Args:
            directory: 初始浏览目录
        """
        self.directory = os.path.abspath(directory)
        self.current_file: Optional[str] = None
        self.current_data: Any = None
        self.query_input: str = ""
        self.query_result: Optional[str] = None
        self.file_list: List[str] = []
        self.file_cursor: int = 0
        self.panel_focus: int = 0  # 0=文件, 1=预览, 2=查询
        self.scroll_offset: int = 0
        self.preview_scroll: int = 0
        self.running: bool = True
        self.status_message: str = "就绪 - 按 ? 查看帮助"
        self.terminal_size: Tuple[int, int] = (24, 80)

        self._refresh_file_list()

    def run(self) -> None:
        """运行TUI仪表盘主循环"""
        # 保存终端设置
        try:
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        except (termios.error, tty.error):
            old_settings = None

        try:
            self._update_terminal_size()
            while self.running:
                self._draw()
                key = self._read_key()
                self._handle_key(key)
        finally:
            # 恢复终端设置
            self._show_cursor()
            print(self.CLEAR_SCREEN)
            print(f"\033[H")
            if old_settings:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def _update_terminal_size(self) -> None:
        """更新终端尺寸"""
        try:
            import fcntl
            import struct
            result = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, b'\x00' * 8)
            rows, cols = struct.unpack('HH', result)
            self.terminal_size = (rows, cols)
        except (ImportError, OSError, IOError):
            self.terminal_size = (24, 80)

    def _refresh_file_list(self) -> None:
        """刷新文件列表"""
        self.file_list = []
        try:
            entries = sorted(os.listdir(self.directory))
            # 先添加目录
            dirs = []
            files = []
            for entry in entries:
                full_path = os.path.join(self.directory, entry)
                if entry.startswith("."):
                    continue
                if os.path.isdir(full_path):
                    dirs.append(f"[DIR]  {entry}/")
                else:
                    ext = os.path.splitext(entry)[1].lower()
                    if ext in (".json", ".yaml", ".yml", ".toml", ".csv"):
                        files.append(f"[{ext[1:].upper():>4}] {entry}")
            self.file_list = dirs + files
        except PermissionError:
            self.status_message = f"无权限访问目录: {self.directory}"

        if self.file_cursor >= len(self.file_list):
            self.file_cursor = max(0, len(self.file_list) - 1)

    def _draw(self) -> None:
        """绘制整个界面"""
        rows, cols = self.terminal_size
        output: List[str] = []

        # 清屏并隐藏光标
        output.append(self.CLEAR_SCREEN)
        output.append(self.HIDE_CURSOR)

        # 标题栏
        title = f" DataForge-CLI TUI Dashboard v1.0.0 "
        title_len = len(title)
        padding = max(0, cols - title_len - 4)
        output.append(f"\033[H{self.BG_BLUE}{self.WHITE}{self.BOLD}{title}{' ' * padding}{self.RESET}")

        # 计算面板尺寸
        left_width = max(20, cols // 3)
        right_width = cols - left_width - 3
        content_height = rows - 4  # 减去标题栏和状态栏

        # 左侧面板 - 文件浏览器
        self._draw_file_panel(output, 0, 2, left_width, content_height)

        # 右侧面板 - 数据预览或查询结果
        self._draw_preview_panel(output, left_width + 3, 2, right_width, content_height)

        # 状态栏
        self._draw_status_bar(output, 0, rows - 1, cols)

        # 渲染输出
        sys.stdout.write("\n".join(output))
        sys.stdout.flush()

    def _draw_file_panel(self, output: List[str], x: int, y: int,
                         width: int, height: int) -> None:
        """绘制文件浏览器面板

        Args:
            output: 输出行列表
            x: 面板起始列
            y: 面板起始行
            width: 面板宽度
            height: 面板高度
        """
        # 面板标题
        title = " 文件浏览器 "
        if self.panel_focus == 0:
            title_style = f"{self.BG_CYAN}{self.BLACK}{self.BOLD}"
        else:
            title_style = f"{self.BOLD}{self.CYAN}"

        output.append(f"\033[{y};{x}H{title_style}{title}{self.RESET}")

        # 面板边框
        border = "+" + "-" * (width - 2) + "+"
        output.append(f"\033[{y + 1};{x}H{self.DIM}{border}{self.RESET}")

        # 当前目录
        dir_display = self.directory[-(width - 4):]
        output.append(f"\033[{y + 2};{x + 1}H{self.YELLOW}{self.BOLD}{dir_display}{self.RESET}")

        # 文件列表
        visible_height = height - 5  # 标题+边框+目录+底部边框+状态
        start = self.scroll_offset
        end = min(start + visible_height, len(self.file_list))

        for i in range(start, end):
            row = y + 3 + (i - start)
            if row >= y + height - 1:
                break

            line = self.file_list[i]
            if len(line) > width - 4:
                line = line[:width - 7] + "..."

            if i == self.file_cursor and self.panel_focus == 0:
                output.append(f"\033[{row};{x + 1}H{self.REVERSE}{line}{self.RESET}")
            else:
                # 根据类型着色
                if "[DIR]" in line:
                    color = self.BLUE
                elif "[JSON" in line:
                    color = self.GREEN
                elif "[YAML" in line or "[YML" in line:
                    color = self.MAGENTA
                elif "[TOML" in line:
                    color = self.YELLOW
                elif "[CSV" in line:
                    color = self.CYAN
                else:
                    color = self.WHITE
                output.append(f"\033[{row};{x + 1}H{color}{line}{self.RESET}")

        # 底部边框
        bottom_row = y + height - 1
        output.append(f"\033[{bottom_row};{x}H{self.DIM}{border}{self.RESET}")

        # 文件数量
        count_text = f" {len(self.file_list)} 个文件 "
        output.append(f"\033[{bottom_row};{x + 2}H{self.DIM}{count_text}{self.RESET}")

    def _draw_preview_panel(self, output: List[str], x: int, y: int,
                            width: int, height: int) -> None:
        """绘制数据预览面板

        Args:
            output: 输出行列表
            x: 面板起始列
            y: 面板起始行
            width: 面板宽度
            height: 面板高度
        """
        # 面板标题
        if self.panel_focus == 2 and self.query_result:
            title = " 查询结果 "
        else:
            title = " 数据预览 "

        if self.panel_focus in (1, 2):
            title_style = f"{self.BG_CYAN}{self.BLACK}{self.BOLD}"
        else:
            title_style = f"{self.BOLD}{self.CYAN}"

        output.append(f"\033[{y};{x}H{title_style}{title}{self.RESET}")

        # 面板边框
        border = "+" + "-" * (width - 2) + "+"
        output.append(f"\033[{y + 1};{x}H{self.DIM}{border}{self.RESET}")

        # 内容
        if self.panel_focus == 2 and self.query_result:
            content = self.query_result
        elif self.current_data is not None:
            try:
                content = json.dumps(self.current_data, indent=2, ensure_ascii=False, default=str)
            except (TypeError, ValueError):
                content = str(self.current_data)
        else:
            content = "请选择文件查看数据\n\n支持格式: JSON, YAML, TOML, CSV"

        # 按行显示
        lines = content.split("\n")
        visible_height = height - 4
        start = self.preview_scroll
        end = min(start + visible_height, len(lines))

        for i in range(start, end):
            row = y + 2 + (i - start)
            if row >= y + height - 1:
                break

            line = lines[i]
            if len(line) > width - 4:
                line = line[:width - 7] + "..."

            output.append(f"\033[{row};{x + 1}H{self.WHITE}{line}{self.RESET}")

        # 底部边框
        bottom_row = y + height - 1
        output.append(f"\033[{bottom_row};{x}H{self.DIM}{border}{self.RESET}")

        # 查询输入行
        if self.panel_focus == 2:
            query_display = f"> {self.query_input}_"
            if len(query_display) > width - 4:
                query_display = query_display[:width - 7] + "_"
            output.append(f"\033[{bottom_row};{x + 2}H{self.GREEN}{self.BOLD}{query_display}{self.RESET}")
        elif self.current_file:
            file_name = os.path.basename(self.current_file)
            output.append(f"\033[{bottom_row};{x + 2}H{self.DIM}{file_name}{self.RESET}")

    def _draw_status_bar(self, output: List[str], x: int, y: int,
                         width: int) -> None:
        """绘制状态栏

        Args:
            output: 输出行列表
            x: 起始列
            y: 起始行
            width: 宽度
        """
        status = self.status_message
        if len(status) > width - 4:
            status = status[:width - 7] + "..."

        # 快捷键提示
        hints = " Tab:切换面板  ?:帮助  q:退出 "
        output.append(f"\033[{y};{x}H{self.BG_BLACK}{self.WHITE}{status}{' ' * (width - len(status) - len(hints) - 2)}{hints}{self.RESET}")

    def _read_key(self) -> str:
        """读取单个按键

        Returns:
            按键字符串
        """
        try:
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                # 转义序列
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    ch3 = sys.stdin.read(1)
                    return f"\x1b[{ch3}"
                return "\x1b"
            return ch
        except (IOError, EOFError):
            return "q"

    def _handle_key(self, key: str) -> None:
        """处理按键事件

        Args:
            key: 按键字符串
        """
        # 全局快捷键
        if key == "q":
            self.running = False
            return

        if key == "?":
            self._show_help()
            return

        if key == "\t":
            self.panel_focus = (self.panel_focus + 1) % 3
            self.status_message = f"当前面板: {['文件浏览器', '数据预览', '查询输入'][self.panel_focus]}"
            return

        # 根据焦点面板处理按键
        if self.panel_focus == 0:
            self._handle_file_panel_key(key)
        elif self.panel_focus == 1:
            self._handle_preview_panel_key(key)
        elif self.panel_focus == 2:
            self._handle_query_panel_key(key)

    def _handle_file_panel_key(self, key: str) -> None:
        """处理文件面板按键

        Args:
            key: 按键字符串
        """
        if key == "\x1b[A":  # 上箭头
            if self.file_cursor > 0:
                self.file_cursor -= 1
                if self.file_cursor < self.scroll_offset:
                    self.scroll_offset = self.file_cursor
        elif key == "\x1b[B":  # 下箭头
            if self.file_cursor < len(self.file_list) - 1:
                self.file_cursor += 1
                visible_height = self.terminal_size[0] - 9
                if self.file_cursor >= self.scroll_offset + visible_height:
                    self.scroll_offset = self.file_cursor - visible_height + 1
        elif key == "\n" or key == "\r":  # 回车
            self._open_selected_file()
        elif key == "h" or key == "\x1b[D":  # 左箭头或h
            parent = os.path.dirname(self.directory)
            if parent != self.directory:
                self.directory = parent
                self.file_cursor = 0
                self.scroll_offset = 0
                self._refresh_file_list()
                self.status_message = f"目录: {self.directory}"

    def _handle_preview_panel_key(self, key: str) -> None:
        """处理预览面板按键

        Args:
            key: 按键字符串
        """
        if key == "\x1b[A":  # 上箭头
            if self.preview_scroll > 0:
                self.preview_scroll -= 1
        elif key == "\x1b[B":  # 下箭头
            self.preview_scroll += 1
        elif key == " ":  # 空格翻页
            self.preview_scroll += self.terminal_size[0] // 2
        elif key == "Home" or key == "g":
            self.preview_scroll = 0
        elif key == "End" or key == "G":
            self.preview_scroll = 9999

    def _handle_query_panel_key(self, key: str) -> None:
        """处理查询面板按键

        Args:
            key: 按键字符串
        """
        if key == "\n" or key == "\r":  # 回车执行查询
            self._execute_query()
        elif key == "\x7f" or key == "\x08":  # 退格
            if self.query_input:
                self.query_input = self.query_input[:-1]
        elif key == "\x1b[C":  # 右箭头（忽略）
            pass
        elif key == "\x1b[A" or key == "\x1b[B":  # 上下箭头（忽略）
            pass
        elif len(key) == 1 and ord(key) >= 32:  # 可打印字符
            self.query_input += key

    def _open_selected_file(self) -> None:
        """打开选中的文件"""
        if not self.file_list:
            return

        entry = self.file_list[self.file_cursor]

        # 检查是否为目录
        if "[DIR]" in entry:
            dir_name = entry.replace("[DIR]  ", "").rstrip("/")
            self.directory = os.path.join(self.directory, dir_name)
            self.file_cursor = 0
            self.scroll_offset = 0
            self._refresh_file_list()
            self.status_message = f"目录: {self.directory}"
            return

        # 提取文件名
        parts = entry.split(" ", 1)
        if len(parts) < 2:
            return
        filename = parts[1].strip()

        filepath = os.path.join(self.directory, filename)
        try:
            from dataforge_cli.core.parser import Parser

            self.current_file = filepath
            self.current_data = Parser.parse_file(filepath)
            self.preview_scroll = 0
            self.panel_focus = 1
            self.status_message = f"已加载: {filename}"

            # 数据统计
            from dataforge_cli.core.transform import TransformEngine
            stats = TransformEngine.stats(self.current_data)
            type_info = stats.get("type", "unknown")
            if isinstance(self.current_data, dict):
                self.status_message += f" ({type_info}, {stats.get('key_count', 0)} 个键)"
            elif isinstance(self.current_data, list):
                self.status_message += f" ({type_info}, {stats.get('length', 0)} 项)"
            else:
                self.status_message += f" ({type_info})"

        except Exception as e:
            self.status_message = f"加载失败: {e}"
            self.current_data = None

    def _execute_query(self) -> None:
        """执行查询表达式"""
        if not self.query_input.strip():
            return

        if self.current_data is None:
            self.status_message = "请先选择一个数据文件"
            return

        try:
            from dataforge_cli.core.query import QueryEngine

            engine = QueryEngine(self.current_data)
            result = engine.query(self.query_input)

            try:
                self.query_result = json.dumps(result, indent=2, ensure_ascii=False, default=str)
            except (TypeError, ValueError):
                self.query_result = str(result)

            self.preview_scroll = 0
            self.status_message = f"查询: {self.query_input} -> 成功"

        except Exception as e:
            self.query_result = f"查询错误: {e}"
            self.status_message = f"查询失败: {e}"

    def _show_help(self) -> None:
        """显示帮助信息"""
        self._show_cursor()
        print(self.CLEAR_SCREEN)
        print(f"\033[H")

        help_text = """
DataForge-CLI TUI 仪表盘 - 帮助
================================

快捷键:
  Tab       - 切换焦点面板（文件浏览器/数据预览/查询输入）
  q         - 退出仪表盘
  ?         - 显示此帮助

文件浏览器面板:
  上/下箭头  - 浏览文件列表
  Enter     - 打开文件/进入目录
  h/左箭头   - 返回上级目录

数据预览面板:
  上/下箭头  - 滚动查看
  空格       - 翻页
  g/Home     - 跳到顶部
  G/End     - 跳到底部

查询输入面板:
  输入查询表达式后按 Enter 执行
  支持类JMESPath语法:
    - users[0].name      点号访问
    - users[*].age       通配符
    - users[?age > 18]   过滤器
    - length(users)      聚合函数
    - sort_by(users,age) 排序

按任意键返回...
"""
        print(help_text)
        sys.stdout.flush()

        try:
            sys.stdin.read(1)
        except (IOError, EOFError):
            pass

        self.HIDE_CURSOR

    def _show_cursor(self) -> None:
        """显示光标"""
        sys.stdout.write(self.SHOW_CURSOR)
        sys.stdout.flush()

    def _hide_cursor(self) -> None:
        """隐藏光标"""
        sys.stdout.write(self.HIDE_CURSOR)
        sys.stdout.flush()
