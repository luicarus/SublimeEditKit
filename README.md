# SublimeEditKit

面向 Sublime Text 的小工具集合，解决日常文本编辑中的具体问题。各工具独立维护，可单独安装；使用方法、配置和兼容性见对应文档。

## 工具列表

| 工具 | 用途 | 版本要求 |
| --- | --- | --- |
| [SmartSoftWrap](SmartSoftWrap/README.md) | 改善纯文本中英文混排的软换行，支持英文单词内折行或保留单词完整，折行不改变文本内容 | Sublime Text 4 Build 4213+ |

## 快速开始

目前提供的工具为 SmartSoftWrap。安装后，普通纯文本会自动按窗口宽度折行，默认允许英文从单词中间折行。

1. 下载或克隆本仓库。
2. 在 Sublime Text 中通过 `Preferences → Browse Packages…` 打开 Packages 目录。
3. 将项目中的 [`SmartSoftWrap/package/SmartSoftWrap`](SmartSoftWrap/package/SmartSoftWrap) 文件夹完整复制到 Packages 目录，包含 `.python-version`，保留文件夹名称 `SmartSoftWrap`。
4. 打开一个使用内置 **Plain Text** 语法的 `.txt` 文件，或打开[演示文本](SmartSoftWrap/examples/wrap-demo.txt)，缩窄窗口查看效果。
5. 打开命令面板，搜索 `SmartSoftWrap`，切换折行模式或恢复当前视图的原始设置。

命令面板快捷键：Windows / Linux 为 `Ctrl+Shift+P`，macOS 为 `Cmd+Shift+P`。

也可以使用 [SmartSoftWrap.sublime-package 安装包](SmartSoftWrap/dist/SmartSoftWrap.sublime-package)。两种安装方式任选一种，具体步骤见 [SmartSoftWrap 安装说明](SmartSoftWrap/README.md#安装)。日常使用不需要额外安装 Python。

## 目录结构

```text
SublimeEditKit/
├── README.md
├── LICENSE
└── SmartSoftWrap/
    ├── README.md                # 工具说明
    ├── package/SmartSoftWrap/    # Sublime 插件源码
    ├── examples/                # 演示文本
    ├── tests/                   # Sublime Text 集成验证脚本
    ├── dist/                    # 安装包和已有验证报告
    └── build_package.py         # 打包脚本
```

## 开发与验证

需要系统 Python 3.9 或更新版本。在项目根目录执行以下命令，生成 SmartSoftWrap 安装包：

```sh
python SmartSoftWrap/build_package.py
```

真实编辑器验证的运行方法和已有结果见 [SmartSoftWrap 开发与验证](SmartSoftWrap/README.md#开发与验证)。

## 反馈与贡献

欢迎通过 GitHub Issues 报告问题、提出使用场景，或通过 Pull Requests 提交改进。报告问题时，请附上操作系统、Sublime Text Build 号、复现步骤和简短示例文本；工具特有的信息见对应文档。

## 许可证

本项目采用 [MIT License](LICENSE)。
