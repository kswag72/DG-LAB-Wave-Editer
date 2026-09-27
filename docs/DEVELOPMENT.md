# DG-LAB-Wave-Editer 二次开发手册

这份文档面向希望对 DG-LAB-Wave-Editer 进行功能扩展或二次开发的开发者。项目采用了 Service/Repository 分层架构，确保了业务逻辑与 UI 显示的彻底解耦。

运行入口、工作范围和已核实问题见 [AGENTS.md](../AGENTS.md)。本文的扩展示例仅供参考，不代表待实施计划。

## 1. 项目概览

DG-LAB-Wave-Editer 是一款专为 DG-Lab Coyote 电击控制器设计的波形可视化编辑器。它允许用户通过数学函数生成、手动绘制以及拼接复杂的波形序列。

- 技术栈：Python 3.10+, PyQt6, JSON5
- 核心功能：波形函数生成、可视化画布编辑、素材库管理、序列拼接与导出、Raw/V3 格式双向转换
- 开源地址：https://github.com/kswag72/DG-LAB-Wave-Editer

## 2. 项目结构

项目代码组织遵循职责分离原则，所有核心逻辑位于 `src/` 目录下。

```
├── pyproject.toml                       # Ruff 插件与 lint 配置
├── README.md
├── LICENSE
├── configs/
│   ├── DG-LAB-Wave-Editer.spec             # PyInstaller 打包配置文件
│   └── requirements.txt                 # 项目依赖 (PyQt6>=6.10.0)
├── docs/
│   └── DEVELOPMENT.md                   # 本开发手册
├── tests/                              # 编辑/保存回归；legacy/ 保留早期独立转换实现
├── src/
│   ├── __init__.py
│   ├── __main__.py                      # 程序入口，支持 python -m src 启动
│   ├── main.py                          # QApplication 实例化与全局资源加载
│   ├── IOC.ico                          # 程序图标
│   ├── fonts/                           # 字体目录 (需放置 Maple Mono NF CN)
│   ├── domain/
│   │   ├── __init__.py
│   │   └── models.py                    # 领域模型 (Wave, WaveItem, SequenceEntry, MAX_STEPS)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── id_service.py                # ID 生成服务
│   │   ├── wave_service.py              # 波形数学计算、平滑处理
│   │   ├── sequence_service.py          # 序列拼接、数据转换与导出逻辑
│   │   └── conversion_service.py        # raw 字符串与 expectedV3 格式双向转换
│   ├── repositories/
│   |   ├── __init__.py
│   │   ├── json5_library_repository.py  # 波形库持久化 (JSON5 格式)
│   │   └── json5_pulse_repository.py    # 导出文件持久化
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py               # 主窗口：组装 DI、信号路由
│       ├── wave_canvas.py               # 自定义 QWidget 绘图控件 (多图表类型 + 段落标签)
│       ├── range_slider.py              # 自定义双端范围选择滑条
│       ├── styles.py                    # 全局 QSS 样式表定义
│       └── panels/
│           ├── __init__.py
│           ├── library_panel.py         # 素材库 UI 面板 (可编辑波形名称, Raw 批量选择)
│           ├── canvas_panel.py          # 画布操作 UI 面板 (图表类型切换)
│           ├── func_panel.py            # 函数生成器 UI 面板 (QGroupBox 布局)
│           ├── raw_panel.py             # Raw 字符串导入/导出面板 (支持批量导出)
│           └── sequence_panel.py        # 序列拼接 UI 面板
```

## 3. 架构设计

项目采用典型的三层架构，通过依赖注入（DI）在主窗口中完成组装。

### Domain 层 (src/domain/models.py)
定义了项目的基础数据结构。使用 `frozen dataclass` 保证数据的不可变性，便于在不同面板间传递。
- `Wave`: 核心波形模型，包含 `intervals` (时长) 和 `intensities` (强度) 两个元组。
- `WaveItem`: 包装 Wave 的条目，用于序列显示。
- `GapItem`: 包装静默时长（毫秒）的条目。
- `SequenceEntry`: `WaveItem | GapItem` 的联合类型。
- `MAX_STEPS = 1000`: 当前画布和 `Wave.validate()` 的帧数上限。载入前先验证，超限则提示并保留当前编辑内容；仓库读取和序列拼接保留原长度，不静默截断。

### Service 层
处理纯业务逻辑，不涉及任何 UI 控件。
- `IdService`: 将 32 bit 随机整数转为十六进制字符串（最多 8 个字符），当前没有碰撞检测。
- `WaveService`: 包含正弦、方波、锯齿、三角、幂、多项式、指数、对数、指数衰减、S形等 10 种内置数学函数。它还负责波形的平滑、钳位（Clamp）处理。
- `SequenceService`: 负责将多个 `WaveItem` 和 `GapItem` 合并为单个 `Wave`，并将其转化为 DG-Lab 协议所需的十六进制字符串。
- `ConversionService`: 负责 `Dungeonlab+pulse:` 字符串与 V3 十六进制帧数组之间的转换。`raw_to_v3` 和 `v3_to_raw` 均为实例方法；反向转换有损。

### Repository 层
处理数据的持久化与反序列化。
- `Json5LibraryRepository`: 负责波形库文件的读取与保存。当前通过正则预处理后调用标准库 `json`，只覆盖部分 JSON5 语法；缺失 ID 时生成 ID，没有 ID 校验。
- `Json5PulseRepository`: 负责最终导出文件的写入。

### UI 层与依赖注入
UI 面板（Panels）只负责处理用户交互信号。所有的逻辑请求都通过信号（Signal）发送给 `MainWindow`。

**数据流示意图：**
```
[LibraryPanel] --load_wave(Wave)--> [CanvasPanel]
[CanvasPanel] --save_wave(Wave)--> [LibraryPanel]
[CanvasPanel] --steps_changed(int)--> [FuncPanel]
[FuncPanel] --wave_generated(list,int,int,int)--> [CanvasPanel]
[FuncPanel] --smooth_requested()--> [CanvasPanel]
[LibraryPanel] --add_wave_to_seq(Wave)--> [SequencePanel]
[SequencePanel] --save_to_lib(Wave)--> [LibraryPanel]
[RawPanel] --import_wave(Wave)--> [CanvasPanel] + [LibraryPanel]
[LibraryPanel] --raw_selection_changed(list[Wave])--> [RawPanel]
```

画布的 `save_wave` 连接 `LibraryPanel.save_wave`：更新已加载条目、保留 ID；新建或另存副本追加条目。保存目标按实际载入的素材跟踪，重复导入相同 ID 时也只更新当前条目。保存后刷新 Raw 选择数据，并清除旧转换文本。素材库保存仍在内存中，导出素材库才写文件。

主窗口使用水平 `QSplitter` 组织素材侧栏与编辑区。画布保持完整高度，下方四个工具页分别用 `QScrollArea` 包装 `CanvasPanel.edit_tools`、函数、序列和 Raw 面板，窄窗口中允许滚动。工具页切换同步当前选区；缩放和定位只更新视图。`FrameSpinBox` 对外显示 1–1000，信号和内部值仍使用 0 起算索引。

`CanvasPanel.is_dirty` 比较当前有效帧及名称与上次载入/保存的快照；`LibraryPanel.is_modified` 单独记录素材库是否尚未导出。主窗口在切换、新建与关闭时处理未保存编辑，在关闭时处理未导出的素材库；取消文件对话框不会清除修改状态。

画布长度变化同步精确编辑、批量范围和函数范围；原来全选时扩展为新的全选范围，局部选区则保留并限制在有效帧内。载入另一条素材会重置尾部缓冲，避免扩展长度时混入旧数据。

**注入流程：**
在 `MainWindow.__init__` 中，按顺序实例化服务。先创建 `IdService`，再将其注入到 `WaveService`，最后将所有服务与仓库注入到各个 UI 面板的构造函数中。

```python
# MainWindow.__init__ 中的依赖注入顺序
id_service = IdService()
wave_service = WaveService(id_service)
sequence_service = SequenceService(id_service, wave_service)
library_repository = Json5LibraryRepository(id_service)
pulse_repository = Json5PulseRepository()

self.library = LibraryPanel(library_repository)
self.canvas_panel = CanvasPanel(wave_service)
self.func_panel = FuncPanel(wave_service)
self.seq_panel = SequencePanel(sequence_service, pulse_repository)
self.raw_panel = RawPanel(conversion_service, wave_service)
```

## 4. 开发环境搭建

1. 克隆代码库：
   ```bash
   git clone https://github.com/kswag72/DG-LAB-Wave-Editer.git
   cd DG-LAB-Wave-Editer
   ```
2. 创建并激活虚拟环境：
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
   ```
3. 安装依赖：
   ```bash
   pip install -r configs/requirements.txt
   ```
4. 下载字体文件：
   前往 [Maple Font Releases](https://github.com/subframe7536/maple-font/releases) 下载 **MapleMono-NF-CN-unhinted** 压缩包，解压后将 `MapleMono-NF-CN-ExtraBold.ttf` 放入 `src/fonts/` 目录。缺少字体时程序仍可运行，回退到系统默认字体。
5. 启动开发版：
   ```bash
   python -m src
   ```
6. 构建 exe 命令：
   ```bash
   pip install pyinstaller
   python -m PyInstaller configs/DG-LAB-Wave-Editer.spec --clean
   ```
   产出：`dist/DG-LAB-Wave-Editer.exe`，单文件可分发。

   现有 spec 将字体列为必需资源；缺少字体时可运行源码，但不能直接按此配置打包。历史校验脚本的运行方式及限制见 [README](../README.md#历史校验脚本)。

   Windows spec 将当前构建进程的 DLL 搜索 PATH 限定为 Qt、Python 与 Windows 系统目录，避免从其他工具的 PATH 收集同名 ICU / C 运行库，导致生成的 exe 无法加载 Qt。修改打包规则后应使用 `--clean` 或新的 `--workpath`，并实际启动生成的 exe 检查加载日志。

## 5. 代码规范

项目使用 Ruff 进行静态代码检查。

- **导入规范**：严禁使用相对导入。所有导入必须从 `src` 开始。
  - 正确：`from src.domain.models import Wave`
  - 错误：`from ..domain.models import Wave`
- **类型标注**：所有函数签名必须包含参数和返回值的类型标注（Type Hints）。
- **可读性**：代码中不应出现解释性的注释。应通过精确的变量命名、细粒度的函数拆解来让代码自解释。
- **Lint 设置**：
  - `ANN`: 强制检查类型标注。
  - `RET`: 检查 return 语句。
  - `I`: 自动排序 import。
  - 行宽限制：120 字符。

运行检查：
```bash
ruff check src/
ruff format src/
```

## 6. 二次开发指南：常见场景

### 6.1 新增波形函数
假设要增加一个"随机噪声"函数：

1. 在 `src/services/wave_service.py` 的 `_compute_wave_value` 方法中添加分支：
```python
# 第一步：在 src/services/wave_service.py 的 _compute_wave_value 末尾添加分支
# 当前最后一个分支是 wave_type == 9 (S形曲线)，新增 wave_type == 10
if wave_type == 10:
    return random.uniform(0, amplitude) * coeff + offset

# 第二步：在文件顶部确保已导入 random
import random
```

2. 在 `src/ui/panels/func_panel.py` 的下拉框初始化代码中加入名称：
```python
# 在 src/ui/panels/func_panel.py 的 _build_target_and_function_row 方法中
# 在 addItems 列表末尾追加 "噪声"
self.function_combo.addItems(
    ["正弦波", "方波", "锯齿波", "三角波", "幂函数", "多项式", "指数函数", "对数函数", "指数衰减", "S形曲线", "噪声"]
)
```

### 6.2 新增领域模型
如果需要支持"波形标签"功能：

1. 在 `src/domain/models.py` 中新增：
```python
# 在 src/domain/models.py 中新增
@dataclass(frozen=True, slots=True)
class WaveTag:
    key: str
    color: str

# 如果需要将 WaveTag 与 Wave 关联，可新建一个扩展模型
@dataclass(frozen=True, slots=True)
class TaggedWave:
    wave: Wave
    tags: tuple[WaveTag, ...]
```

2. 补充说明：如果新模型需要参与序列拼接，需要将其添加到 `SequenceEntry` 联合类型中，并在 `SequenceService` 中添加对应的 `isinstance` 分支。

### 6.3 新增 Repository
如果想把波形保存到 SQLite 数据库而不是 JSON5 文件：

1. 在 `src/repositories/` 下新建 `sqlite_library_repository.py`：
```python
# src/repositories/sqlite_library_repository.py
from __future__ import annotations

import sqlite3
from collections.abc import Sequence

from src.domain.models import Wave
from src.services.id_service import IdService


class SqliteLibraryRepository:
    def __init__(self, id_service: IdService, db_path: str = "library.db") -> None:
        self._ids = id_service
        self._db_path = db_path

    def load(self) -> list[Wave]:
        conn = sqlite3.connect(self._db_path)
        cursor = conn.execute("SELECT id, name, intervals, intensities FROM waves")
        waves: list[Wave] = []
        for row in cursor:
            intervals = tuple(int(x) for x in row[2].split(","))
            intensities = tuple(int(x) for x in row[3].split(","))
            waves.append(Wave(id=row[0], name=row[1], intervals=intervals, intensities=intensities))
        conn.close()
        return waves

    def save(self, waves: Sequence[Wave]) -> None:
        conn = sqlite3.connect(self._db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS waves (id TEXT PRIMARY KEY, name TEXT, intervals TEXT, intensities TEXT)")
        conn.execute("DELETE FROM waves")
        for wave in waves:
            conn.execute(
                "INSERT INTO waves VALUES (?, ?, ?, ?)",
                (wave.id, wave.name, ",".join(str(v) for v in wave.intervals), ",".join(str(v) for v in wave.intensities)),
            )
        conn.commit()
        conn.close()
```

2. 在 `MainWindow.__init__` 中替换：
```python
# 将
library_repository = Json5LibraryRepository(id_service)
# 替换为
library_repository = SqliteLibraryRepository(id_service, db_path="my_library.db")
```

### 6.4 新增 UI 面板
新增一个用于实时预览的面板：

1. 在 `src/ui/panels/` 创建 `preview_panel.py`：
```python
# src/ui/panels/preview_panel.py
from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.domain.models import Wave


class PreviewPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._info_label = QLabel("尚未加载波形")
        layout.addWidget(self._info_label)

    def update_preview(self, wave: Wave) -> None:
        text = f"名称: {wave.name} | 步数: {wave.steps} | 首步间隔: {wave.intervals[0]}"
        self._info_label.setText(text)
```

2. 在 `MainWindow` 中注册：
```python
# main_window.py — __init__ 中
from src.ui.panels.preview_panel import PreviewPanel

self.preview = PreviewPanel()

# _assemble_layout 中
mid.addWidget(self.preview)

# _connect_signals 中
self.canvas_panel.save_wave.connect(self.preview.update_preview)
```

### 6.5 修改 pulse 导出格式
DG-Lab 的十六进制格式遵循以下逻辑：
- 每步对应 16 个字符。
- 前 8 字符是 interval（间隔时长），将时长转为 2 位 hex 并重复 4 次。
- 后 8 字符是 intensity（强度），将强度转为 2 位 hex 并重复 4 次。

如果要修改导出逻辑，请编辑 `src/services/sequence_service.py` 中的 `build_pulse_lines` 函数。

### 6.6 修改主题样式
编辑 `src/ui/styles.py` 中的 `MAIN_STYLESHEET` 字符串。项目保留原粉蓝配色，使用圆角卡片和按钮：
- 窗口背景：`#3a4149`，面板背景：`#414955`
- 输入控件背景：`#2e3740`
- 普通操作与选中页签（浅蓝）：`#cbf1f5`
- 主要操作与强度图例（浅粉）：`#ffe2e2`
- 间隔图例与 Raw 选中状态（黄色）：`#ffde7d`

标题旁的小爱心由 `src/ui/brand_badge.py` 使用 QPainter 绘制，不依赖字体字符或外部图片。

### 6.7 Raw/V3 格式转换
`ConversionService` 提供 raw 字符串与 expectedV3 格式之间的双向转换，位于 `src/services/conversion_service.py`。
- `parse_raw` 支持带 `全局设置=分段数据` 和仅含分段数据的两种输入；后者默认 `sleep_time=0`、`speed_factor=1`，不会把第一段参数误当作全局设置。`Dungeonlab+pulse:` 前缀可省略。
- `raw_to_v3(raw_str: str) -> list[str]`：将 `Dungeonlab+pulse:` 字符串转换为 V3 帧数组，每帧 16 个十六进制字符。
- `v3_to_raw(frames: list[str]) -> str`：将 V3 帧数组转换为单段 raw 字符串，会平均频率、去掉末尾零强度帧，不能承诺无损往返。

**时长精度修正**：`_config_to_v3` 中对 `section_time` 转循环数的计算使用了 `math.ceil(... - 1e-9)` 修正浮点误差，避免整除场景下多算一个循环。这不等于所有转换样例或往返场景都已通过。

**批量导出**：`RawPanel` 支持接收 `LibraryPanel` 通过 `raw_selection_changed` 信号传递的多个波形，点击导出按钮后一次性生成所有选中波形的 raw 字符串。素材卡片中的 Raw 按钮用于切换选中状态。

如需扩展新的转换格式，在 `ConversionService` 中添加对应的静态方法即可。

### 6.8 画布图表类型
`WaveCanvas` 支持四种图表显示类型，通过 `chart_type` 属性切换：
- `0` — 折线图（默认）
- `1` — 面积图
- `2` — 散点图
- `3` — 阶梯图

如需新增图表类型，在 `wave_canvas.py` 的 `_draw_plot` 方法中添加新的 `elif` 分支，并在 `canvas_panel.py` 的图表类型下拉框中添加对应选项。

## 7. DG-Lab Pulse 数据格式参考

`pulse.json5` 是一个包含波形对象的数组。

```json5
[
  {
    id: 'a1b2c3d4',            // 字符串标识，导入时保留
    name: '示例波形',
    pulseData: [
      '0A0A0A0A64646464',   // 第1步：interval=10(0A), intensity=100(64)
      '1414141432323232',   // 第2步：interval=20(14), intensity=50(32)
    ]
  }
]
```

当前素材库解析只读取前 2 字符作为 `interval`、第 9/10 字符作为 `intensity`；输出时分别重复 4 次。因此四组子采样不同的帧不能保证无损。这里的字节值也没有像 `ConversionService` 一样解码为 10–1000 的间隔值。素材库和序列导出仍直接使用 `hex(interval)`；间隔超过 255 时会生成超过 16 字符的帧。这些是现有实现差异，不应当作协议规范。

## 8. 提交规范

请遵循 Conventional Commits 规范，这有助于自动化生成变更日志。

格式：`<type>(<scope>): <description>`

常见 type：
- `feat`: 新功能
- `fix`: 修复错误
- `refactor`: 代码重构（不改变功能）
- `cleanup`: 仅清理代码、格式化、删除冗余

示例：
- `refactor(ui): decouple panels from business logic`
- `feat(services): add exponential decay function to wave service`
- `fix(repositories): resolve id collision in library repository`
