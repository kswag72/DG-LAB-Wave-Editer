# PulseWaveStudio — 项目结构重构

## TL;DR

> **Quick Summary**: 将单文件 `main.py`(362行 PyQt6 波形编辑器) 拆分为模块化 `src/` 目录结构，初始化 git 仓库，最终在 VSCode 中打开项目。
> 
> **Deliverables**:
> - `main.py` — 精简入口文件 (~10行)
> - `src/ui/wave_canvas.py` — WaveCanvas 画布组件
> - `src/ui/main_window.py` — MainWindow 主窗口控制器
> - `src/ui/styles.py` — QSS 样式表
> - `src/utils/data_loader.py` — JSON5 解析与导出纯函数
> - `src/utils/signal_ops.py` — 波形生成与数学运算纯函数
> - `requirements.txt` — 依赖列表
> - `.gitignore` — Python 项目 gitignore
> - 更新后的 `PulseWaveStudio.spec`
> - 初始化 git 仓库 + 首次提交
> 
> **Estimated Effort**: Short (约 30-45 分钟自动执行)
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 → Task 2/3/4/5 (并行) → Task 6 → Task 7 → Task 8 → Task 9

---

## Context

### Original Request
用户希望将 `venv/main.py` 单文件 PyQt6 应用重构为模块化目录结构，保持源代码逻辑不变，添加 git 管理，完成后在 VSCode 中打开。

### Interview Summary
**Key Discussions**:
- 目标结构由用户明确指定（`src/ui/` + `src/utils/` 二级模块结构）
- 保持代码逻辑和风格完全不变（紧凑格式、中文注释、分号连写等）
- `main - 副本.py` 是旧版本备份，不参与重构
- 使用 PyInstaller 打包为 exe，spec 文件需要适配新结构
- venv 根目录即为项目根目录

**Research Findings**:
- 依赖：PyQt6 6.10.2, PyInstaller 6.18.0, Python 3.13.5
- 当前 `.gitignore` 内容为 `*`（忽略一切），必须替换后才能 git add
- 存在 build/ 和 dist/ 目录（PyInstaller 产物）
- `WaveCanvas` 类完全自包含，无外部依赖，可干净提取
- `MainWindow` 的方法存在与 UI 状态的紧耦合，需提取纯函数核心

### Metis Review
**Identified Gaps** (addressed):
- 方法提取策略：选择 Option A（纯函数提取），utils 模块不依赖 Qt
- `.gitignore` 必须在 `git add` 前替换，否则所有文件被忽略
- PyInstaller spec 需要更新 `pathex` 和可能的 `hiddenimports`
- 使用绝对导入（`from src.ui.wave_canvas import WaveCanvas`）避免路径问题
- `__pycache__/` 目录需加入 `.gitignore`

---

## Work Objectives

### Core Objective
将单文件 PyQt6 应用拆分为清晰的模块化结构，启用 git 版本管理，保持功能行为完全一致。

### Concrete Deliverables
- 10 个新文件/修改文件构成目标目录结构
- 可用的 git 仓库（含初始提交）
- VSCode 中打开的项目工作区

### Definition of Done
- [ ] `python main.py` 启动无报错，窗口标题为 "coyote波形绘制器"
- [ ] 所有 10 个目标文件存在且内容正确
- [ ] `python -c "from src.ui.main_window import MainWindow"` 成功
- [ ] `git log --oneline` 显示初始提交
- [ ] `git status` 显示干净工作树
- [ ] VSCode 已打开项目目录

### Must Have
- 所有原始功能完整保留（波形绘制、JSON5导入导出、素材库管理、序列拼接、函数生成）
- 代码风格完全保持原样（紧凑格式、中文注释、分号连写、无类型注解）
- 正确的 Python `.gitignore`（排除 venv 内部文件、构建产物、缓存）
- `requirements.txt` 包含运行时依赖
- `PulseWaveStudio.spec` 适配新结构

### Must NOT Have (Guardrails)
- **禁止修改任何业务逻辑** — 纯结构重组，函数体完全一致
- **禁止添加类型注解、docstring、额外日志** — 保持原始代码风格
- **禁止创建 `setup.py`、`pyproject.toml`** — 只需 `requirements.txt`
- **禁止创建 `constants.py` 提取魔术数字** — 保持内联
- **禁止触碰 `Lib/`、`Scripts/`、`Include/`、`pyvenv.cfg`** — venv 内部文件
- **禁止添加单元测试** — 不在本次范围内
- **禁止使用相对导入** — 统一使用绝对导入 `from src.xxx import xxx`
- **禁止"改进"任何代码** — 不加错误处理、不重命名变量、不改格式

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: None
- **Framework**: None

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Application Launch**: Use Bash — run `python main.py` with timeout, verify process starts
- **Import Verification**: Use Bash — `python -c "import ..."` commands
- **File Structure**: Use Bash — verify file existence
- **Git Status**: Use Bash — git commands

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — sequential single task):
└── Task 1: 验证基线 + 创建目录结构 + 替换 .gitignore [quick]

Wave 2 (Core Module Extraction — MAX PARALLEL):
├── Task 2: 提取 WaveCanvas → src/ui/wave_canvas.py [quick]
├── Task 3: 提取 styles → src/ui/styles.py [quick]
├── Task 4: 提取 data_loader → src/utils/data_loader.py [quick]
├── Task 5: 提取 signal_ops → src/utils/signal_ops.py [quick]
└── Task 6: 创建 requirements.txt [quick]

Wave 3 (Integration — sequential):
├── Task 7: 创建 main_window.py + 更新 main.py 入口 [unspecified-high]
├── Task 8: 更新 PulseWaveStudio.spec + 验证完整功能 [quick]
└── Task 9: Git init + commit + 打开 VSCode [quick]

Wave FINAL (Verification — 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 1 → Tasks 2-5 (parallel) → Task 7 → Task 8 → Task 9 → F1-F4
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 | — | 2, 3, 4, 5, 6 |
| 2 | 1 | 7 |
| 3 | 1 | 7 |
| 4 | 1 | 7 |
| 5 | 1 | 7 |
| 6 | 1 | 8 |
| 7 | 2, 3, 4, 5 | 8 |
| 8 | 6, 7 | 9 |
| 9 | 8 | F1-F4 |
| F1-F4 | 9 | — |

### Agent Dispatch Summary

- **Wave 1**: 1 task — T1 → `quick`
- **Wave 2**: 5 tasks — T2-T5 → `quick`, T6 → `quick`
- **Wave 3**: 3 tasks — T7 → `unspecified-high`, T8 → `quick`, T9 → `quick`
- **FINAL**: 4 tasks — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [ ] 1. 验证基线 + 创建目录结构 + 替换 .gitignore

  **What to do**:
  - 在 venv 根目录运行 `python main.py`，确认当前应用可正常启动（启动后 3 秒内 kill 进程即可）
  - 创建目录结构：`src/`、`src/ui/`、`src/utils/`
  - 创建空的 `__init__.py` 文件：`src/__init__.py`、`src/ui/__init__.py`、`src/utils/__init__.py`
  - 替换 `.gitignore`（当前内容为 `*`，会忽略一切），新内容必须覆盖：
    ```
    # Python
    __pycache__/
    *.py[cod]
    *.pyo
    *.egg-info/
    
    # Virtual Environment internals
    Lib/
    Scripts/
    Include/
    pyvenv.cfg
    
    # PyInstaller build artifacts
    build/
    dist/
    
    # IDE
    .vscode/
    .idea/
    
    # OS
    Thumbs.db
    .DS_Store
    
    # Backup files
    main - 副本.py
    
    # Evidence (internal)
    .sisyphus/evidence/
    ```

  **Must NOT do**:
  - 不要修改 `main.py` 或任何源代码
  - 不要删除任何现有文件
  - 不要在 `__init__.py` 中添加任何内容（保持空文件）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单文件操作和目录创建，无复杂逻辑
  - **Skills**: []
    - No special skills needed for file/directory operations

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1 (solo)
  - **Blocks**: Tasks 2, 3, 4, 5, 6
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `main.py:359-362` — 当前入口点代码，用于验证基线启动

  **WHY Each Reference Matters**:
  - 需要确认原始 `main.py` 可以正常启动，作为重构前的基线

  **Acceptance Criteria**:
  - [ ] `python main.py` 进程启动成功（退出码 0 或被 kill）
  - [ ] 目录 `src/`、`src/ui/`、`src/utils/` 存在
  - [ ] 文件 `src/__init__.py`、`src/ui/__init__.py`、`src/utils/__init__.py` 存在且为空
  - [ ] `.gitignore` 包含 `Lib/`、`Scripts/`、`build/`、`dist/`、`__pycache__/`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 基线应用启动验证
    Tool: Bash
    Preconditions: 当前工作目录为 venv 根目录，python 可用
    Steps:
      1. 运行 `python main.py &` 后台启动进程
      2. 等待 3 秒
      3. 使用 taskkill 终止进程
      4. 检查进程启动时无 ImportError 或 SyntaxError
    Expected Result: 进程正常启动，无错误输出
    Failure Indicators: stderr 包含 "Error"、"Traceback"、"ImportError"
    Evidence: .sisyphus/evidence/task-1-baseline-launch.txt

  Scenario: 目录结构创建验证
    Tool: Bash
    Preconditions: Task 1 目录创建步骤已执行
    Steps:
      1. 运行 `python -c "import os; dirs=['src','src/ui','src/utils']; print('PASS' if all(os.path.isdir(d) for d in dirs) else 'FAIL')"`
      2. 运行 `python -c "import os; files=['src/__init__.py','src/ui/__init__.py','src/utils/__init__.py']; print('PASS' if all(os.path.isfile(f) for f in files) else 'FAIL')"`
      3. 检查 `.gitignore` 内容包含关键条目
    Expected Result: 两个检查均输出 "PASS"，.gitignore 包含必要排除项
    Failure Indicators: 输出 "FAIL" 或文件不存在
    Evidence: .sisyphus/evidence/task-1-directory-structure.txt
  ```

  **Commit**: NO (groups with final commit)

- [ ] 2. 提取 WaveCanvas → src/ui/wave_canvas.py

  **What to do**:
  - 从 `main.py` 第 12-89 行提取 `WaveCanvas` 类
  - 创建 `src/ui/wave_canvas.py`，包含必要的导入和完整的类定义
  - 导入清单（仅需这些）：
    ```python
    from PyQt6.QtWidgets import QWidget
    from PyQt6.QtCore import Qt, QPoint
    from PyQt6.QtGui import QPainter, QPen, QColor
    ```
  - 类体代码必须与原始 `main.py:12-89` 完全一致，一字不差
  - 不要在文件开头添加任何注释或 docstring

  **Must NOT do**:
  - 不要添加类型注解
  - 不要修改任何方法体
  - 不要添加 `__all__` 导出
  - 不要添加模块级注释

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单代码复制提取，无逻辑变更
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 3, 4, 5, 6)
  - **Blocks**: Task 7
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `main.py:1-10` — 原始导入语句，用于确定 WaveCanvas 需要的最小导入集
  - `main.py:12-89` — WaveCanvas 类完整代码，必须原样复制

  **WHY Each Reference Matters**:
  - `main.py:12-89` 是要提取的目标代码，必须逐字复制
  - `main.py:1-10` 用于确定 WaveCanvas 实际用到的 Qt 类（QWidget, Qt, QPoint, QPainter, QPen, QColor）

  **Acceptance Criteria**:
  - [ ] `src/ui/wave_canvas.py` 存在
  - [ ] `python -c "from src.ui.wave_canvas import WaveCanvas; print('OK')"` 输出 "OK"
  - [ ] WaveCanvas 类包含所有原始方法：`__init__`, `update_geometry`, `paintEvent`, `draw_plot`, `handle_mouse`, `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: WaveCanvas 模块导入验证
    Tool: Bash
    Preconditions: src/ui/wave_canvas.py 已创建
    Steps:
      1. 运行 `python -c "from src.ui.wave_canvas import WaveCanvas; print(type(WaveCanvas)); print('OK')"`
      2. 确认输出包含 "<class" 和 "OK"
    Expected Result: 导入成功，WaveCanvas 是一个类
    Failure Indicators: ImportError, ModuleNotFoundError
    Evidence: .sisyphus/evidence/task-2-wave-canvas-import.txt

  Scenario: WaveCanvas 方法完整性验证
    Tool: Bash
    Preconditions: 模块已创建
    Steps:
      1. 运行 `python -c "from src.ui.wave_canvas import WaveCanvas; methods=['update_geometry','paintEvent','draw_plot','handle_mouse','mousePressEvent','mouseMoveEvent','mouseReleaseEvent']; missing=[m for m in methods if not hasattr(WaveCanvas, m)]; print('PASS' if not missing else f'MISSING: {missing}')"`
    Expected Result: 输出 "PASS"
    Failure Indicators: 输出包含 "MISSING"
    Evidence: .sisyphus/evidence/task-2-wave-canvas-methods.txt
  ```

  **Commit**: NO (groups with final commit)

- [ ] 3. 提取 styles → src/ui/styles.py

  **What to do**:
  - 从 `main.py:102-131` 提取 `apply_styles` 方法中的 QSS 样式字符串
  - 创建 `src/ui/styles.py`，定义常量 `MAIN_STYLESHEET`
  - 格式：
    ```python
    MAIN_STYLESHEET = """
        QMainWindow { background-color: #121212; }
        ... (完整复制 main.py:103-131 中的 QSS 内容)
    """
    ```
  - QSS 字符串内容必须与原始完全一致（包括中文注释 `/* 高对比度滚动条 */`）

  **Must NOT do**:
  - 不要使用函数而非常量
  - 不要拆分为多个样式变量
  - 不要修改任何 CSS 属性值

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯字符串提取，无逻辑
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 4, 5, 6)
  - **Blocks**: Task 7
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `main.py:102-131` — apply_styles 方法中的完整 QSS 字符串

  **WHY Each Reference Matters**:
  - 这是要提取的 QSS 样式内容，必须原样复制包括中文注释

  **Acceptance Criteria**:
  - [ ] `src/ui/styles.py` 存在
  - [ ] `python -c "from src.ui.styles import MAIN_STYLESHEET; print('OK' if '121212' in MAIN_STYLESHEET else 'FAIL')"`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 样式表导入验证
    Tool: Bash
    Preconditions: src/ui/styles.py 已创建
    Steps:
      1. 运行 `python -c "from src.ui.styles import MAIN_STYLESHEET; print(type(MAIN_STYLESHEET)); print(len(MAIN_STYLESHEET)); print('OK')"`
      2. 确认 MAIN_STYLESHEET 是字符串且长度大于 100
    Expected Result: 类型为 str，长度 > 100，输出 "OK"
    Failure Indicators: ImportError, 长度为 0
    Evidence: .sisyphus/evidence/task-3-styles-import.txt

  Scenario: 样式表内容完整性
    Tool: Bash
    Preconditions: 模块已创建
    Steps:
      1. 运行 `python -c "from src.ui.styles import MAIN_STYLESHEET; checks=['#121212','#00ffcc','QScrollBar','高对比度']; missing=[c for c in checks if c not in MAIN_STYLESHEET]; print('PASS' if not missing else f'MISSING: {missing}')"`
    Expected Result: 输出 "PASS"
    Failure Indicators: 输出包含 "MISSING"
    Evidence: .sisyphus/evidence/task-3-styles-content.txt
  ```

  **Commit**: NO (groups with final commit)

- [ ] 4. 提取 data_loader → src/utils/data_loader.py

  **What to do**:
  - 从 `main.py` 提取 JSON5 解析与导出逻辑为**纯函数**（不依赖 Qt）
  - 创建 `src/utils/data_loader.py`，包含以下函数：

  **函数 1: `parse_json5_content(content: str) -> list`**
  - 提取自 `main.py:226-241` `import_file` 方法的核心解析逻辑
  - 输入：文件内容字符串
  - 输出：解析后的波形数据列表 `[{"id": ..., "name": ..., "intervals": [...], "intensities": [...], "steps": N}, ...]`
  - 包含 regex 清洗逻辑（去注释、键名加引号、单引号转双引号、去尾逗号）
  - 注意：**不包含** file open、QMessageBox 错误处理 — 这些留在 MainWindow

  **函数 2: `format_pulse_export(sequence: list) -> str`**
  - 提取自 `main.py:333-342` `generate_code` 方法的格式化逻辑
  - 输入：sequence 列表
  - 输出：格式化后的 JSON5 字符串
  - 包含 hex 编码逻辑和静默填充逻辑

  **函数 3: `format_library_export(wave_lib: list) -> str`**
  - 提取自 `main.py:349-354` `export_entire_library` 方法的格式化逻辑
  - 输入：wave_lib 列表
  - 输出：格式化后的完整库 JSON5 字符串

  - 导入清单（仅标准库）：
    ```python
    import json
    import re
    import random
    import math
    ```

  **Must NOT do**:
  - 不要添加类型注解（函数签名中的冒号注解只是上面的说明，实际代码不要写）
  - 不要添加 try/except — 异常处理留在 MainWindow
  - 不要导入任何 PyQt6 模块
  - 不要改变原始的 hex 编码算法

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 提取纯函数，逻辑清晰
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 3, 5, 6)
  - **Blocks**: Task 7
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `main.py:224-243` — import_file 方法完整代码，提取核心解析逻辑
  - `main.py:333-347` — generate_code 方法完整代码，提取格式化逻辑
  - `main.py:349-357` — export_entire_library 方法完整代码，提取格式化逻辑
  - `main.py:1-5` — 原始导入语句，确定需要的标准库

  **WHY Each Reference Matters**:
  - `main.py:226-241`：parse_json5_content 的核心逻辑来源，regex 清洗 + JSON 解析 + 数据转换
  - `main.py:334-342`：format_pulse_export 的逻辑来源，hex 编码 + 静默填充
  - `main.py:350-354`：format_library_export 的逻辑来源，完整库格式化
  - 所有函数体必须与原始逻辑完全一致，只是从 `self.xxx` 变为函数参数

  **Acceptance Criteria**:
  - [ ] `src/utils/data_loader.py` 存在
  - [ ] `python -c "from src.utils.data_loader import parse_json5_content, format_pulse_export, format_library_export; print('OK')"` 成功
  - [ ] 模块中无 PyQt6 导入

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: data_loader 函数导入验证
    Tool: Bash
    Preconditions: src/utils/data_loader.py 已创建
    Steps:
      1. 运行 `python -c "from src.utils.data_loader import parse_json5_content, format_pulse_export, format_library_export; print('OK')"`
      2. 确认无 ImportError
    Expected Result: 输出 "OK"
    Failure Indicators: ImportError, ModuleNotFoundError
    Evidence: .sisyphus/evidence/task-4-data-loader-import.txt

  Scenario: parse_json5_content 功能验证
    Tool: Bash
    Preconditions: 模块已创建
    Steps:
      1. 运行 `python -c "from src.utils.data_loader import parse_json5_content; test_input='[{id: \"test\", name: \"wave1\", pulseData: [\"0A0A0A0A64646464\"]}]'; result=parse_json5_content(test_input); print('PASS' if len(result)==1 and result[0]['name']=='wave1' else f'FAIL: {result}')"`
    Expected Result: 输出 "PASS"
    Failure Indicators: 输出 "FAIL" 或解析错误
    Evidence: .sisyphus/evidence/task-4-parse-json5-test.txt

  Scenario: 无 PyQt6 依赖验证
    Tool: Bash
    Preconditions: 模块已创建
    Steps:
      1. 运行 `python -c "import ast; tree=ast.parse(open('src/utils/data_loader.py').read()); imports=[n.names[0].name for n in ast.walk(tree) if isinstance(n, ast.Import)]; from_imports=[n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module]; all_imports=imports+from_imports; has_qt=any('Qt' in i or 'PyQt' in i for i in all_imports); print('PASS' if not has_qt else 'FAIL: Qt dependency found')"`
    Expected Result: 输出 "PASS"
    Failure Indicators: 输出 "FAIL"
    Evidence: .sisyphus/evidence/task-4-no-qt-dependency.txt
  ```

  **Commit**: NO (groups with final commit)

- [ ] 5. 提取 signal_ops → src/utils/signal_ops.py

  **What to do**:
  - 从 `main.py` 提取波形生成和数学运算逻辑为**纯函数**（不依赖 Qt）
  - 创建 `src/utils/signal_ops.py`，包含以下函数：

  **函数 1: `generate_wave(wave_type, cycles, amplitude, steps) -> list`**
  - 提取自 `main.py:301-309` `apply_func` 方法的核心计算逻辑
  - 输入：wave_type (int, 0=正弦 1=方波 2=锯齿 3=三角), cycles (int), amplitude (int), steps (int)
  - 输出：intensities 列表 `[int, ...]`
  - 逻辑必须与原始完全一致：
    ```python
    for i in range(steps):
        p = (i/(steps-1))*cycles*math.pi*2 if steps>1 else 0
        if wave_type==0: v=(math.sin(p-math.pi/2)+1)/2*amplitude
        elif wave_type==1: v=amplitude if math.sin(p)>=0 else 0
        elif wave_type==2: v=((i*cycles/steps)%1)*amplitude
        else: v=(1-abs(((i*cycles/steps)%1)*2-1))*amplitude
        result.append(int(v))
    ```

  **函数 2: `smooth_array(arr, n) -> list`**
  - 提取自 `main.py:312-316` `smooth_wave` 方法中的内部 `sm` 函数
  - 输入：arr (list), n (int, 有效长度)
  - 输出：平滑后的列表
  - 逻辑：`r[i] = int(arr[i-1]*0.25 + arr[i]*0.5 + arr[i+1]*0.25)`

  - 导入清单：`import math`

  **Must NOT do**:
  - 不要添加类型注解
  - 不要改变数学公式
  - 不要导入 PyQt6
  - 不要添加参数验证

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯函数提取，逻辑清晰
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 3, 4, 6)
  - **Blocks**: Task 7
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `main.py:301-310` — apply_func 方法完整代码
  - `main.py:312-319` — smooth_wave 方法和内部 sm 函数

  **WHY Each Reference Matters**:
  - `main.py:302-309`：generate_wave 的精确数学逻辑，4 种波形生成算法
  - `main.py:313-316`：smooth_array 的平滑算法（加权平均）

  **Acceptance Criteria**:
  - [ ] `src/utils/signal_ops.py` 存在
  - [ ] `python -c "from src.utils.signal_ops import generate_wave, smooth_array; print('OK')"` 成功
  - [ ] `generate_wave(0, 1, 100, 10)` 返回长度为 10 的列表

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: signal_ops 函数导入验证
    Tool: Bash
    Preconditions: src/utils/signal_ops.py 已创建
    Steps:
      1. 运行 `python -c "from src.utils.signal_ops import generate_wave, smooth_array; print('OK')"`
    Expected Result: 输出 "OK"
    Failure Indicators: ImportError
    Evidence: .sisyphus/evidence/task-5-signal-ops-import.txt

  Scenario: generate_wave 正弦波验证
    Tool: Bash
    Preconditions: 模块已创建
    Steps:
      1. 运行 `python -c "from src.utils.signal_ops import generate_wave; result=generate_wave(0, 1, 100, 10); print('PASS' if len(result)==10 and result[0]==0 and max(result)==100 else f'FAIL: {result}')"`
    Expected Result: 输出 "PASS"（正弦波从 0 开始，最大值 100）
    Failure Indicators: 输出 "FAIL" 或计算错误
    Evidence: .sisyphus/evidence/task-5-sine-wave-test.txt

  Scenario: smooth_array 功能验证
    Tool: Bash
    Preconditions: 模块已创建
    Steps:
      1. 运行 `python -c "from src.utils.signal_ops import smooth_array; result=smooth_array([0, 100, 0, 100, 0], 5); print('PASS' if result[1]==50 and result[3]==50 else f'FAIL: {result}')"`
    Expected Result: 输出 "PASS"（加权平均平滑）
    Failure Indicators: 输出 "FAIL"
    Evidence: .sisyphus/evidence/task-5-smooth-test.txt
  ```

  **Commit**: NO (groups with final commit)

- [ ] 6. 创建 requirements.txt

  **What to do**:
  - 创建 `requirements.txt`，仅包含运行时依赖（不含 PyInstaller 等开发工具）
  - 内容：
    ```
    PyQt6>=6.10.0
    ```
  - 只需要 PyQt6，其他都是标准库（sys, math, json, random, re）
  - PyInstaller 是构建工具，不应该在 requirements.txt 中

  **Must NOT do**:
  - 不要包含 PyInstaller（构建工具）
  - 不要包含 pip、setuptools 等基础工具
  - 不要使用 `pip freeze` 直接输出（会包含所有包）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单文件创建
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 3, 4, 5)
  - **Blocks**: Task 8
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `main.py:1-10` — 导入语句，确定实际运行时依赖

  **WHY Each Reference Matters**:
  - 通过分析 import 语句确定只有 PyQt6 是第三方依赖

  **Acceptance Criteria**:
  - [ ] `requirements.txt` 存在
  - [ ] 内容包含 `PyQt6`
  - [ ] 不包含 `PyInstaller`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: requirements.txt 内容验证
    Tool: Bash
    Preconditions: 文件已创建
    Steps:
      1. 运行 `python -c "content=open('requirements.txt').read(); has_pyqt='PyQt6' in content; no_pyinstaller='PyInstaller' not in content and 'pyinstaller' not in content; print('PASS' if has_pyqt and no_pyinstaller else f'FAIL: has_pyqt={has_pyqt}, no_pyinstaller={no_pyinstaller}')"`
    Expected Result: 输出 "PASS"
    Failure Indicators: 输出 "FAIL"
    Evidence: .sisyphus/evidence/task-6-requirements-check.txt
  ```

  **Commit**: NO (groups with final commit)

- [ ] 7. 创建 main_window.py + 更新 main.py 入口

  **What to do**:
  
  **Part A: 创建 `src/ui/main_window.py`**
  - 将 `MainWindow` 类从 `main.py:91-358` 移入此文件
  - 添加必要导入：
    ```python
    import math
    import random
    from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                 QPushButton, QSlider, QLabel, QLineEdit, QComboBox,
                                 QScrollArea, QFrame, QFileDialog, QTextEdit, QSpinBox, QMessageBox)
    from PyQt6.QtCore import Qt
    from src.ui.wave_canvas import WaveCanvas
    from src.ui.styles import MAIN_STYLESHEET
    from src.utils.data_loader import parse_json5_content, format_pulse_export, format_library_export
    from src.utils.signal_ops import generate_wave, smooth_array
    ```
  - **修改 `apply_styles` 方法**：原本是内联 QSS 字符串，改为使用导入的 `MAIN_STYLESHEET`：
    ```python
    def apply_styles(self):
        self.setStyleSheet(MAIN_STYLESHEET)
    ```
  - **修改 `import_file` 方法**：调用 `parse_json5_content` 替代内联解析逻辑：
    ```python
    def import_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = parse_json5_content(content)
                for item in data:
                    self.wave_lib.append(item)
                self.refresh_lib_ui()
        except Exception as err: QMessageBox.critical(self, "解析错误", str(err))
    ```
  - **修改 `apply_func` 方法**：调用 `generate_wave` 替代内联计算：
    ```python
    def apply_func(self):
        t, c, a, s = self.f_type.currentIndex(), self.f_cyc.value(), self.f_amp.value(), self.canvas.steps
        result = generate_wave(t, c, a, s)
        for i in range(s):
            self.canvas.intensities[i] = result[i]
        self.canvas.update()
    ```
  - **修改 `smooth_wave` 方法**：调用 `smooth_array` 替代内联算法：
    ```python
    def smooth_wave(self):
        self.canvas.intervals = smooth_array(self.canvas.intervals, self.canvas.steps)
        self.canvas.intensities = smooth_array(self.canvas.intensities, self.canvas.steps)
        self.canvas.update()
    ```
  - **修改 `generate_code` 方法**：调用 `format_pulse_export` 替代内联格式化：
    ```python
    def generate_code(self, is_save):
        code = format_pulse_export(self.sequence)
        self.output.setText(code)
        if is_save:
            p, _ = QFileDialog.getSaveFileName(self, "保存", "export.json5", "JSON5 (*.json5)")
            if p:
                with open(p, 'w', encoding='utf-8') as f: f.write(code)
    ```
  - **修改 `export_entire_library` 方法**：调用 `format_library_export` 替代内联格式化：
    ```python
    def export_entire_library(self):
        full = format_library_export(self.wave_lib)
        p, _ = QFileDialog.getSaveFileName(self, "导出资产库", "library.json5", "JSON5 (*.json5)")
        if p:
            with open(p, 'w', encoding='utf-8') as f: f.write(full)
    ```
  - 所有其他方法保持原样（`init_ui`, `sync_step_val`, `dragEnterEvent`, `dropEvent`, `refresh_lib_ui`, `load_to_canvas`, `del_from_lib`, `add_to_seq`, `add_gap_to_seq`, `clear_sequence`, `refresh_seq_ui`, `save_sequence_to_library`, `clear_canvas`, `save_to_lib`）

  **Part B: 更新 `main.py` 入口文件**
  - 将 `main.py` 的全部内容替换为精简入口：
    ```python
    import sys
    from PyQt6.QtWidgets import QApplication
    from src.ui.main_window import MainWindow

    if __name__ == "__main__":
        app = QApplication(sys.argv)
        w = MainWindow(); w.show()
        sys.exit(app.exec())
    ```
  - **重要**：在替换 `main.py` 前，确认 Tasks 2-5 的所有模块已就位

  **Must NOT do**:
  - 不要修改未提到的方法体
  - 不要删除 `re` 导入如果 main_window 中仍需用到（检查：当前 re 已移到 data_loader，main_window 不再需要）
  - 不要添加额外导入
  - 不要修改 `init_ui` 中的 UI 布局代码

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 这是最复杂的任务，需要精确修改多个方法的调用方式并确保一致性
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (sequential)
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 2, 3, 4, 5

  **References**:

  **Pattern References**:
  - `main.py:91-358` — MainWindow 类完整代码（268行），这是要移动和修改的代码
  - `main.py:359-362` — 原始入口代码
  - `main.py:102-131` — apply_styles 方法，要改为使用 MAIN_STYLESHEET
  - `main.py:224-243` — import_file 方法，要改为调用 parse_json5_content
  - `main.py:301-310` — apply_func 方法，要改为调用 generate_wave
  - `main.py:312-319` — smooth_wave 方法，要改为调用 smooth_array
  - `main.py:333-347` — generate_code 方法，要改为调用 format_pulse_export
  - `main.py:349-357` — export_entire_library 方法，要改为调用 format_library_export

  **API/Type References**:
  - `src/ui/wave_canvas.py:WaveCanvas` — 画布组件类
  - `src/ui/styles.py:MAIN_STYLESHEET` — 样式表常量
  - `src/utils/data_loader.py:parse_json5_content, format_pulse_export, format_library_export` — 数据处理函数
  - `src/utils/signal_ops.py:generate_wave, smooth_array` — 信号处理函数

  **WHY Each Reference Matters**:
  - 原始 `main.py` 包含所有要移动和修改的代码
  - 各 `src/` 模块的导出接口是修改调用方式的依据
  - 每个被修改的方法必须保持与原始相同的外部行为

  **Acceptance Criteria**:
  - [ ] `src/ui/main_window.py` 存在且包含 MainWindow 类
  - [ ] `main.py` 已精简为入口文件（约 8 行）
  - [ ] `python -c "from src.ui.main_window import MainWindow; print('OK')"` 成功
  - [ ] `python main.py` 启动无错误

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 完整应用启动验证
    Tool: Bash
    Preconditions: 所有模块已创建，main.py 已更新
    Steps:
      1. 运行 `python main.py &` 后台启动
      2. 等待 5 秒确认进程存活
      3. 使用 taskkill 终止进程
      4. 检查 stderr 无错误输出
    Expected Result: 应用正常启动，窗口标题 "coyote波形绘制器"
    Failure Indicators: ImportError, AttributeError, 进程立即退出
    Evidence: .sisyphus/evidence/task-7-app-launch.txt

  Scenario: 所有模块导入链验证
    Tool: Bash
    Preconditions: 所有文件就位
    Steps:
      1. 运行 `python -c "from src.ui.main_window import MainWindow; from src.ui.wave_canvas import WaveCanvas; from src.ui.styles import MAIN_STYLESHEET; from src.utils.data_loader import parse_json5_content, format_pulse_export, format_library_export; from src.utils.signal_ops import generate_wave, smooth_array; print('All imports OK')"`
    Expected Result: 输出 "All imports OK"
    Failure Indicators: 任何 ImportError
    Evidence: .sisyphus/evidence/task-7-all-imports.txt

  Scenario: main.py 入口文件精简验证
    Tool: Bash
    Preconditions: main.py 已更新
    Steps:
      1. 运行 `python -c "lines=open('main.py').readlines(); print(f'Lines: {len(lines)}'); print('PASS' if len(lines) < 15 else 'FAIL: too many lines')"`
    Expected Result: main.py 少于 15 行
    Failure Indicators: 超过 15 行说明未充分精简
    Evidence: .sisyphus/evidence/task-7-entry-point-size.txt

  Scenario: MainWindow 方法完整性
    Tool: Bash
    Preconditions: main_window.py 已创建
    Steps:
      1. 运行 `python -c "from src.ui.main_window import MainWindow; methods=['init_ui','apply_styles','sync_step_val','dragEnterEvent','dropEvent','import_file','refresh_lib_ui','load_to_canvas','del_from_lib','add_to_seq','add_gap_to_seq','clear_sequence','refresh_seq_ui','save_sequence_to_library','apply_func','smooth_wave','clear_canvas','save_to_lib','generate_code','export_entire_library']; missing=[m for m in methods if not hasattr(MainWindow, m)]; print('PASS' if not missing else f'MISSING: {missing}')"`
    Expected Result: 输出 "PASS"
    Failure Indicators: 输出 "MISSING"
    Evidence: .sisyphus/evidence/task-7-mainwindow-methods.txt
  ```

  **Commit**: NO (groups with final commit)

- [ ] 8. 更新 PulseWaveStudio.spec + 验证完整功能

  **What to do**:
  - 更新 `PulseWaveStudio.spec` 适配新的模块结构：
    - `pathex` 添加项目根目录确保 `src` 包可被发现
    - `hiddenimports` 添加所有 `src` 子模块（PyInstaller 可能无法自动发现）
    - `datas` 保持为空（无数据文件需要打包）
  - 更新后的关键部分：
    ```python
    a = Analysis(
        ['main.py'],
        pathex=['.'],
        binaries=[],
        datas=[],
        hiddenimports=[
            'src',
            'src.ui',
            'src.ui.main_window',
            'src.ui.wave_canvas',
            'src.ui.styles',
            'src.utils',
            'src.utils.data_loader',
            'src.utils.signal_ops',
        ],
        ...
    )
    ```
  - 保留原有的所有其他配置（name='PulseWaveStudio', console=False, upx=True 等）
  - 验证 spec 文件语法正确

  **Must NOT do**:
  - 不要修改 exe 配置（name、console、upx 等）
  - 不要实际运行 PyInstaller 构建（耗时且不在范围内）
  - 不要删除原有配置项

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单文件修改，改动明确
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (after Task 7)
  - **Blocks**: Task 9
  - **Blocked By**: Tasks 6, 7

  **References**:

  **Pattern References**:
  - `PulseWaveStudio.spec:1-38` — 当前 spec 文件完整内容

  **WHY Each Reference Matters**:
  - 需要在现有配置基础上添加 pathex 和 hiddenimports，保留其他配置

  **Acceptance Criteria**:
  - [ ] `PulseWaveStudio.spec` 包含 `hiddenimports` 列表
  - [ ] `PulseWaveStudio.spec` 的 `pathex` 包含 `'.'`
  - [ ] spec 文件语法正确（`python -c "exec(open('PulseWaveStudio.spec').read())"` 不报错... 注意：spec 文件使用 PyInstaller 内部 API，此验证可能不适用，改用语法检查）

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: spec 文件内容验证
    Tool: Bash
    Preconditions: PulseWaveStudio.spec 已更新
    Steps:
      1. 运行 `python -c "content=open('PulseWaveStudio.spec').read(); checks=['hiddenimports','src.ui.main_window','src.utils.data_loader','pathex']; missing=[c for c in checks if c not in content]; print('PASS' if not missing else f'MISSING: {missing}')"`
    Expected Result: 输出 "PASS"
    Failure Indicators: 输出 "MISSING"
    Evidence: .sisyphus/evidence/task-8-spec-content.txt

  Scenario: spec 文件语法验证
    Tool: Bash
    Preconditions: 文件已更新
    Steps:
      1. 运行 `python -c "import ast; ast.parse(open('PulseWaveStudio.spec').read()); print('SYNTAX OK')"` （注意：spec 文件可能用 PyInstaller 专用函数如 Analysis/PYZ/EXE，ast.parse 可以检查 Python 语法但无法验证运行时）
    Expected Result: Python 语法正确
    Failure Indicators: SyntaxError
    Evidence: .sisyphus/evidence/task-8-spec-syntax.txt
  ```

  **Commit**: NO (groups with final commit)

- [ ] 9. Git init + commit + 打开 VSCode

  **What to do**:
  - 确认 `.gitignore` 已正确设置（Task 1 中完成）
  - 在 venv 根目录执行 `git init`
  - 执行 `git add .`（此时 .gitignore 应排除 Lib/, Scripts/ 等）
  - 验证 `git status` 只显示目标文件（main.py, src/**, requirements.txt, .gitignore）
  - 执行 `git commit -m "refactor: restructure monolithic main.py into modular src/ package"`
  - 验证 `git log --oneline` 显示提交
  - 执行 `code .` 在 VSCode 中打开项目

  **Must NOT do**:
  - 不要配置 git user.name / user.email（使用系统默认）
  - 不要创建 .github/ 目录或 CI 配置
  - 不要推送到远程仓库

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 标准 git 操作
  - **Skills**: [`git-master`]
    - `git-master`: git 操作专家，确保正确的提交流程

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (final sequential)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 8

  **References**:

  **Pattern References**:
  - `.gitignore` — Task 1 中创建的 gitignore 文件

  **WHY Each Reference Matters**:
  - gitignore 内容决定了哪些文件会被 git 跟踪

  **Acceptance Criteria**:
  - [ ] `git log --oneline` 显示至少 1 个提交
  - [ ] `git status` 显示 "nothing to commit, working tree clean"
  - [ ] `PulseWaveStudio.spec` 在 git 跟踪文件中（`git ls-files` 包含它）
  - [ ] 尝试执行 `code .` 打开 VSCode（若 `code` CLI 不可用则跳过，不阻塞任务完成）

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Git 仓库初始化验证
    Tool: Bash
    Preconditions: 所有文件已就位，.gitignore 正确
    Steps:
      1. 运行 `git log --oneline`
      2. 运行 `git status`
      3. 运行 `git ls-files` 查看跟踪的文件列表
    Expected Result: 有 1 个提交，工作树干净，跟踪文件包含 main.py, src/ 下的文件, requirements.txt, .gitignore
    Failure Indicators: "not a git repository", "Untracked files", 跟踪了 Lib/ 或 Scripts/
    Evidence: .sisyphus/evidence/task-9-git-status.txt

  Scenario: 排除 venv 内部文件验证
    Tool: Bash
    Preconditions: git 已初始化并提交
    Steps:
      1. 运行 `git ls-files` 并检查不包含 Lib/, Scripts/, Include/, build/, dist/ 下的文件
      2. 运行 `python -c "import subprocess; files=subprocess.check_output(['git','ls-files']).decode().split('\n'); bad=[f for f in files if any(f.startswith(p) for p in ['Lib/','Scripts/','Include/','build/','dist/'])]; print('PASS' if not bad else f'FAIL: tracked venv files: {bad[:5]}')"`
    Expected Result: 输出 "PASS"
    Failure Indicators: 输出 "FAIL" 或跟踪了 venv 内部文件
    Evidence: .sisyphus/evidence/task-9-gitignore-verify.txt

  Scenario: VSCode 打开（best-effort，不阻塞）
    Tool: Bash
    Preconditions: git 提交完成
    Steps:
      1. 检查 `code --version` 是否可用
      2. 若可用则运行 `code .`
      3. 若不可用则输出 "SKIP: code CLI not available" 并标记为通过
    Expected Result: VSCode 已启动，或 CLI 不可用时跳过
    Failure Indicators: 无（此场景为 best-effort，不阻塞任务）
    Evidence: .sisyphus/evidence/task-9-vscode-open.txt
  ```

  **Commit**: YES (this task IS the commit)
  - Message: `refactor: restructure monolithic main.py into modular src/ package`
  - Files: main.py, src/**, requirements.txt, .gitignore, PulseWaveStudio.spec
  - Pre-commit: `python -c "from src.ui.main_window import MainWindow; print('OK')"`

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `python -m py_compile main.py` + `python -m py_compile src/ui/main_window.py` + all modules. Review all changed files for: unused imports, broken references, missing `__init__.py` exports. Check AI slop: excessive comments not in original, added type hints, reformatted code.
  Output: `Compile [PASS/FAIL] | Imports [N clean/N issues] | Style preserved [YES/NO] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Run `python main.py` — verify window appears. Test drag-and-drop JSON5 import (create a test file). Test wave generation (select 正弦波, generate). Test save/export buttons. Test canvas drawing. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Launch [PASS/FAIL] | Features [N/N] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  Compare original `main.py` function bodies with extracted modules. Verify 1:1 code preservation — no logic changes, no style changes, no additions. Check every extracted function body is identical to original. Flag any unaccounted changes.
  Output: `Functions [N/N identical] | Additions [CLEAN/N] | VERDICT`

---

## Commit Strategy

- **Single commit after all tasks complete**: `refactor: restructure monolithic main.py into modular src/ package`
  - Files: main.py, src/**, requirements.txt, .gitignore, PulseWaveStudio.spec
  - Verify: `python main.py` launches successfully

---

## Success Criteria

### Verification Commands
```bash
# 1. Application launches
python main.py  # Expected: Window appears, no errors (kill after 3s)

# 2. All imports resolve
python -c "from src.ui.main_window import MainWindow; from src.ui.wave_canvas import WaveCanvas; from src.ui.styles import MAIN_STYLESHEET; from src.utils.data_loader import parse_json5_content, format_pulse_export, format_library_export; from src.utils.signal_ops import generate_wave, smooth_array; print('All imports OK')"

# 3. File structure
python -c "import os; files=['main.py','requirements.txt','src/__init__.py','src/ui/__init__.py','src/ui/main_window.py','src/ui/wave_canvas.py','src/ui/styles.py','src/utils/__init__.py','src/utils/data_loader.py','src/utils/signal_ops.py']; missing=[f for f in files if not os.path.exists(f)]; print('PASS' if not missing else f'MISSING: {missing}')"

# 4. Git status clean
git log --oneline  # Expected: 1 commit
git status  # Expected: nothing to commit
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Application launches and functions correctly
- [ ] Git repo initialized with clean commit
- [ ] VSCode opened on project directory
