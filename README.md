# Coyote 波形绘制器 (PulseWaveStudio)

为 [DG-Lab-Coyote-Game-Hub](https://github.com/hyperzlib/DG-Lab-Coyote-Game-Hub) 设计的波形可视化编辑工具，支持手绘、函数生成、素材拼接和 JSON5 导入导出。

## 功能

- **手绘波形** — 鼠标拖动直接绘制间隔/强度曲线
- **函数生成** — 10 种函数（正弦/方波/锯齿/三角/幂/多项式/指数/对数/衰减/S形），支持周期、振幅、指数、系数、偏移参数
- **批量设置** — 双端范围滑条选区，一键填充间隔或强度
- **素材拼接** — 多波形 + 静默间隔拼接为完整序列
- **JSON5 导入导出** — 拖入 `pulse.json5` 导入，导出为 DG-Lab pulse 格式

## 快速开始

需要 Python 3.10+。

```bash
git clone https://github.com/kswag72/PulseWaveStudio.git
cd PulseWaveStudio
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat

pip install PyQt6
python main.py
```

### 构建 exe

```bash
pip install pyinstaller
python -m PyInstaller PulseWaveStudio.spec --clean
```

产出：`dist/PulseWaveStudio.exe`，单文件可分发。

### 字体

使用 [Maple Mono](https://github.com/subframe7536/maple-font) 字体，未包含在仓库中：

1. 前往 [Maple Font Releases](https://github.com/subframe7536/maple-font/releases) 下载 **MapleMono-NF-CN-unhinted**
2. 将 `MapleMono-NF-CN-ExtraBold.ttf` 放入 `src/fonts/`

缺少字体时程序仍可运行，回退到系统默认字体。

## 项目结构

```
├── main.py                 # 入口
├── PulseWaveStudio.spec    # PyInstaller 构建配置
├── src/
│   ├── IOC.ico             # 窗口图标
│   ├── fonts/              # 字体 (需手动下载)
│   ├── ui/
│   │   ├── main_window.py  # 主界面
│   │   ├── wave_canvas.py  # 波形画布
│   │   ├── range_slider.py # 双端范围滑条
│   │   └── styles.py       # 样式表
│   └── utils/
│       ├── data_loader.py  # JSON5 解析与导出
│       └── signal_ops.py   # 波形生成与平滑
```

## 许可证

[MIT](LICENSE)

## 免责声明

本工具为第三方社区工具，与 DG-Lab 官方无关。使用者应自行了解并遵守所在地区的相关法律法规。作者不对因使用本工具产生的任何直接或间接后果承担责任。请在安全、合法、知情同意的前提下使用。
