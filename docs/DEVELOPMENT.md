# DG-LAB-Wave-Editer 二次开发手册

这份文档面向希望对 DG-LAB-Wave-Editer 进行功能扩展或二次开发的开发者。项目采用了 Service/Repository 分层架构，确保了业务逻辑与 UI 显示的彻底解耦。

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
├── tests/                               # 单元测试目录
├── scripts/                             # 辅助脚本
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
- `MAX_STEPS = 100`: 限制单个波形的最大步数。

### Service 层
处理纯业务逻辑，不涉及任何 UI 控件。
- `IdService`: 负责生成 32 位随机十六进制 ID，确保每个波形在库中唯一。
- `WaveService`: 包含正弦、方波、锯齿、三角、幂、多项式、指数、对数、指数衰减、S形等 10 种内置数学函数。它还负责波形的平滑、钳位（Clamp）处理。
- `SequenceService`: 负责将多个 `WaveItem` 和 `GapItem` 合并为单个 `Wave`，并将其转化为 DG-Lab 协议所需的十六进制字符串。
- `ConversionService`: 负责 raw 字符串（十六进制脉冲数据）与 expectedV3 波形格式之间的双向转换。提供 `raw_to_v3` 和 `v3_to_raw` 两个静态方法。

### Repository 层
处理数据的持久化与反序列化。
- `Json5LibraryRepository`: 负责波形库文件的读取与保存。它将 `Wave` 对象转换为 JSON5 格式，并处理 ID 校验。
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
   python -m venv venv
   source venv/bin/activate  # Windows 使用 venv\Scripts\activate
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
编辑 `src/ui/styles.py` 中的 `MAIN_STYLESHEET` 字符串。项目采用暗色调方案：
- 背景：`#3a4149`
- 控件背景：`#2e3740`
- 主色调（青色）：`#cbf1f5`
- 强调色（粉色）：`#ffe2e2`
- 辅助色（黄色）：`#ffde7d`

### 6.7 Raw/V3 格式转换
`ConversionService` 提供 raw 字符串与 expectedV3 格式之间的双向转换，位于 `src/services/conversion_service.py`。
- `raw_to_v3(raw: str) -> list[dict]`：将十六进制 raw 字符串解析为 expectedV3 格式的字典列表。
- `v3_to_raw(v3_data: list[dict]) -> str`：将 expectedV3 格式的字典列表编码为 raw 十六进制字符串。

**V3 往返精度修正**：`v3_to_raw` 中对 `section_time` 转脉冲数的计算使用了 `math.ceil(... - 1e-9)` 修正浮点误差，避免整除场景下多算一个脉冲（例如 20 小节被错误识别为 38 小节）。

**批量导出**：`RawPanel` 支持接收 `LibraryPanel` 通过 `raw_selection_changed` 信号传递的多个波形，点击导出按钮后一次性生成所有选中波形的 raw 字符串。素材库中每个波形行右侧的 R 按钮用于切换选中状态。

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
    id: 'a1b2c3d4...',         // 32位唯一标识
    name: '示例波形',
    pulseData: [
      '0A0A0A0A64646464',   // 第1步：interval=10(0A), intensity=100(64)
      '1414141432323232',   // 第2步：interval=20(14), intensity=50(32)
    ]
  }
]
```

解析逻辑：
- 读取前 2 字符，十六进制转十进制得到 `interval` (范围 10-1000)。
- 读取第 9, 10 两个字符，十六进制转十进制得到 `intensity` (范围 0-100)。

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
