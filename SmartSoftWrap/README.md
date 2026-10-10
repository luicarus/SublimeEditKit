# SmartSoftWrap

Sublime Text 纯文本软换行插件，用于改善中英文混排时连续文本提前移到下一行、留下较大行尾空白的情况。

默认允许中文和英文按字符边界折行，也可切换为保留英文单词完整的模式。窗口宽度变化时，由编辑器自动重新排版。

**软换行只影响显示，插件不插入换行、空格或零宽字符，也不改写文本内容。**

[返回工具列表](../README.md)

## 功能

- 默认允许中文和英文从字符边界折行。
- 提供保留英文单词完整的可选模式。
- 自动启用使用内置 Plain Text 语法的视图，包括普通 `.txt` 文件和新建的纯文本标签页。
- 提供恢复命令，恢复当前视图原来的语法和换行设置。
- 保留组合音标、常见 emoji 肤色修饰符、ZWJ 序列和国旗字符组合。

## 兼容性

- 要求 **Sublime Text 4 Build 4213 或更新版本**，使用编辑器内置的 Python 3.14 插件运行环境。
- 日常使用不需要额外安装系统 Python 或第三方依赖。
- 项目中已有的集成验证报告：Windows、Sublime Text Build 4215，11 项检查全部通过。
- macOS 和 Linux 尚未进行实机验证。

## 安装

以下两种方式任选一种，避免同时安装两份插件。

### 方式一：复制插件文件夹

1. 下载或克隆 SublimeEditKit 仓库。
2. 在 Sublime Text 中通过 `Preferences → Browse Packages…` 打开 Packages 目录。
3. 将本工具的 [`package/SmartSoftWrap`](package/SmartSoftWrap) 文件夹完整复制到 Packages 目录，包含隐藏文件 `.python-version`。
4. 保持目录名称为 **`SmartSoftWrap`**。复制完成后，插件会自动加载。

安装后的目录应为：

```text
Packages/
└── SmartSoftWrap/
    ├── .python-version
    ├── LICENSE
    ├── soft_wrap.py
    ├── SmartSoftWrap.sublime-settings
    ├── Default.sublime-commands
    ├── Soft Wrap Characters.sublime-syntax
    └── Soft Wrap Words.sublime-syntax
```

注意复制 `package` 内的插件文件夹，而不是整个工具目录。

### 方式二：使用安装包

1. 从仓库下载 [`dist/SmartSoftWrap.sublime-package`](dist/SmartSoftWrap.sublime-package)。在 GitHub 文件页面下载原始文件，避免保存成网页；如需自行打包，见[生成安装包](#生成安装包)。
2. 通过 `Browse Packages…` 打开 Packages 目录，然后进入其上一级目录。
3. 将安装包放入同级的 `Installed Packages` 目录；如果该目录不存在，可先创建。

安装包名称保持为 **`SmartSoftWrap.sublime-package`**。

## 使用

安装后，打开一个使用内置 **Plain Text** 语法的 `.txt` 文件并调整窗口宽度，即可查看折行效果。插件加载时也会处理已经打开的普通纯文本视图。

打开命令面板，输入 **`SmartSoftWrap`**：Windows / Linux 使用 `Ctrl+Shift+P`，macOS 使用 `Cmd+Shift+P`。

以下命令均带有 `SmartSoftWrap:` 前缀：

| 命令 | 效果 |
| --- | --- |
| `Soft Wrap - Allow English Word Splitting` | 中文逐字折行，英文也可从单词中间折行；默认模式 |
| `Soft Wrap - Preserve English Words` | 中文逐字折行，将连续 ASCII 英文字母、数字和下划线视为一个词 |
| `Soft Wrap - Restore Original` | 当前视图恢复原来的语法、换行开关和换行宽度 |

停用后，切换回该标签页不会重新启用；可以通过前两个命令手动启用。新打开的纯文本视图仍会自动启用。

可打开 [`examples/wrap-demo.txt`](examples/wrap-demo.txt)，缩窄窗口并切换两种折行模式，比较中英文混排的显示效果。

### 没有自动生效时

检查文件使用的语法是否为内置 **Plain Text**。文件扩展名为 `.txt` 并不代表它一定使用该语法，可通过右下角的语法菜单确认。

自动启用和手动启用都只适用于内置 Plain Text 或本插件的语法；代码、Markdown 和其他自定义语法不会被替换。关闭自动启用后，仍可在普通纯文本视图中通过命令面板选择折行模式。

如果命令面板中没有 `SmartSoftWrap` 命令，请核对编辑器版本以及上述安装目录结构。

## 配置

默认配置为：

```json
{
    "auto_enable": true,
    "default_mode": "characters"
}
```

通过 `Preferences → Browse Packages…` 打开 Packages 目录，在 `User` 子目录创建或编辑 `SmartSoftWrap.sublime-settings`，写入需要覆盖的配置。建议将个人配置放在 User 目录，便于更新插件。

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `auto_enable` | `true` | 是否自动启用普通纯文本视图 |
| `default_mode` | `"characters"` | 自动启用且尚未选择模式的视图使用此默认值；`"characters"` 允许英文中间折行，`"words"` 保留英文单词 |

例如，自动启用时默认保留英文单词：

```json
{
    "default_mode": "words"
}
```

设置 `"auto_enable": false` 可以关闭自动启用，随后通过命令面板手动启用需要处理的视图。该设置不会停用已经启用的视图，已有视图可以使用 `Restore Original` 命令停用。

配置在插件加载以及新建、打开或激活普通纯文本视图时读取。修改 `default_mode` 不会切换已经启用的视图；如需切换，请使用命令面板。执行过 `Restore Original` 的视图也不会因修改配置而自动重新启用。

### 折行宽度

插件启用或切换模式时使用窗口宽度（`word_wrap: true`、`wrap_width: 0`）。如需临时使用固定列宽，可通过 `View → Word Wrap Column` 调整。自动启用开启时，重新激活该视图会回到窗口宽度；关闭自动启用后，重新激活不会重置列宽。

### 纯文本显示偏好

插件的两种模式使用独立的语法名称。如果原来的字体、字号等偏好仅配置在 `Plain text.sublime-settings` 中，可以在 User 目录下将它们分别配置到：

- `Soft Wrap Characters.sublime-settings`
- `Soft Wrap Words.sublime-settings`

通用 Preferences 设置仍然生效。

## 更新与卸载

更新时，用新版本替换原来安装的插件文件夹或 `.sublime-package` 文件，保持安装方式一致。

卸载前，可对需要恢复的视图执行 `Restore Original`；然后删除 Packages 中的 `SmartSoftWrap` 文件夹，或 Installed Packages 中的 `SmartSoftWrap.sublime-package`。插件退出时也会恢复它管理的视图。通用 Preferences 文件不会被修改。

## 原理与限制

原生折行优先采用空格和语法分词边界。无空格的中英文连续文本可能作为一个块提前移到下一行，留下空白。插件通过自定义纯文本语法提供更细的分词边界，排版仍由 Sublime 自己完成。

当前实现有以下限制：

- 保留常见组合音标、emoji 肤色修饰符、ZWJ 序列和成对的国旗字符，但没有实现完整 Unicode 字素分割。
- 没有实现中文排版禁则，逗号、句号等标点可能出现在行首；不提供两端对齐。
- 保留英文单词模式只将连续 ASCII 英文字母、数字和下划线视为一个词，不提供通用语言分词。
- 逐字符分词可能增加超大文本的布局开销。

## 开发与验证

以下命令在工具目录 `SmartSoftWrap` 中执行，需要系统 Python 3.9 或更新版本。

### 生成安装包

```sh
python build_package.py
```

输出为 `dist/SmartSoftWrap.sublime-package`，仅包含运行时文件。

### 运行真实编辑器验证

先安装插件并保持 Sublime Text 正在运行，再执行以下命令。Windows 安装路径仅为示例，请替换为自己的 Sublime Text 命令行程序路径：

```powershell
python tests/run_integration.py --sublime "C:/Program Files/Sublime Text/subl.exe"
```

便携版或非 Windows 环境还需传入 `--packages`，指定与当前运行的 Sublime 实例对应的 Packages 目录；`--sublime` 则指定该实例的命令行程序路径。例如，Windows 便携版可以使用：

```powershell
python tests/run_integration.py --sublime "C:/Tools/Sublime Text/subl.exe" --packages "C:/Tools/Sublime Text/Data/Packages"
```

可使用 `python tests/run_integration.py --help` 查看参数，包括自定义报告路径的 `--output`。

验证脚本会临时安装测试辅助包，在真实 Sublime 视图中检查断行位置、自动启用、模式恢复、语法隔离、常见组合字符，以及保存后字节不变（含 UTF-8 BOM 和 CRLF）。测试正常完成后关闭临时标签页、恢复原来活动标签，并删除临时文本文件；运行脚本退出时会清理测试辅助包。如果测试回调中断，可能残留测试标签页或临时文本文件。

验证报告默认写入 [`dist/integration-results.json`](dist/integration-results.json)。项目内已有报告记录了 Windows、Build 4215 上全部 **11 项**检查通过的结果；其他环境需自行运行验证。使用 `--output` 时，请指定专用报告路径，验证完成后会替换该路径下已有的报告。

## 反馈问题

提交 GitHub Issue 时，请提供：

- 操作系统和 Sublime Text Build 号（可在编辑器的 About 窗口中查看）。
- 安装方式、当前文件语法和使用的折行模式。
- 复现步骤、预期效果，以及能够复现问题的简短文本。

如问题与断行位置有关，请附上截图，便于比较实际显示和预期效果。

## 许可证

本工具采用 [MIT License](../LICENSE)。插件文件夹和 `.sublime-package` 安装包均包含许可证文件。
