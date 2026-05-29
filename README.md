<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-success.svg" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/Tests-106%20Passed-brightgreen.svg" alt="106 Tests Passed" />
  <img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="v1.0.0" />
</p>

<h1 align="center">DataForge-CLI</h1>

<p align="center">
  <strong>轻量级终端 JSON/YAML 数据智能处理与转换引擎</strong>
</p>

<p align="center">
  <a href="#简体中文">简体中文</a> | <a href="#繁體中文">繁體中文</a> | <a href="#english">English</a>
</p>

---

<!-- 截图占位区域 -->
<!--
<p align="center">
  <img src="docs/screenshots/demo.png" alt="DataForge-CLI Demo" width="800" />
</p>
-->

---

<a id="简体中文"></a>

## 简体中文

### 目录

- [项目介绍](#-项目介绍)
- [核心特性](#-核心特性)
- [快速开始](#-快速开始)
- [详细使用指南](#-详细使用指南)
- [设计思路与迭代规划](#-设计思路与迭代规划)
- [安装与部署指南](#-安装与部署指南)
- [贡献指南](#-贡献指南)
- [开源协议](#-开源协议)

---

### 🎉 项目介绍

**DataForge-CLI** 是一款专为开发者打造的轻量级终端数据智能处理与转换引擎。它用纯 Python 标准库实现，**零外部依赖**，安装即用，无需担心环境冲突和依赖地狱。

#### 解决的用户痛点

在日常开发与运维工作中，处理 JSON/YAML 数据是高频场景，但现有工具往往存在以下问题：

- **`jq`** 功能强大但语法学习曲线陡峭，且不支持 YAML/TOML 等格式
- **Python 脚本** 灵活但每次都要写代码，效率低下
- **在线工具** 需要上传数据到第三方服务器，存在隐私风险
- **重型工具**（如 `pandas`）依赖庞大，仅处理一个小 JSON 就要安装一堆库

DataForge-CLI 正是为了解决这些问题而生——**一个命令搞定所有数据操作**。

#### 自研差异化亮点

- **自研 JMESPath 风格查询引擎**：不依赖第三方库，从零实现点号访问、数组索引、通配符、过滤器、管道、聚合函数等完整查询能力
- **多策略深度合并引擎**：支持 append/replace/merge-by-key/prepend 四种数组合并策略，以及 ours/theirs/manual/error 四种冲突解决机制，还提供 dry-run 预览模式
- **递归差异对比引擎**：支持颜色高亮输出、JSON Patch（RFC 6902）格式输出，可忽略指定路径
- **自研模板渲染引擎**：支持变量替换、循环、条件判断、过滤器链、文件包含等完整模板功能
- **内置 JSON Schema 验证器**：覆盖 Draft-07 常用子集，支持自定义验证规则
- **TUI 交互式仪表盘**：终端内直接浏览和操作数据文件

---

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🔧 **零外部依赖** | 纯 Python 标准库实现，`pip install` 即用，无任何第三方依赖 |
| 🔍 **JMESPath 风格查询引擎** | 支持点号访问、数组索引与切片、通配符 `[*]`、过滤器 `[?expr]`、管道 `\|`、多选、聚合函数（`length`/`sum`/`avg`/`sort_by` 等） |
| 🔄 **多格式转换** | JSON ↔ YAML ↔ TOML ↔ CSV ↔ Table 自由互转，一行命令搞定 |
| 🔀 **深度合并引擎** | 四种数组合并策略（append/replace/merge-by-key/prepend），四种冲突解决（ours/theirs/manual/error），支持 dry-run 预览 |
| 📊 **差异对比引擎** | 递归对比、ANSI 颜色高亮、JSON Patch（RFC 6902）输出、路径忽略 |
| 📝 **模板渲染引擎** | 变量替换 `{{ var }}`、循环 `{% for %}`、条件 `{% if %}`、过滤器链 `\| upper`、文件包含 `{% include %}`、注释 `{# #}` |
| ✅ **JSON Schema 验证器** | 支持 type/required/properties/items/minimum/maximum/pattern/enum/const/format 等常用关键字，可扩展自定义规则 |
| 🖥️ **TUI 交互式仪表盘** | 终端内可视化浏览数据文件，支持目录导航 |
| 🌐 **HTTP API 服务** | 内置 HTTP 服务器，将数据操作能力暴露为 REST API |
| 🧪 **106 个单元测试** | 全部通过，代码质量有保障 |

---

### 🚀 快速开始

#### 环境要求

- **Python 3.8+**（支持 3.8、3.9、3.10、3.11、3.12）
- pip 包管理器

#### 安装

```bash
# 方式一：从 PyPI 安装（推荐）
pip install git+https://github.com/gitstq/DataForge-CLI.git

# 方式二：克隆仓库后本地安装
git clone https://github.com/gitstq/DataForge-CLI.git
cd DataForge-CLI
pip install .
```

#### 本地启动

```bash
# 查看版本
dataforge --version

# 查看帮助
dataforge --help

# 快速体验：查询 JSON 数据
echo '{"users": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 18}]}' > data.json
dataforge query data.json "users[?age > 18].name"

# 输出: ["Alice"]
```

---

### 📖 详细使用指南

#### 命令总览

| 命令 | 说明 | 示例 |
|------|------|------|
| `query` | 查询数据 | `dataforge query data.json "users[0].name"` |
| `convert` | 格式转换 | `dataforge convert data.json --to yaml` |
| `merge` | 深度合并 | `dataforge merge a.json b.json --strategy append` |
| `diff` | 差异对比 | `dataforge diff old.json new.json --format colorized` |
| `validate` | Schema 验证 | `dataforge validate data.json --schema schema.json` |
| `template` | 模板渲染 | `dataforge template tpl.txt --data data.json` |
| `format` | 格式化数据 | `dataforge format data.json --indent 4 --sort-keys` |
| `flatten` | 展平嵌套 | `dataforge flatten data.json --separator "."` |
| `unflatten` | 还原嵌套 | `dataforge unflatten flat.json --separator "."` |
| `stats` | 数据统计 | `dataforge stats data.json` |
| `server` | HTTP API 服务 | `dataforge server --port 8080` |
| `tui` | TUI 仪表盘 | `dataforge tui` |

---

#### `query` — 查询数据

使用 JMESPath 风格表达式从 JSON/YAML 数据中提取信息。

```bash
dataforge query <file> <expression> [--output FORMAT] [--color]
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `file` | 数据文件路径 |
| `expression` | JMESPath 风格查询表达式 |
| `-o, --output` | 输出格式：`json`（默认）、`yaml`、`table`、`tree` |
| `--color` | 启用彩色输出 |

**使用示例：**

```bash
# 点号访问
dataforge query data.json "users[0].name"

# 通配符：获取所有用户名
dataforge query data.json "users[*].name"

# 过滤器：筛选年龄大于 18 的用户
dataforge query data.json "users[?age > 18]"

# 聚合函数：计算用户数量
dataforge query data.json "length(users)"

# 排序：按年龄排序
dataforge query data.json "sort_by(users, age)"

# 管道操作
dataforge query data.json "users | [?age > 18] | [0].name"

# 以表格形式输出
dataforge query data.json "users[*]" --output table
```

---

#### `convert` — 格式转换

在 JSON、YAML、TOML、CSV、Table 之间自由转换。

```bash
dataforge convert <file> --to FORMAT [--output FILE] [--indent N]
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `file` | 输入文件路径 |
| `-t, --to` | 目标格式：`json`、`yaml`、`toml`、`csv`、`table` |
| `-o, --output` | 输出文件路径（不指定则输出到 stdout） |
| `--indent` | 缩进空格数（默认 2） |

**使用示例：**

```bash
# JSON 转 YAML
dataforge convert data.json --to yaml --output data.yaml

# JSON 转 CSV
dataforge convert data.json --to csv --output data.csv

# JSON 转 TOML
dataforge convert config.json --to toml --output config.toml

# 以表格形式展示
dataforge convert users.json --to table
```

---

#### `merge` — 深度合并

递归合并多个数据文件，支持多种合并策略和冲突解决机制。

```bash
dataforge merge <file1> <file2> [file3 ...] [--strategy STRATEGY] [--conflict STRATEGY] [--output FILE] [--dry-run]
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `files` | 要合并的文件路径（至少 2 个） |
| `-s, --strategy` | 数组合并策略：`replace`（默认）、`append`、`prepend`、`merge-by-key` |
| `-c, --conflict` | 冲突解决策略：`theirs`（默认）、`ours`、`manual`、`error` |
| `-o, --output` | 输出文件路径 |
| `--dry-run` | 预览合并结果，不实际写入 |

**使用示例：**

```bash
# 基本合并（默认 replace 策略）
dataforge merge base.json override.json --output merged.json

# 追加数组合并
dataforge merge base.json update.json --strategy append --output merged.json

# 按键值合并数组
dataforge merge users1.json users2.json --strategy merge-by-key --output merged.json

# 预览合并结果
dataforge merge a.json b.json --dry-run

# 冲突时保留原值
dataforge merge a.json b.json --conflict ours --output merged.json
```

---

#### `diff` — 差异对比

递归对比两个数据文件，输出详细的差异报告。

```bash
dataforge diff <file1> <file2> [--ignore PATH] [--format FORMAT] [--output FILE]
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `file1` | 旧文件路径 |
| `file2` | 新文件路径 |
| `-i, --ignore` | 忽略的路径模式（支持通配符 `*`） |
| `-f, --format` | 输出格式：`colorized`（默认）、`text`、`patch`、`summary` |
| `-o, --output` | 输出文件路径 |

**使用示例：**

```bash
# 彩色差异对比
dataforge diff old.json new.json --format colorized

# JSON Patch 格式输出（RFC 6902）
dataforge diff old.json new.json --format patch

# 差异摘要
dataforge diff old.json new.json --format summary

# 忽略特定路径
dataforge diff old.json new.json --ignore "timestamp" --ignore "metadata.*"
```

---

#### `validate` — Schema 验证

使用 JSON Schema 验证数据文件的合法性。

```bash
dataforge validate <file> [--schema FILE] [--report FILE]
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `file` | 数据文件路径 |
| `-s, --schema` | Schema 文件路径（不指定则执行基本类型检查） |
| `--report` | 生成验证报告到指定文件 |

**使用示例：**

```bash
# 使用 Schema 文件验证
dataforge validate data.json --schema schema.json

# 生成验证报告
dataforge validate config.json --schema config-schema.json --report report.txt

# 基本类型检查（无 Schema）
dataforge validate data.json
```

---

#### `template` — 模板渲染

基于数据渲染模板文件，支持变量替换、循环、条件、过滤器等功能。

```bash
dataforge template <template> --data <file> [--output FILE] [--var key=value]
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `template` | 模板文件路径或模板字符串 |
| `-d, --data` | 数据文件路径 |
| `-o, --output` | 输出文件路径 |
| `-v, --var` | 额外变量（格式：`key=value`） |

**模板语法：**

```django
{# 注释 #}
{{ variable }}              {# 变量替换 #}
{{ user.name }}             {# 点号访问 #}
{{ name | upper }}          {# 过滤器 #}
{{ price | round:2 }}       {# 带参数的过滤器 #}
{{ items | join:", " }}     {# 列表连接 #}

{% for item in items %}     {# 循环 #}
  - {{ item }}
{% endfor %}

{% if status == "active" %} {# 条件 #}
  已激活
{% elif status == "pending" %}
  待处理
{% else %}
  未知状态
{% endif %}

{% include "header.txt" %}  {# 文件包含 #}
```

**使用示例：**

```bash
# 使用模板文件渲染
dataforge template report.tpl --data data.json --output report.txt

# 使用内联模板
dataforge template "Hello, {{ name }}!" --data user.json

# 传入额外变量
dataforge template tpl.txt --data data.json --var title="月度报告" --var date="2024-01"
```

---

#### `format` — 格式化数据

美化和格式化 JSON/YAML 数据。

```bash
dataforge format <file> [--indent N] [--sort-keys] [--minify] [--output FORMAT] [--output FILE]
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `file` | 数据文件路径 |
| `--indent` | 缩进空格数（默认 2） |
| `--sort-keys` | 按键名排序 |
| `--minify` | 压缩输出（去除空白） |
| `--output-format` | 输出格式：`json`（默认）、`yaml`、`table`、`tree` |
| `-o, --output` | 输出文件路径 |

**使用示例：**

```bash
# 美化 JSON
dataforge format data.json --indent 4

# 按键名排序
dataforge format data.json --sort-keys

# 压缩 JSON
dataforge format data.json --minify

# 以树形结构展示
dataforge format data.json --output-format tree
```

---

#### `flatten` / `unflatten` — 展平与还原嵌套

将嵌套数据展平为单层结构，或反向还原。

```bash
# 展平嵌套
dataforge flatten <file> [--separator SEP] [--output FILE]

# 还原嵌套
dataforge unflatten <file> [--separator SEP] [--output FILE]
```

**使用示例：**

```bash
# 展平嵌套数据
dataforge flatten data.json --separator "."
# {"a": {"b": {"c": 1}}} → {"a.b.c": 1}

# 还原嵌套数据
dataforge unflatten flat.json --separator "."
# {"a.b.c": 1} → {"a": {"b": {"c": 1}}}
```

---

#### `stats` — 数据统计

快速获取数据文件的结构统计信息。

```bash
dataforge stats <file>
```

**使用示例：**

```bash
dataforge stats data.json
# 输出：数据类型、键数量、嵌套深度、值类型分布等
```

---

#### `server` — HTTP API 服务

启动内置 HTTP 服务器，将数据操作能力暴露为 REST API。

```bash
dataforge server [--port PORT] [--host HOST]
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `-p, --port` | 端口号（默认 8080） |
| `--host` | 绑定地址（默认 127.0.0.1） |

**API 端点：**

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/help` | GET | 帮助信息 |
| `/query` | POST | 查询数据 |
| `/convert` | POST | 格式转换 |
| `/validate` | POST | 数据验证 |

**使用示例：**

```bash
# 启动服务
dataforge server --port 8080

# 调用 API
curl -X POST http://127.0.0.1:8080/query \
  -H "Content-Type: application/json" \
  -d '{"data": {"users": [{"name": "Alice"}]}, "expression": "users[0].name"}'
```

---

#### `tui` — TUI 交互式仪表盘

在终端内启动交互式数据浏览仪表盘。

```bash
dataforge tui [--directory DIR]
```

**使用示例：**

```bash
# 启动 TUI 仪表盘
dataforge tui

# 指定初始浏览目录
dataforge tui --directory ./configs
```

---

### 💡 设计思路与迭代规划

#### 设计理念

DataForge-CLI 的核心设计理念是 **"简单即正义"**：

1. **零依赖哲学**：纯 Python 标准库实现，杜绝依赖地狱。在任何 Python 环境中安装即用，特别适合 CI/CD 流水线和容器化部署场景。
2. **Unix 哲学**：每个命令做好一件事，通过管道组合完成复杂操作。输出默认到 stdout，方便与其他工具集成。
3. **自研核心引擎**：查询、合并、对比、模板、验证五大引擎全部自研，不依赖 `jmespath`、`jsonpatch` 等第三方库，保证可控性和轻量性。

#### 技术选型原因

| 决策 | 原因 |
|------|------|
| 纯 Python 标准库 | 消除依赖冲突，降低安装失败率，提升启动速度 |
| argparse | 标准库自带，零依赖实现 CLI 参数解析 |
| 自研查询引擎 | 避免引入 jmespath 依赖，同时提供更灵活的扩展能力 |
| 自研模板引擎 | Jinja2 过于庞大，自研引擎覆盖 80% 常用场景且零依赖 |
| ANSI 颜色输出 | 终端原生支持，无需额外库即可实现彩色差异高亮 |

#### 后续计划

- [ ] **流式处理**：支持大文件流式读取和增量处理，突破内存限制
- [ ] **插件系统**：支持自定义命令和过滤器插件
- [ ] **Shell 补全**：提供 Bash/Zsh/Fish 自动补全脚本
- [ ] **配置文件**：支持 `~/.dataforgerc` 全局配置
- [ ] **性能优化**：对大文件场景引入惰性求值和缓存机制
- [ ] **更多格式**：支持 XML、INI、Properties 等格式
- [ ] **Watch 模式**：监控文件变更并自动执行操作

---

### 📦 安装与部署指南

#### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/DataForge-CLI.git
cd DataForge-CLI

# 安装
pip install .

# 或使用开发模式安装（可编辑模式）
pip install -e .
```

#### 开发环境配置

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行单个测试文件
pytest tests/test_query.py -v

# 运行特定测试
pytest tests/test_query.py::TestQueryEngine::test_dot_access -v
```

#### 系统要求

| 项目 | 要求 |
|------|------|
| Python | >= 3.8 |
| 操作系统 | Linux / macOS / Windows |
| 依赖 | 无（纯标准库） |

---

### 🤝 贡献指南

我们欢迎并感谢所有形式的贡献！无论是提交 Bug 报告、改进建议还是代码 PR。

#### 提交 Issue

- 使用 **清晰的标题** 描述问题
- 提供 **最小可复现示例**
- 附上 **运行环境信息**（Python 版本、操作系统）
- 如有必要，附上 **错误日志截图**

#### 提交 Pull Request

1. **Fork** 本仓库
2. 创建 **特性分支**（`git checkout -b feature/amazing-feature`）
3. **编写代码** 并确保通过所有测试（`pytest`）
4. **提交变更**（`git commit -m 'feat: add amazing feature'`）
5. **推送到远程**（`git push origin feature/amazing-feature`）
6. 创建 **Pull Request**

#### Commit 规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
feat: 新增特性
fix: 修复 Bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具链相关
```

---

### 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

```
MIT License

Copyright (c) 2024 DataForge Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<a id="繁體中文"></a>

## 繁體中文

### 目錄

- [專案介紹](#-專案介紹-1)
- [核心特性](#-核心特性-1)
- [快速開始](#-快速開始-1)
- [詳細使用指南](#-詳細使用指南-1)
- [設計思路與迭代規劃](#-設計思路與迭代規劃-1)
- [安裝與部署指南](#-安裝與部署指南-1)
- [貢獻指南](#-貢獻指南-1)
- [開源授權](#-開源授權-1)

---

### 🎉 專案介紹

**DataForge-CLI** 是一款專為開發者打造的輕量級終端資料智慧處理與轉換引擎。它以純 Python 標準函式庫實作，**零外部依賴**，安裝即可使用，無須擔心環境衝突與依賴地獄。

#### 解決的使用者痛點

在日常開發與維運工作中，處理 JSON/YAML 資料是高頻場景，但現有工具往往存在以下問題：

- **`jq`** 功能強大但語法學習曲線陡峭，且不支援 YAML/TOML 等格式
- **Python 腳本** 雖然靈活，但每次都要寫程式碼，效率低落
- **線上工具** 需要上傳資料到第三方伺服器，存在隱私風險
- **重型工具**（如 `pandas`）依賴龐大，僅處理一個小 JSON 就要安裝一堆函式庫

DataForge-CLI 正是為了解決這些問題而生——**一個指令搞定所有資料操作**。

#### 自研差異化亮點

- **自研 JMESPath 風格查詢引擎**：不依賴第三方函式庫，從零實作點號存取、陣列索引、萬用字元、過濾器、管道、聚合函式等完整查詢能力
- **多策略深度合併引擎**：支援 append/replace/merge-by-key/prepend 四種陣列合併策略，以及 ours/theirs/manual/error 四種衝突解決機制，並提供 dry-run 預覽模式
- **遞迴差異對比引擎**：支援顏色高亮輸出、JSON Patch（RFC 6902）格式輸出，可忽略指定路徑
- **自研模板渲染引擎**：支援變數替換、迴圈、條件判斷、過濾器鏈、檔案包含等完整模板功能
- **內建 JSON Schema 驗證器**：涵蓋 Draft-07 常用子集，支援自訂驗證規則
- **TUI 互動式儀表板**：終端內直接瀏覽與操作資料檔案

---

### ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🔧 **零外部依賴** | 純 Python 標準函式庫實作，`pip install` 即用，無任何第三方依賴 |
| 🔍 **JMESPath 風格查詢引擎** | 支援點號存取、陣列索引與切片、萬用字元 `[*]`、過濾器 `[?expr]`、管道 `\|`、多選、聚合函式（`length`/`sum`/`avg`/`sort_by` 等） |
| 🔄 **多格式轉換** | JSON ↔ YAML ↔ TOML ↔ CSV ↔ Table 自由互轉，一行指令搞定 |
| 🔀 **深度合併引擎** | 四種陣列合併策略（append/replace/merge-by-key/prepend），四種衝突解決（ours/theirs/manual/error），支援 dry-run 預覽 |
| 📊 **差異對比引擎** | 遞迴對比、ANSI 顏色高亮、JSON Patch（RFC 6902）輸出、路徑忽略 |
| 📝 **模板渲染引擎** | 變數替換 `{{ var }}`、迴圈 `{% for %}`、條件 `{% if %}`、過濾器鏈 `\| upper`、檔案包含 `{% include %}`、註解 `{# #}` |
| ✅ **JSON Schema 驗證器** | 支援 type/required/properties/items/minimum/maximum/pattern/enum/const/format 等常用關鍵字，可擴充自訂規則 |
| 🖥️ **TUI 互動式儀表板** | 終端內視覺化瀏覽資料檔案，支援目錄導覽 |
| 🌐 **HTTP API 服務** | 內建 HTTP 伺服器，將資料操作能力暴露為 REST API |
| 🧪 **106 個單元測試** | 全部通過，程式碼品質有保障 |

---

### 🚀 快速開始

#### 環境需求

- **Python 3.8+**（支援 3.8、3.9、3.10、3.11、3.12）
- pip 套件管理器

#### 安裝

```bash
# 方式一：從 PyPI 安裝（推薦）
pip install git+https://github.com/gitstq/DataForge-CLI.git

# 方式二：克隆儲存庫後本機安裝
git clone https://github.com/gitstq/DataForge-CLI.git
cd DataForge-CLI
pip install .
```

#### 本機啟動

```bash
# 查看版本
dataforge --version

# 查看說明
dataforge --help

# 快速體驗：查詢 JSON 資料
echo '{"users": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 18}]}' > data.json
dataforge query data.json "users[?age > 18].name"

# 輸出: ["Alice"]
```

---

### 📖 詳細使用指南

#### 指令總覽

| 指令 | 說明 | 範例 |
|------|------|------|
| `query` | 查詢資料 | `dataforge query data.json "users[0].name"` |
| `convert` | 格式轉換 | `dataforge convert data.json --to yaml` |
| `merge` | 深度合併 | `dataforge merge a.json b.json --strategy append` |
| `diff` | 差異對比 | `dataforge diff old.json new.json --format colorized` |
| `validate` | Schema 驗證 | `dataforge validate data.json --schema schema.json` |
| `template` | 模板渲染 | `dataforge template tpl.txt --data data.json` |
| `format` | 格式化資料 | `dataforge format data.json --indent 4 --sort-keys` |
| `flatten` | 展平巢狀 | `dataforge flatten data.json --separator "."` |
| `unflatten` | 還原巢狀 | `dataforge unflatten flat.json --separator "."` |
| `stats` | 資料統計 | `dataforge stats data.json` |
| `server` | HTTP API 服務 | `dataforge server --port 8080` |
| `tui` | TUI 儀表板 | `dataforge tui` |

---

#### `query` — 查詢資料

使用 JMESPath 風格運算式從 JSON/YAML 資料中擷取資訊。

```bash
dataforge query <file> <expression> [--output FORMAT] [--color]
```

**參數說明：**

| 參數 | 說明 |
|------|------|
| `file` | 資料檔案路徑 |
| `expression` | JMESPath 風格查詢運算式 |
| `-o, --output` | 輸出格式：`json`（預設）、`yaml`、`table`、`tree` |
| `--color` | 啟用彩色輸出 |

**使用範例：**

```bash
# 點號存取
dataforge query data.json "users[0].name"

# 萬用字元：取得所有使用者名稱
dataforge query data.json "users[*].name"

# 過濾器：篩選年齡大於 18 的使用者
dataforge query data.json "users[?age > 18]"

# 聚合函式：計算使用者數量
dataforge query data.json "length(users)"

# 排序：依年齡排序
dataforge query data.json "sort_by(users, age)"

# 管道操作
dataforge query data.json "users | [?age > 18] | [0].name"

# 以表格形式輸出
dataforge query data.json "users[*]" --output table
```

---

#### `convert` — 格式轉換

在 JSON、YAML、TOML、CSV、Table 之間自由轉換。

```bash
dataforge convert <file> --to FORMAT [--output FILE] [--indent N]
```

**參數說明：**

| 參數 | 說明 |
|------|------|
| `file` | 輸入檔案路徑 |
| `-t, --to` | 目標格式：`json`、`yaml`、`toml`、`csv`、`table` |
| `-o, --output` | 輸出檔案路徑（不指定則輸出至 stdout） |
| `--indent` | 縮排空格數（預設 2） |

**使用範例：**

```bash
# JSON 轉 YAML
dataforge convert data.json --to yaml --output data.yaml

# JSON 轉 CSV
dataforge convert data.json --to csv --output data.csv

# JSON 轉 TOML
dataforge convert config.json --to toml --output config.toml

# 以表格形式展示
dataforge convert users.json --to table
```

---

#### `merge` — 深度合併

遞迴合併多個資料檔案，支援多種合併策略與衝突解決機制。

```bash
dataforge merge <file1> <file2> [file3 ...] [--strategy STRATEGY] [--conflict STRATEGY] [--output FILE] [--dry-run]
```

**參數說明：**

| 參數 | 說明 |
|------|------|
| `files` | 要合併的檔案路徑（至少 2 個） |
| `-s, --strategy` | 陣列合併策略：`replace`（預設）、`append`、`prepend`、`merge-by-key` |
| `-c, --conflict` | 衝突解決策略：`theirs`（預設）、`ours`、`manual`、`error` |
| `-o, --output` | 輸出檔案路徑 |
| `--dry-run` | 預覽合併結果，不實際寫入 |

**使用範例：**

```bash
# 基本合併（預設 replace 策略）
dataforge merge base.json override.json --output merged.json

# 追加陣列合併
dataforge merge base.json update.json --strategy append --output merged.json

# 依鍵值合併陣列
dataforge merge users1.json users2.json --strategy merge-by-key --output merged.json

# 預覽合併結果
dataforge merge a.json b.json --dry-run

# 衝突時保留原值
dataforge merge a.json b.json --conflict ours --output merged.json
```

---

#### `diff` — 差異對比

遞迴對比兩個資料檔案，輸出詳細的差異報告。

```bash
dataforge diff <file1> <file2> [--ignore PATH] [--format FORMAT] [--output FILE]
```

**參數說明：**

| 參數 | 說明 |
|------|------|
| `file1` | 舊檔案路徑 |
| `file2` | 新檔案路徑 |
| `-i, --ignore` | 忽略的路徑模式（支援萬用字元 `*`） |
| `-f, --format` | 輸出格式：`colorized`（預設）、`text`、`patch`、`summary` |
| `-o, --output` | 輸出檔案路徑 |

**使用範例：**

```bash
# 彩色差異對比
dataforge diff old.json new.json --format colorized

# JSON Patch 格式輸出（RFC 6902）
dataforge diff old.json new.json --format patch

# 差異摘要
dataforge diff old.json new.json --format summary

# 忽略特定路徑
dataforge diff old.json new.json --ignore "timestamp" --ignore "metadata.*"
```

---

#### `validate` — Schema 驗證

使用 JSON Schema 驗證資料檔案的合法性。

```bash
dataforge validate <file> [--schema FILE] [--report FILE]
```

**參數說明：**

| 參數 | 說明 |
|------|------|
| `file` | 資料檔案路徑 |
| `-s, --schema` | Schema 檔案路徑（不指定則執行基本型別檢查） |
| `--report` | 產生驗證報告至指定檔案 |

**使用範例：**

```bash
# 使用 Schema 檔案驗證
dataforge validate data.json --schema schema.json

# 產生驗證報告
dataforge validate config.json --schema config-schema.json --report report.txt

# 基本型別檢查（無 Schema）
dataforge validate data.json
```

---

#### `template` — 模板渲染

基於資料渲染模板檔案，支援變數替換、迴圈、條件、過濾器等功能。

```bash
dataforge template <template> --data <file> [--output FILE] [--var key=value]
```

**參數說明：**

| 參數 | 說明 |
|------|------|
| `template` | 模板檔案路徑或模板字串 |
| `-d, --data` | 資料檔案路徑 |
| `-o, --output` | 輸出檔案路徑 |
| `-v, --var` | 額外變數（格式：`key=value`） |

**模板語法：**

```django
{# 註解 #}
{{ variable }}              {# 變數替換 #}
{{ user.name }}             {# 點號存取 #}
{{ name | upper }}          {# 過濾器 #}
{{ price | round:2 }}       {# 帶參數的過濾器 #}
{{ items | join:", " }}     {# 列表連接 #}

{% for item in items %}     {# 迴圈 #}
  - {{ item }}
{% endfor %}

{% if status == "active" %} {# 條件 #}
  已啟用
{% elif status == "pending" %}
  待處理
{% else %}
  未知狀態
{% endif %}

{% include "header.txt" %}  {# 檔案包含 #}
```

**使用範例：**

```bash
# 使用模板檔案渲染
dataforge template report.tpl --data data.json --output report.txt

# 使用內聯模板
dataforge template "Hello, {{ name }}!" --data user.json

# 傳入額外變數
dataforge template tpl.txt --data data.json --var title="月度報告" --var date="2024-01"
```

---

#### `format` — 格式化資料

美化與格式化 JSON/YAML 資料。

```bash
dataforge format <file> [--indent N] [--sort-keys] [--minify] [--output FORMAT] [--output FILE]
```

**參數說明：**

| 參數 | 說明 |
|------|------|
| `file` | 資料檔案路徑 |
| `--indent` | 縮排空格數（預設 2） |
| `--sort-keys` | 依鍵名排序 |
| `--minify` | 壓縮輸出（去除空白） |
| `--output-format` | 輸出格式：`json`（預設）、`yaml`、`table`、`tree` |
| `-o, --output` | 輸出檔案路徑 |

**使用範例：**

```bash
# 美化 JSON
dataforge format data.json --indent 4

# 依鍵名排序
dataforge format data.json --sort-keys

# 壓縮 JSON
dataforge format data.json --minify

# 以樹狀結構展示
dataforge format data.json --output-format tree
```

---

#### `flatten` / `unflatten` — 展平與還原巢狀

將巢狀資料展平為單層結構，或反向還原。

```bash
# 展平巢狀
dataforge flatten <file> [--separator SEP] [--output FILE]

# 還原巢狀
dataforge unflatten <file> [--separator SEP] [--output FILE]
```

**使用範例：**

```bash
# 展平巢狀資料
dataforge flatten data.json --separator "."
# {"a": {"b": {"c": 1}}} → {"a.b.c": 1}

# 還原巢狀資料
dataforge unflatten flat.json --separator "."
# {"a.b.c": 1} → {"a": {"b": {"c": 1}}}
```

---

#### `stats` — 資料統計

快速取得資料檔案的結構統計資訊。

```bash
dataforge stats <file>
```

**使用範例：**

```bash
dataforge stats data.json
# 輸出：資料型別、鍵數量、巢狀深度、值型別分佈等
```

---

#### `server` — HTTP API 服務

啟動內建 HTTP 伺服器，將資料操作能力暴露為 REST API。

```bash
dataforge server [--port PORT] [--host HOST]
```

**參數說明：**

| 參數 | 說明 |
|------|------|
| `-p, --port` | 連接埠號（預設 8080） |
| `--host` | 綁定位址（預設 127.0.0.1） |

**API 端點：**

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | 健康檢查 |
| `/help` | GET | 說明資訊 |
| `/query` | POST | 查詢資料 |
| `/convert` | POST | 格式轉換 |
| `/validate` | POST | 資料驗證 |

**使用範例：**

```bash
# 啟動服務
dataforge server --port 8080

# 呼叫 API
curl -X POST http://127.0.0.1:8080/query \
  -H "Content-Type: application/json" \
  -d '{"data": {"users": [{"name": "Alice"}]}, "expression": "users[0].name"}'
```

---

#### `tui` — TUI 互動式儀表板

在終端內啟動互動式資料瀏覽儀表板。

```bash
dataforge tui [--directory DIR]
```

**使用範例：**

```bash
# 啟動 TUI 儀表板
dataforge tui

# 指定初始瀏覽目錄
dataforge tui --directory ./configs
```

---

### 💡 設計思路與迭代規劃

#### 設計理念

DataForge-CLI 的核心設計理念是 **「簡單即正義」**：

1. **零依賴哲學**：純 Python 標準函式庫實作，杜絕依賴地獄。在任何 Python 環境中安裝即可使用，特別適合 CI/CD 流水線與容器化部署場景。
2. **Unix 哲學**：每個指令做好一件事，透過管道組合完成複雜操作。輸出預設至 stdout，方便與其他工具整合。
3. **自研核心引擎**：查詢、合併、對比、模板、驗證五大引擎全部自研，不依賴 `jmespath`、`jsonpatch` 等第三方函式庫，保證可控性與輕量性。

#### 技術選型原因

| 決策 | 原因 |
|------|------|
| 純 Python 標準函式庫 | 消除依賴衝突，降低安裝失敗率，提升啟動速度 |
| argparse | 標準函式庫內建，零依賴實作 CLI 參數解析 |
| 自研查詢引擎 | 避免引入 jmespath 依賴，同時提供更靈活的擴充能力 |
| 自研模板引擎 | Jinja2 過於龐大，自研引擎覆蓋 80% 常用場景且零依賴 |
| ANSI 顏色輸出 | 終端原生支援，無需額外函式庫即可實現彩色差異高亮 |

#### 後續計畫

- [ ] **串流處理**：支援大檔案串流讀取與增量處理，突破記憶體限制
- [ ] **外掛系統**：支援自訂指令與過濾器外掛
- [ ] **Shell 補全**：提供 Bash/Zsh/Fish 自動補全腳本
- [ ] **設定檔**：支援 `~/.dataforgerc` 全域設定
- [ ] **效能最佳化**：對大檔案場景引入惰性求值與快取機制
- [ ] **更多格式**：支援 XML、INI、Properties 等格式
- [ ] **Watch 模式**：監控檔案變更並自動執行操作

---

### 📦 安裝與部署指南

#### 從原始碼安裝

```bash
# 克隆儲存庫
git clone https://github.com/gitstq/DataForge-CLI.git
cd DataForge-CLI

# 安裝
pip install .

# 或使用開發模式安裝（可編輯模式）
pip install -e .
```

#### 開發環境設定

```bash
# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest

# 執行單一測試檔案
pytest tests/test_query.py -v

# 執行特定測試
pytest tests/test_query.py::TestQueryEngine::test_dot_access -v
```

#### 系統需求

| 項目 | 需求 |
|------|------|
| Python | >= 3.8 |
| 作業系統 | Linux / macOS / Windows |
| 依賴 | 無（純標準函式庫） |

---

### 🤝 貢獻指南

我們歡迎並感謝所有形式的貢獻！無論是提交 Bug 回報、改進建議還是程式碼 PR。

#### 提交 Issue

- 使用 **清晰的標題** 描述問題
- 提供 **最小可重現範例**
- 附上 **執行環境資訊**（Python 版本、作業系統）
- 如有必要，附上 **錯誤日誌截圖**

#### 提交 Pull Request

1. **Fork** 本儲存庫
2. 建立 **特性分支**（`git checkout -b feature/amazing-feature`）
3. **編寫程式碼** 並確保通過所有測試（`pytest`）
4. **提交變更**（`git commit -m 'feat: add amazing feature'`）
5. **推送至遠端**（`git push origin feature/amazing-feature`）
6. 建立 **Pull Request**

#### Commit 規範

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

```
feat: 新增特性
fix: 修復 Bug
docs: 文件更新
style: 程式碼格式調整
refactor: 程式碼重構
test: 測試相關
chore: 建置/工具鏈相關
```

---

### 📄 開源授權

本專案基於 [MIT License](LICENSE) 開源。

```
MIT License

Copyright (c) 2024 DataForge Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<a id="english"></a>

## English

### Table of Contents

- [Project Introduction](#-project-introduction)
- [Core Features](#-core-features)
- [Quick Start](#-quick-start)
- [Detailed Usage Guide](#-detailed-usage-guide)
- [Design Philosophy & Roadmap](#-design-philosophy--roadmap)
- [Installation & Deployment](#-installation--deployment)
- [Contributing Guide](#-contributing-guide)
- [License](#-license)

---

### 🎉 Project Introduction

**DataForge-CLI** is a lightweight, intelligent terminal-based data processing and transformation engine designed for developers. Built entirely with the Python standard library, it has **zero external dependencies** -- install it and start using it immediately, with no worries about dependency conflicts or dependency hell.

#### Pain Points It Solves

Processing JSON/YAML data is a frequent task in day-to-day development and operations, yet existing tools often fall short:

- **`jq`** is powerful but has a steep learning curve, and does not support YAML/TOML formats
- **Python scripts** are flexible but require writing code every time, which is inefficient
- **Online tools** require uploading data to third-party servers, raising privacy concerns
- **Heavyweight tools** (like `pandas`) have massive dependency trees just to process a small JSON file

DataForge-CLI was born to solve these problems -- **one command is all you need for any data operation**.

#### Key Differentiators

- **Custom JMESPath-style query engine**: Built from scratch without third-party libraries, offering full query capabilities including dot notation, array indexing, wildcards, filters, pipes, and aggregate functions
- **Multi-strategy deep merge engine**: Supports four array merge strategies (append/replace/merge-by-key/prepend), four conflict resolution mechanisms (ours/theirs/manual/error), and a dry-run preview mode
- **Recursive diff engine**: Colorized terminal output, JSON Patch (RFC 6902) format output, and path-based ignore patterns
- **Custom template rendering engine**: Full template support including variable substitution, loops, conditionals, filter chains, file includes, and comments
- **Built-in JSON Schema validator**: Covers the Draft-07 commonly-used subset with extensible custom validation rules
- **TUI interactive dashboard**: Browse and interact with data files directly in the terminal

---

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔧 **Zero External Dependencies** | Pure Python standard library -- `pip install` and go, no third-party packages required |
| 🔍 **JMESPath-style Query Engine** | Dot notation, array indexing & slicing, wildcards `[*]`, filters `[?expr]`, pipes `\|`, multi-select, aggregate functions (`length`/`sum`/`avg`/`sort_by`, etc.) |
| 🔄 **Multi-format Conversion** | Bidirectional conversion between JSON, YAML, TOML, CSV, and Table formats |
| 🔀 **Deep Merge Engine** | Four array strategies (append/replace/merge-by-key/prepend), four conflict modes (ours/theirs/manual/error), dry-run preview |
| 📊 **Diff Engine** | Recursive comparison, ANSI color highlighting, JSON Patch (RFC 6902) output, path ignore patterns |
| 📝 **Template Rendering Engine** | Variable substitution `{{ var }}`, loops `{% for %}`, conditionals `{% if %}`, filter chains `\| upper`, file includes `{% include %}`, comments `{# #}` |
| ✅ **JSON Schema Validator** | Supports type/required/properties/items/minimum/maximum/pattern/enum/const/format keywords, extensible with custom rules |
| 🖥️ **TUI Interactive Dashboard** | Visual data file browsing in the terminal with directory navigation |
| 🌐 **HTTP API Server** | Built-in HTTP server exposing data operations as REST API endpoints |
| 🧪 **106 Unit Tests** | All passing, ensuring code quality and reliability |

---

### 🚀 Quick Start

#### Requirements

- **Python 3.8+** (supports 3.8, 3.9, 3.10, 3.11, 3.12)
- pip package manager

#### Installation

```bash
# Option 1: Install from GitHub (recommended)
pip install git+https://github.com/gitstq/DataForge-CLI.git

# Option 2: Clone and install locally
git clone https://github.com/gitstq/DataForge-CLI.git
cd DataForge-CLI
pip install .
```

#### Getting Started

```bash
# Check version
dataforge --version

# View help
dataforge --help

# Quick demo: query JSON data
echo '{"users": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 18}]}' > data.json
dataforge query data.json "users[?age > 18].name"

# Output: ["Alice"]
```

---

### 📖 Detailed Usage Guide

#### Command Overview

| Command | Description | Example |
|---------|-------------|---------|
| `query` | Query data | `dataforge query data.json "users[0].name"` |
| `convert` | Format conversion | `dataforge convert data.json --to yaml` |
| `merge` | Deep merge | `dataforge merge a.json b.json --strategy append` |
| `diff` | Compare differences | `dataforge diff old.json new.json --format colorized` |
| `validate` | Schema validation | `dataforge validate data.json --schema schema.json` |
| `template` | Template rendering | `dataforge template tpl.txt --data data.json` |
| `format` | Format data | `dataforge format data.json --indent 4 --sort-keys` |
| `flatten` | Flatten nested data | `dataforge flatten data.json --separator "."` |
| `unflatten` | Unflatten data | `dataforge unflatten flat.json --separator "."` |
| `stats` | Data statistics | `dataforge stats data.json` |
| `server` | HTTP API server | `dataforge server --port 8080` |
| `tui` | TUI dashboard | `dataforge tui` |

---

#### `query` -- Query Data

Extract information from JSON/YAML data using JMESPath-style expressions.

```bash
dataforge query <file> <expression> [--output FORMAT] [--color]
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `file` | Path to the data file |
| `expression` | JMESPath-style query expression |
| `-o, --output` | Output format: `json` (default), `yaml`, `table`, `tree` |
| `--color` | Enable colorized output |

**Examples:**

```bash
# Dot notation access
dataforge query data.json "users[0].name"

# Wildcard: get all user names
dataforge query data.json "users[*].name"

# Filter: users older than 18
dataforge query data.json "users[?age > 18]"

# Aggregate function: count users
dataforge query data.json "length(users)"

# Sort by age
dataforge query data.json "sort_by(users, age)"

# Pipe operations
dataforge query data.json "users | [?age > 18] | [0].name"

# Output as table
dataforge query data.json "users[*]" --output table
```

---

#### `convert` -- Format Conversion

Convert between JSON, YAML, TOML, CSV, and Table formats seamlessly.

```bash
dataforge convert <file> --to FORMAT [--output FILE] [--indent N]
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `file` | Path to the input file |
| `-t, --to` | Target format: `json`, `yaml`, `toml`, `csv`, `table` |
| `-o, --output` | Path to the output file (defaults to stdout) |
| `--indent` | Number of spaces for indentation (default: 2) |

**Examples:**

```bash
# JSON to YAML
dataforge convert data.json --to yaml --output data.yaml

# JSON to CSV
dataforge convert data.json --to csv --output data.csv

# JSON to TOML
dataforge convert config.json --to toml --output config.toml

# Display as table
dataforge convert users.json --to table
```

---

#### `merge` -- Deep Merge

Recursively merge multiple data files with configurable strategies and conflict resolution.

```bash
dataforge merge <file1> <file2> [file3 ...] [--strategy STRATEGY] [--conflict STRATEGY] [--output FILE] [--dry-run]
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `files` | File paths to merge (minimum 2) |
| `-s, --strategy` | Array merge strategy: `replace` (default), `append`, `prepend`, `merge-by-key` |
| `-c, --conflict` | Conflict resolution: `theirs` (default), `ours`, `manual`, `error` |
| `-o, --output` | Path to the output file |
| `--dry-run` | Preview merge results without writing |

**Examples:**

```bash
# Basic merge (default replace strategy)
dataforge merge base.json override.json --output merged.json

# Append array merge
dataforge merge base.json update.json --strategy append --output merged.json

# Merge arrays by key
dataforge merge users1.json users2.json --strategy merge-by-key --output merged.json

# Preview merge results
dataforge merge a.json b.json --dry-run

# Keep original values on conflict
dataforge merge a.json b.json --conflict ours --output merged.json
```

---

#### `diff` -- Compare Differences

Recursively compare two data files and generate a detailed diff report.

```bash
dataforge diff <file1> <file2> [--ignore PATH] [--format FORMAT] [--output FILE]
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `file1` | Path to the old file |
| `file2` | Path to the new file |
| `-i, --ignore` | Path patterns to ignore (supports wildcards `*`) |
| `-f, --format` | Output format: `colorized` (default), `text`, `patch`, `summary` |
| `-o, --output` | Path to the output file |

**Examples:**

```bash
# Colorized diff
dataforge diff old.json new.json --format colorized

# JSON Patch format output (RFC 6902)
dataforge diff old.json new.json --format patch

# Diff summary
dataforge diff old.json new.json --format summary

# Ignore specific paths
dataforge diff old.json new.json --ignore "timestamp" --ignore "metadata.*"
```

---

#### `validate` -- Schema Validation

Validate data files against a JSON Schema.

```bash
dataforge validate <file> [--schema FILE] [--report FILE]
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `file` | Path to the data file |
| `-s, --schema` | Path to the schema file (performs basic type check if omitted) |
| `--report` | Generate a validation report to the specified file |

**Examples:**

```bash
# Validate with a schema file
dataforge validate data.json --schema schema.json

# Generate a validation report
dataforge validate config.json --schema config-schema.json --report report.txt

# Basic type check (no schema)
dataforge validate data.json
```

---

#### `template` -- Template Rendering

Render template files with data, supporting variables, loops, conditionals, and filters.

```bash
dataforge template <template> --data <file> [--output FILE] [--var key=value]
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `template` | Path to the template file or a template string |
| `-d, --data` | Path to the data file |
| `-o, --output` | Path to the output file |
| `-v, --var` | Extra variables (format: `key=value`) |

**Template Syntax:**

```django
{# Comment #}
{{ variable }}              {# Variable substitution #}
{{ user.name }}             {# Dot notation access #}
{{ name | upper }}          {# Filter #}
{{ price | round:2 }}       {# Filter with arguments #}
{{ items | join:", " }}     {# List join #}

{% for item in items %}     {# Loop #}
  - {{ item }}
{% endfor %}

{% if status == "active" %} {# Conditional #}
  Active
{% elif status == "pending" %}
  Pending
{% else %}
  Unknown
{% endif %}

{% include "header.txt" %}  {# File include #}
```

**Examples:**

```bash
# Render with a template file
dataforge template report.tpl --data data.json --output report.txt

# Inline template
dataforge template "Hello, {{ name }}!" --data user.json

# Pass extra variables
dataforge template tpl.txt --data data.json --var title="Monthly Report" --var date="2024-01"
```

---

#### `format` -- Format Data

Beautify and format JSON/YAML data.

```bash
dataforge format <file> [--indent N] [--sort-keys] [--minify] [--output FORMAT] [--output FILE]
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `file` | Path to the data file |
| `--indent` | Number of spaces for indentation (default: 2) |
| `--sort-keys` | Sort keys alphabetically |
| `--minify` | Minify output (remove whitespace) |
| `--output-format` | Output format: `json` (default), `yaml`, `table`, `tree` |
| `-o, --output` | Path to the output file |

**Examples:**

```bash
# Beautify JSON
dataforge format data.json --indent 4

# Sort keys
dataforge format data.json --sort-keys

# Minify JSON
dataforge format data.json --minify

# Display as tree
dataforge format data.json --output-format tree
```

---

#### `flatten` / `unflatten` -- Flatten & Unflatten

Flatten nested data into a single-level structure, or restore it back.

```bash
# Flatten nested data
dataforge flatten <file> [--separator SEP] [--output FILE]

# Unflatten data
dataforge unflatten <file> [--separator SEP] [--output FILE]
```

**Examples:**

```bash
# Flatten nested data
dataforge flatten data.json --separator "."
# {"a": {"b": {"c": 1}}} -> {"a.b.c": 1}

# Unflatten data
dataforge unflatten flat.json --separator "."
# {"a.b.c": 1} -> {"a": {"b": {"c": 1}}}
```

---

#### `stats` -- Data Statistics

Quickly get structural statistics about a data file.

```bash
dataforge stats <file>
```

**Examples:**

```bash
dataforge stats data.json
# Output: data type, key count, nesting depth, value type distribution, etc.
```

---

#### `server` -- HTTP API Server

Start the built-in HTTP server to expose data operations as REST API endpoints.

```bash
dataforge server [--port PORT] [--host HOST]
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `-p, --port` | Port number (default: 8080) |
| `--host` | Bind address (default: 127.0.0.1) |

**API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/help` | GET | Help information |
| `/query` | POST | Query data |
| `/convert` | POST | Format conversion |
| `/validate` | POST | Data validation |

**Examples:**

```bash
# Start the server
dataforge server --port 8080

# Call the API
curl -X POST http://127.0.0.1:8080/query \
  -H "Content-Type: application/json" \
  -d '{"data": {"users": [{"name": "Alice"}]}, "expression": "users[0].name"}'
```

---

#### `tui` -- TUI Interactive Dashboard

Launch an interactive data browsing dashboard in the terminal.

```bash
dataforge tui [--directory DIR]
```

**Examples:**

```bash
# Launch the TUI dashboard
dataforge tui

# Specify initial browse directory
dataforge tui --directory ./configs
```

---

### 💡 Design Philosophy & Roadmap

#### Design Philosophy

The core design philosophy of DataForge-CLI is **"Simplicity First"**:

1. **Zero-dependency philosophy**: Built entirely with the Python standard library to eliminate dependency hell. Install and use in any Python environment -- ideal for CI/CD pipelines and containerized deployments.
2. **Unix philosophy**: Each command does one thing well. Combine commands through pipes for complex workflows. Output defaults to stdout for seamless integration with other tools.
3. **Custom core engines**: All five engines (query, merge, diff, template, validator) are built from scratch without relying on `jmespath`, `jsonpatch`, or other third-party libraries, ensuring full control and lightweight operation.

#### Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Pure Python standard library | Eliminates dependency conflicts, reduces install failures, improves startup speed |
| argparse | Built into the standard library, zero-dependency CLI argument parsing |
| Custom query engine | Avoids the `jmespath` dependency while providing more flexible extension capabilities |
| Custom template engine | Jinja2 is too heavyweight; our engine covers 80% of common use cases with zero dependencies |
| ANSI color output | Natively supported by terminals, no extra libraries needed for colorized diff highlighting |

#### Roadmap

- [ ] **Streaming support**: Stream-based reading and incremental processing for large files, breaking through memory limits
- [ ] **Plugin system**: Support for custom commands and filter plugins
- [ ] **Shell completions**: Auto-completion scripts for Bash/Zsh/Fish
- [ ] **Configuration file**: Support for `~/.dataforgerc` global configuration
- [ ] **Performance optimization**: Lazy evaluation and caching for large file scenarios
- [ ] **More formats**: Support for XML, INI, Properties, and other formats
- [ ] **Watch mode**: Monitor file changes and automatically execute operations

---

### 📦 Installation & Deployment

#### Install from Source

```bash
# Clone the repository
git clone https://github.com/gitstq/DataForge-CLI.git
cd DataForge-CLI

# Install
pip install .

# Or install in development (editable) mode
pip install -e .
```

#### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run a single test file
pytest tests/test_query.py -v

# Run a specific test
pytest tests/test_query.py::TestQueryEngine::test_dot_access -v
```

#### System Requirements

| Item | Requirement |
|------|-------------|
| Python | >= 3.8 |
| Operating System | Linux / macOS / Windows |
| Dependencies | None (pure standard library) |

---

### 🤝 Contributing Guide

We welcome and appreciate contributions of all kinds -- bug reports, feature suggestions, or code pull requests.

#### Filing Issues

- Use a **clear, descriptive title**
- Provide a **minimal reproducible example**
- Include **environment details** (Python version, OS)
- Attach **error log screenshots** when applicable

#### Submitting Pull Requests

1. **Fork** this repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Write your code** and ensure all tests pass (`pytest`)
4. **Commit your changes** (`git commit -m 'feat: add amazing feature'`)
5. **Push to remote** (`git push origin feature/amazing-feature`)
6. Open a **Pull Request**

#### Commit Convention

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat:     New feature
fix:      Bug fix
docs:     Documentation update
style:    Code formatting
refactor: Code refactoring
test:     Test-related changes
chore:    Build/tooling changes
```

---

### 📄 License

This project is licensed under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2024 DataForge Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
