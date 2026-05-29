.PHONY: all install test lint clean run

# 默认目标
all: install

# 安装到本地环境
install:
	pip install -e .

# 卸载
uninstall:
	pip uninstall dataforge-cli -y

# 运行测试
test:
	python -m pytest dataforge_cli/tests/ -v

# 快速测试（不依赖pytest）
test-quick:
	python -m dataforge_cli.tests.test_parser
	python -m dataforge_cli.tests.test_query
	python -m dataforge_cli.tests.test_transform
	python -m dataforge_cli.tests.test_merge
	python -m dataforge_cli.tests.test_diff

# 代码检查
lint:
	python -m py_compile dataforge_cli/cli.py
	python -m py_compile dataforge_cli/core/parser.py
	python -m py_compile dataforge_cli/core/query.py
	python -m py_compile dataforge_cli/core/transform.py
	python -m py_compile dataforge_cli/core/merge.py
	python -m py_compile dataforge_cli/core/diff.py
	python -m py_compile dataforge_cli/core/template.py
	python -m py_compile dataforge_cli/core/validator.py
	python -m py_compile dataforge_cli/core/formatter.py
	python -m py_compile dataforge_cli/tui/dashboard.py
	python -m py_compile dataforge_cli/utils/colors.py
	python -m py_compile dataforge_cli/utils/file_io.py

# 清理构建产物
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info/

# 运行CLI
run:
	python -m dataforge_cli

# 帮助
help:
	python -m dataforge_cli --help
