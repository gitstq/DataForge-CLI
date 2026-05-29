"""
DataForge-CLI 命令行入口
========================
提供所有CLI命令的解析和分发。

命令列表:
    dataforge query <file> <expression> [--output FORMAT]
    dataforge convert <file> --to FORMAT [--output FILE]
    dataforge merge <file1> <file2> [--strategy STRATEGY] [--output FILE]
    dataforge diff <file1> <file2> [--ignore PATH] [--format FORMAT]
    dataforge validate <file> [--schema FILE]
    dataforge template <template> --data <file> [--output FILE]
    dataforge format <file> [--indent N] [--sort-keys] [--output FILE]
    dataforge flatten <file> [--separator SEP] [--output FILE]
    dataforge unflatten <file> [--separator SEP] [--output FILE]
    dataforge stats <file>
    dataforge server [--port PORT]
    dataforge tui

使用示例:
    # 查询数据
    python -m dataforge_cli query data.json "users[0].name"

    # 格式转换
    python -m dataforge_cli convert data.json --to yaml --output data.yaml

    # 合并文件
    python -m dataforge_cli merge a.json b.json --strategy append --output merged.json

    # 差异对比
    python -m dataforge_cli diff old.json new.json --format colorized

    # 启动TUI
    python -m dataforge_cli tui
"""

import argparse
import json
import os
import sys
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> int:
    """CLI主入口函数

    Args:
        argv: 命令行参数列表（为None时使用sys.argv）

    Returns:
        退出码（0=成功，非0=失败）
    """
    parser = _create_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func") or args.func is None:
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n操作已取消")
        return 130
    except Exception as e:
        from dataforge_cli.utils.colors import Colors
        print(f"{Colors.red('错误')}: {e}", file=sys.stderr)
        return 1


def _create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器

    Returns:
        配置好的ArgumentParser实例
    """
    parser = argparse.ArgumentParser(
        prog="dataforge",
        description="DataForge-CLI - 轻量级终端JSON/YAML数据智能处理与转换引擎",
        epilog="使用 'dataforge <command> --help' 查看各命令的详细帮助",
    )
    parser.add_argument("-v", "--version", action="version",
                        version=f"dataforge-cli v1.0.0")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ==================== query 命令 ====================
    query_parser = subparsers.add_parser("query", help="查询数据")
    query_parser.add_argument("file", help="数据文件路径")
    query_parser.add_argument("expression", help="查询表达式（类JMESPath语法）")
    query_parser.add_argument("-o", "--output", help="输出格式（json/yaml/table）", default="json")
    query_parser.add_argument("--color", help="启用彩色输出", action="store_true")
    query_parser.set_defaults(func=cmd_query)

    # ==================== convert 命令 ====================
    convert_parser = subparsers.add_parser("convert", help="格式转换")
    convert_parser.add_argument("file", help="输入文件路径")
    convert_parser.add_argument("-t", "--to", required=True, dest="to_format",
                                help="目标格式（json/yaml/toml/csv/table）")
    convert_parser.add_argument("-o", "--output", help="输出文件路径（不指定则输出到stdout）")
    convert_parser.add_argument("--indent", type=int, default=2, help="缩进空格数")
    convert_parser.set_defaults(func=cmd_convert)

    # ==================== merge 命令 ====================
    merge_parser = subparsers.add_parser("merge", help="合并文件")
    merge_parser.add_argument("files", nargs="+", help="要合并的文件路径（至少2个）")
    merge_parser.add_argument("-s", "--strategy", default="replace",
                               help="数组合并策略（append/replace/merge-by-key/prepend）")
    merge_parser.add_argument("-c", "--conflict", default="theirs",
                               help="冲突解决策略（ours/theirs/manual/error）")
    merge_parser.add_argument("-o", "--output", help="输出文件路径")
    merge_parser.add_argument("--dry-run", help="预览合并结果", action="store_true")
    merge_parser.set_defaults(func=cmd_merge)

    # ==================== diff 命令 ====================
    diff_parser = subparsers.add_parser("diff", help="差异对比")
    diff_parser.add_argument("file1", help="旧文件路径")
    diff_parser.add_argument("file2", help="新文件路径")
    diff_parser.add_argument("-i", "--ignore", nargs="*", default=[], help="忽略的路径模式")
    diff_parser.add_argument("-f", "--format", default="colorized",
                             help="输出格式（text/colorized/patch/summary）")
    diff_parser.add_argument("-o", "--output", help="输出文件路径")
    diff_parser.set_defaults(func=cmd_diff)

    # ==================== validate 命令 ====================
    validate_parser = subparsers.add_parser("validate", help="数据验证")
    validate_parser.add_argument("file", help="数据文件路径")
    validate_parser.add_argument("-s", "--schema", help="Schema文件路径")
    validate_parser.add_argument("--report", help="生成验证报告到文件")
    validate_parser.set_defaults(func=cmd_validate)

    # ==================== template 命令 ====================
    template_parser = subparsers.add_parser("template", help="模板渲染")
    template_parser.add_argument("template", help="模板文件路径或模板字符串")
    template_parser.add_argument("-d", "--data", required=True, help="数据文件路径")
    template_parser.add_argument("-o", "--output", help="输出文件路径")
    template_parser.add_argument("-v", "--var", nargs="*", default=[],
                                help="额外变量（格式: key=value）")
    template_parser.set_defaults(func=cmd_template)

    # ==================== format 命令 ====================
    format_parser = subparsers.add_parser("format", help="格式化数据")
    format_parser.add_argument("file", help="数据文件路径")
    format_parser.add_argument("--indent", type=int, default=2, help="缩进空格数")
    format_parser.add_argument("--sort-keys", help="按键名排序", action="store_true")
    format_parser.add_argument("--minify", help="压缩输出", action="store_true")
    format_parser.add_argument("-o", "--output", help="输出文件路径")
    format_parser.add_argument("--output-format", help="输出格式（json/yaml/table/tree）",
                               default="json")
    format_parser.set_defaults(func=cmd_format)

    # ==================== flatten 命令 ====================
    flatten_parser = subparsers.add_parser("flatten", help="展平嵌套数据")
    flatten_parser.add_argument("file", help="数据文件路径")
    flatten_parser.add_argument("-s", "--separator", default=".", help="路径分隔符")
    flatten_parser.add_argument("-o", "--output", help="输出文件路径")
    flatten_parser.set_defaults(func=cmd_flatten)

    # ==================== unflatten 命令 ====================
    unflatten_parser = subparsers.add_parser("unflatten", help="还原嵌套数据")
    unflatten_parser.add_argument("file", help="数据文件路径")
    unflatten_parser.add_argument("-s", "--separator", default=".", help="路径分隔符")
    unflatten_parser.add_argument("-o", "--output", help="输出文件路径")
    unflatten_parser.set_defaults(func=cmd_unflatten)

    # ==================== stats 命令 ====================
    stats_parser = subparsers.add_parser("stats", help="数据统计")
    stats_parser.add_argument("file", help="数据文件路径")
    stats_parser.set_defaults(func=cmd_stats)

    # ==================== server 命令 ====================
    server_parser = subparsers.add_parser("server", help="启动HTTP API服务")
    server_parser.add_argument("-p", "--port", type=int, default=8080, help="端口号")
    server_parser.add_argument("--host", default="127.0.0.1", help="绑定地址")
    server_parser.set_defaults(func=cmd_server)

    # ==================== tui 命令 ====================
    tui_parser = subparsers.add_parser("tui", help="启动TUI交互式仪表盘")
    tui_parser.add_argument("-d", "--directory", default=".", help="初始浏览目录")
    tui_parser.set_defaults(func=cmd_tui)

    return parser


# ==================== 命令处理函数 ====================

def cmd_query(args: argparse.Namespace) -> int:
    """执行查询命令

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from dataforge_cli.core.parser import Parser
    from dataforge_cli.core.query import QueryEngine
    from dataforge_cli.core.formatter import Formatter

    data = Parser.parse_file(args.file)
    engine = QueryEngine(data)
    result = engine.query(args.expression)

    if args.output == "table":
        if isinstance(result, list):
            print(Formatter.format_table(result, title=f"查询: {args.expression}"))
        else:
            print(result)
    elif args.output == "yaml":
        print(Parser.serialize_yaml(result))
    elif args.output == "tree":
        print(Formatter.format_tree(result))
    else:
        if args.color:
            print(Formatter.format_json(result, color=True))
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    return 0


def cmd_convert(args: argparse.Namespace) -> int:
    """执行格式转换命令

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from dataforge_cli.core.parser import Parser
    from dataforge_cli.core.transform import TransformEngine
    from dataforge_cli.utils.file_io import FileIO

    data = Parser.parse_file(args.file)
    result = TransformEngine.convert(data, "auto", args.to_format, indent=args.indent)

    if isinstance(result, str):
        if args.output:
            FileIO.write(args.output, result, ensure_dir=True)
            print(f"已转换并保存到: {args.output}")
        else:
            print(result, end="")
    else:
        output = json.dumps(result, indent=2, ensure_ascii=False, default=str)
        if args.output:
            FileIO.write(args.output, output, ensure_dir=True)
            print(f"已转换并保存到: {args.output}")
        else:
            print(output)

    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    """执行合并命令

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from dataforge_cli.core.merge import MergeEngine
    from dataforge_cli.utils.file_io import FileIO

    if len(args.files) < 2:
        print("错误: 合并至少需要2个文件", file=sys.stderr)
        return 1

    if args.dry_run:
        from dataforge_cli.core.parser import Parser
        data1 = Parser.parse_file(args.files[0])
        data2 = Parser.parse_file(args.files[1])
        preview = MergeEngine.preview_merge(data1, data2, args.strategy, args.conflict)

        print("合并预览:")
        print(f"  新增: {preview['changes']['added']} 项")
        print(f"  修改: {preview['changes']['modified']} 项")
        print(f"  未变: {preview['changes']['unchanged']} 项")

        if preview["conflicts"]:
            print(f"\n冲突 ({len(preview['conflicts'])} 个):")
            for conflict in preview["conflicts"]:
                print(f"  路径: {conflict['path']}")
                print(f"    旧值: {conflict['base']}")
                print(f"    新值: {conflict['override']}")
        else:
            print("\n无冲突")
    else:
        result = MergeEngine.merge_files(args.files, args.strategy, args.conflict)
        output = json.dumps(result, indent=2, ensure_ascii=False, default=str)

        if args.output:
            FileIO.write(args.output, output, ensure_dir=True)
            print(f"已合并并保存到: {args.output}")
        else:
            print(output)

    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    """执行差异对比命令

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from dataforge_cli.core.parser import Parser
    from dataforge_cli.core.diff import DiffEngine
    from dataforge_cli.utils.file_io import FileIO

    data1 = Parser.parse_file(args.file1)
    data2 = Parser.parse_file(args.file2)

    result = DiffEngine.diff(data1, data2, ignore_paths=args.ignore)

    if args.format == "colorized":
        output = DiffEngine.diff_colorized(result)
    elif args.format == "patch":
        patches = DiffEngine.json_patch(data1, data2)
        output = json.dumps(patches, indent=2, ensure_ascii=False)
    elif args.format == "summary":
        output = DiffEngine.diff_summary(result)
    else:
        output = DiffEngine.diff_detail(result)

    if args.output:
        FileIO.write(args.output, output, ensure_dir=True)
        print(f"差异报告已保存到: {args.output}")
    else:
        print(output)

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """执行验证命令

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from dataforge_cli.core.parser import Parser
    from dataforge_cli.core.validator import Validator
    from dataforge_cli.utils.file_io import FileIO

    data = Parser.parse_file(args.file)

    if args.schema:
        schema = Parser.parse_file(args.schema)
    else:
        # 如果没有指定schema，使用基本验证
        schema = {"type": ["object", "array", "string", "number", "boolean", "null"]}

    validator = Validator(schema)
    result = validator.validate(data)

    if args.report:
        report = validator.generate_report(data)
        FileIO.write(args.report, report, ensure_dir=True)
        print(f"验证报告已保存到: {args.report}")
    else:
        report = validator.generate_report(data)
        print(report)

    return 0 if result["valid"] else 1


def cmd_template(args: argparse.Namespace) -> int:
    """执行模板渲染命令

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from dataforge_cli.core.parser import Parser
    from dataforge_cli.core.template import TemplateEngine
    from dataforge_cli.utils.file_io import FileIO

    # 加载数据
    data = Parser.parse_file(args.data)
    if not isinstance(data, dict):
        data = {"data": data}

    # 解析额外变量
    extra_vars: dict = {}
    for var in args.var:
        if "=" in var:
            key, _, value = var.partition("=")
            extra_vars[key] = value

    # 判断模板是文件还是字符串
    if os.path.exists(args.template):
        engine = TemplateEngine("")
        result = engine.render_file(args.template, data, **extra_vars)
    else:
        engine = TemplateEngine(args.template)
        result = engine.render(data, **extra_vars)

    if args.output:
        FileIO.write(args.output, result, ensure_dir=True)
        print(f"渲染结果已保存到: {args.output}")
    else:
        print(result, end="")

    return 0


def cmd_format(args: argparse.Namespace) -> int:
    """执行格式化命令

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from dataforge_cli.core.parser import Parser
    from dataforge_cli.core.transform import TransformEngine
    from dataforge_cli.core.formatter import Formatter
    from dataforge_cli.utils.file_io import FileIO

    data = Parser.parse_file(args.file)

    if args.minify:
        output = TransformEngine.minify(json.dumps(data, ensure_ascii=False))
    elif args.output_format == "yaml":
        output = Parser.serialize_yaml(data, indent=args.indent)
    elif args.output_format == "table":
        if isinstance(data, list):
            output = Formatter.format_table(data)
        else:
            output = Formatter.format_table([data])
    elif args.output_format == "tree":
        output = Formatter.format_tree(data)
    else:
        output = json.dumps(data, indent=args.indent, ensure_ascii=False, sort_keys=args.sort_keys)

    if args.output:
        FileIO.write(args.output, output, ensure_dir=True)
        print(f"已格式化并保存到: {args.output}")
    else:
        print(output)

    return 0


def cmd_flatten(args: argparse.Namespace) -> int:
    """执行展平命令

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from dataforge_cli.core.parser import Parser
    from dataforge_cli.core.transform import TransformEngine
    from dataforge_cli.utils.file_io import FileIO

    data = Parser.parse_file(args.file)
    result = TransformEngine.flatten(data, separator=args.separator)
    output = json.dumps(result, indent=2, ensure_ascii=False, default=str)

    if args.output:
        FileIO.write(args.output, output, ensure_dir=True)
        print(f"已展平并保存到: {args.output}")
    else:
        print(output)

    return 0


def cmd_unflatten(args: argparse.Namespace) -> int:
    """执行还原命令

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from dataforge_cli.core.parser import Parser
    from dataforge_cli.core.transform import TransformEngine
    from dataforge_cli.utils.file_io import FileIO

    data = Parser.parse_file(args.file)
    result = TransformEngine.unflatten(data, separator=args.separator)
    output = json.dumps(result, indent=2, ensure_ascii=False, default=str)

    if args.output:
        FileIO.write(args.output, output, ensure_dir=True)
        print(f"已还原并保存到: {args.output}")
    else:
        print(output)

    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """执行统计命令

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from dataforge_cli.core.parser import Parser
    from dataforge_cli.core.formatter import Formatter

    data = Parser.parse_file(args.file)
    print(Formatter.format_stats(data))

    return 0


def cmd_server(args: argparse.Namespace) -> int:
    """启动HTTP API服务

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from dataforge_cli.utils.colors import Colors

    print(f"{Colors.green('DataForge HTTP API 服务启动中...')}")
    print(f"  地址: http://{args.host}:{args.port}")
    print(f"  按 Ctrl+C 停止服务")
    print()

    try:
        _run_http_server(args.host, args.port)
    except KeyboardInterrupt:
        print(f"\n{Colors.yellow('服务已停止')}")
        return 0


def _run_http_server(host: str, port: int) -> None:
    """运行简易HTTP服务器

    使用标准库http.server实现。

    Args:
        host: 绑定地址
        port: 端口号
    """
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json as json_mod
    import urllib.parse

    class DataForgeHandler(BaseHTTPRequestHandler):
        """DataForge HTTP请求处理器"""

        def do_GET(self) -> None:
            """处理GET请求"""
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path

            if path == "/" or path == "/health":
                self._send_json({"status": "ok", "version": "1.0.0"})
            elif path == "/help":
                self._send_json({
                    "endpoints": [
                        "GET / - 健康检查",
                        "GET /help - 帮助信息",
                        "POST /query - 查询数据",
                        "POST /convert - 格式转换",
                        "POST /validate - 数据验证",
                    ]
                })
            else:
                self._send_json({"error": "未找到端点"}, status=404)

        def do_POST(self) -> None:
            """处理POST请求"""
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path

            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json_mod.loads(body) if body else {}
            except (json_mod.JSONDecodeError, ValueError) as e:
                self._send_json({"error": f"无效的JSON: {e}"}, status=400)
                return

            if path == "/query":
                self._handle_query(data)
            elif path == "/convert":
                self._handle_convert(data)
            elif path == "/validate":
                self._handle_validate(data)
            else:
                self._send_json({"error": "未找到端点"}, status=404)

        def _handle_query(self, data: dict) -> None:
            """处理查询请求"""
            from dataforge_cli.core.query import QueryEngine

            if "data" not in data or "expression" not in data:
                self._send_json({"error": "需要 data 和 expression 字段"}, status=400)
                return

            try:
                engine = QueryEngine(data["data"])
                result = engine.query(data["expression"])
                self._send_json({"result": result})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)

        def _handle_convert(self, data: dict) -> None:
            """处理转换请求"""
            from dataforge_cli.core.transform import TransformEngine

            if "data" not in data or "to" not in data:
                self._send_json({"error": "需要 data 和 to 字段"}, status=400)
                return

            try:
                result = TransformEngine.convert(data["data"], "json", data["to"])
                self._send_json({"result": result})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)

        def _handle_validate(self, data: dict) -> None:
            """处理验证请求"""
            from dataforge_cli.core.validator import Validator

            if "data" not in data:
                self._send_json({"error": "需要 data 字段"}, status=400)
                return

            try:
                schema = data.get("schema", {})
                validator = Validator(schema)
                result = validator.validate(data["data"])
                self._send_json(result)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)

        def _send_json(self, data: dict, status: int = 200) -> None:
            """发送JSON响应"""
            response = json_mod.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def log_message(self, format: str, *args: Any) -> None:
            """自定义日志格式"""
            from dataforge_cli.utils.colors import Colors
            sys.stderr.write(f"{Colors.dim(f'  [HTTP] {args[0]}')}\n")

    server = HTTPServer((host, port), DataForgeHandler)
    server.serve_forever()


def cmd_tui(args: argparse.Namespace) -> int:
    """启动TUI仪表盘

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    try:
        from dataforge_cli.tui.dashboard import Dashboard
        dashboard = Dashboard(directory=args.directory)
        dashboard.run()
    except ImportError as e:
        print(f"无法启动TUI: {e}", file=sys.stderr)
        print("TUI功能需要终端支持ANSI控制码", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"TUI错误: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
