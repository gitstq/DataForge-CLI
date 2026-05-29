"""
DataForge-CLI 安装配置
======================
纯Python零依赖的CLI工具安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dataforge-cli",
    version="1.0.0",
    description="轻量级终端JSON/YAML数据智能处理与转换引擎",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="DataForge Team",
    author_email="dataforge@example.com",
    url="https://github.com/dataforge/dataforge-cli",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    entry_points={
        "console_scripts": [
            "dataforge=dataforge_cli.cli:main",
        ],
    },
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.0"],
    },
)
