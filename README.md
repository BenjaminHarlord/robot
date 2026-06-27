# ROSA — Robot Oriented Sensing Agent

**开发者：安德烈·萨沙·阿列克谢维奇**

ROSA 是一个模块化 VLA（Vision-Language-Action）智能体系统，实现三层解耦架构：
- **Vision** — YOLO 实时目标检测（30 FPS daemon 线程）
- **Language** — DeepSeek 自然语言理解与生成（统一自然回复管道）
- **Action** — ROS2 机器人控制层（待扩展）

支持中文语音输入/输出，摄像头实时感知，与用户自然对话。

---

## 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│  main.py  (PyQt6 GUI)                                           │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │ 聊天面板 │ │ 检测预览  │ │ 语音输入按钮  │ │ 语音输出按钮     │ │
│  └────┬─────┘ └──────────┘ └──────┬───────┘ └───────┬──────────┘ │
│       │                           │                   │           │
├───────┼───────────────────────────┼───────────────────┼───────────┤
│       ▼                           ▼                   ▼           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  agent.py — 总调度器                                         │ │
│  │  process(user_input) → 解析 → 决策 → 执行 → LLM 自然回复     │ │
│  └──┬──────────┬──────────┬──────────┬─────────────────────────┘ │
│     ▼          ▼          ▼          ▼                            │
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌──────────┐                     │
│  │Command│ │Decision│ │Percep.│ │LLM mw.   │                     │
│  │ mw.   │ │ mw.    │ │ mw.   │ │(DeepSeek)│                     │
│  └───────┘ └───────┘ └───┬───┘ └──────────┘                     │
│                          │                                        │
│  ┌──────────┐ ┌──────────┼──────────┐                            │
│  │TTS mw.   │ │STT mw.   │Model mw. │                            │
│  │(Piper)   │ │(Vosk)    │(下载/检) │                            │
│  └──────────┘ └──────────┘ └──────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户输入（文字 / 麦克风语音）
      │
      ▼
CommandMiddleware.parse()
      │ → cmd_type: detect / inquire / chat / action
      │ → target: 椅子 / person / *
      ▼
DecisionMiddleware.decide()
      │ → 规则匹配 (DECISION_RULES) 优先
      │ → LLM 辅助决策兜底
      │ → ActionType: do_detect / count_objects / check_presence / chat_reply / ...
      ▼
agent._execute_decision()
      │ → 按 ActionType 分发到对应 handler
      ▼
handler._exec_xxx()
      │ → PerceptionMiddleware.get_latest_detection()
      │ → 组装检测数据
      ▼
_llm_reply(_NATURAL_PROMPT, context)
      │ → DeepSeek API（同步）
      │ → 返回自然语言回复（2-4 句中文）
      ▼
UI 显示 + TTS 朗读
```

### 回复通道：统一自然管道

所有输出（检测 / 计数 / 存在性查询 / 闲聊）都经过同一套 `_llm_reply()` 管道，系统提示词统一注入开发者身份和对话风格：

```
你是ROSA，一个有视觉能力的机器人助手。
你的开发者是安德烈·萨沙·阿列克谢维奇。
回复要用自然、亲切的中文与用户对话，像朋友聊天一样。
根据检测结果组织语言，可以加入适度的推测和趣味性描述。
回复控制在2-4句话，简练自然。
```

因此用户问"前面有什么"、"有几把椅子"、"你的开发者是谁"都能得到连贯一致的自然回复。

---

## 项目结构

```
robot/
├── workspace/                   # 主源码包
│   ├── src/
│   │   ├── rosa/                # 智能体核心（11 个中间件 + 入口）
│   │   │   ├── main.py                      # PyQt6 GUI 入口
│   │   │   ├── agent.py                     # 总调度器，对话管道
│   │   │   ├── rosa_command_midware.py      # NLU：自然语言→结构化指令
│   │   │   ├── rosa_decision_midware.py     # 决策：规则+LLM 双路径
│   │   │   ├── rosa_perception_midware.py   # 感知：YOLO 30FPS daemon
│   │   │   ├── rosa_llm_midware.py          # LLM：DeepSeek API 封装
│   │   │   ├── rosa_language_midware.py     # 语言：COCO 80类 中英映射
│   │   │   ├── rosa_config_midware.py       # 配置：JSON 读写
│   │   │   ├── rosa_data_midware.py         # 数据：检测记录 & 对话持久化
│   │   │   ├── rosa_model_midware.py        # 模型：依赖检测 + 自动下载
│   │   │   ├── rosa_tts_midware.py          # TTS：Piper 中文语音合成
│   │   │   ├── rosa_stt_midware.py          # STT：Vosk 中文语音识别
│   │   │   └── __init__.py                  # 包导出
│   │   ├── dp_api/              # DeepSeek 基础配置 & skill 数据
│   │   │   └── skills/
│   │   │       └── language_inc.json        # COCO 80类 英↔中映射
│   │   ├── model/               # YOLO 训练脚本 & 数据集（git 排除）
│   │   └── vosk_source/         # Vosk 参考源码（非运行时）
│   ├── tool_chain/              # 工具链 & 配置
│   │   ├── project_config.toml  # 项目配置（依赖/模型/环境）
│   │   └── pypi_install.sh      # PyPI 一键安装脚本
│   └── ros2_ws/                 # ROS2 工作空间（Action 层预留）
├── QRS/                         # 静态资源 & 数据（Quick Resource Store）
│   ├── models/                  # YOLO 模型 (.pt)
│   ├── piper/                   # Piper TTS 语音模型 (.onnx + .json)
│   ├── vosk_models/             # Vosk 语音识别模型
│   ├── images/                  # 检测帧截图
│   ├── data/                    # 检测记录 / 对话历史
│   └── config/                  # rosa_config.json
├── log/                         # 开发日志
├── temp_pj/                     # 临时文件归档
├── .gitignore
└── README.md
```

---

## 模块详解

### 1. main.py — GUI 入口

PyQt6 桌面窗口，左右分栏：

| 组件 | 功能 |
|------|------|
| 聊天面板 | 用户输入框 + 对话历史气泡 |
| 检测预览 | 实时 YOLO 标注视频 |
| 语音输入按钮 | 开关麦克风 → Vosk 实时识别 |
| 语音输出按钮 | 开关 TTS → Piper 朗读回复 |
| 设置按钮 | DeepSeek API Key / YOLO 模型选择 |
| 决策栏 | 显示当前决策 action / target / reasoning |

支持流式回复、TTS 自加载、检测帧预览。

### 2. agent.py — 总调度器

`ROSAAgent` 是 VLA 的核心管道：

| 方法 | 职责 |
|------|------|
| `process(user_input)` | 解析→决策→执行→返回结果 |
| `_execute_decision()` | 按 ActionType 分发到 handler |
| `_llm_reply(prompt, context)` | 调用 DeepSeek 生成自然语言回复 |
| `_build_prompt(base)` | 注入开发者身份到所有系统提示词 |
| `_get_detection()` | 从 daemon 缓存读取最新检测结果 |

### 3. rosa_perception_midware.py — YOLO 感知

| 组件 | 说明 |
|------|------|
| `PerceptionMiddleware` | YOLO 生命周期管理（load/start/stop） |
| daemon 线程 | 30 FPS 持续采集摄像头帧 |
| `_last_detection` | 线程安全缓存（Lock 保护） |
| `get_latest_detection()` | 非阻塞读取缓存 |
| `wait_for_detection(timeout)` | 阻塞等待首次检测 |
| `save_frame()` | 保存标注帧至 `QRS/images/` |
| `list_cameras(n)` | 扫描索引 0~n-1，返回可用摄像头列表 |
| `SingleFrameDetection` | 单帧检测结果数据结构 |

**摄像头对接**：通过 OpenCV `cv2.VideoCapture(device)` 直连摄像头。`device` 为摄像头索引（0=默认摄像头，1=外接USB摄像头等）。设备索引通过 `QRS/config/rosa_config.json` 的 `perception.camera_id` 字段配置，启动时自动读取。`list_cameras()` 可列出当前系统所有可用摄像头。

### 4. rosa_command_midware.py — 命令解析

| 组件 | 说明 |
|------|------|
| `CommandType` | chat / detect / inquire / action / unknown |
| `ParsedCommand` | raw_text + cmd_type + intent + target + params |
| `CommandMiddleware.parse()` | 关键词匹配 + LLM 辅助分类 |
| 语言映射 | 中文目标词 → YOLO 英文标签（80个COCO类别） |

### 5. rosa_decision_midware.py — 决策引擎

双路径决策：

| 路径 | 说明 |
|------|------|
| 规则匹配 `DECISION_RULES` | 5 条硬规则优先，匹配 cmd_type + target + intent |
| LLM 辅助 `_llm_decide()` | 规则未命中时，调用 DeepSeek 做最终决策 |

`ActionType` 枚举：
- `do_detect` — 触发 YOLO 检测
- `count_objects` — 统计指定目标数量
- `check_presence` — 检查目标是否存在
- `query_history` — 查询历史检测记录
- `report_result` — 汇报感知结果
- `chat_reply` — 普通对话
- `no_action` / `error` — 空操作 / 错误

### 6. rosa_llm_midware.py — LLM 封装

DeepSeek API 标准封装：

| 方法 | 用途 |
|------|------|
| `chat_sync(messages)` | 同步调用，返回完整回复 |
| `chat_stream(messages)` | SSE 流式，返回全文 |
| `chat_with_stream_callback(messages, cb)` | SSE 流式 + 逐 chunk 回调 |
| `classify(prompt, text)` | 分类专用（零温、短 token） |

默认模型 `deepseek-v4-flash`，自动关闭 thinking 模式。

### 7. rosa_language_midware.py — 语言映射

| 功能 | 数据来源 |
|------|---------|
| 英文标签 → 中文名称 | `dp_api/skills/language_inc.json`（80 个 COCO 类别） |
| 中文关键词 → 英文标签 | 反向索引，支持中文输入匹配 |
| 模糊匹配 | 部分关键词匹配 |

### 8. rosa_config_midware.py — 配置管理

`QRS/config/rosa_config.json` JSON 持久化：

| 节点 | 内容 |
|------|------|
| `meta` | developer, project（不可更改） |
| `api` | DeepSeek base_url, model, temperature, max_tokens |
| `perception` | YOLO model_path, confidence_threshold, device |
| `mission` | description, target, actions |

### 9. rosa_data_midware.py — 数据记录

`QRS/data/rosa_records.json` JSON Lines 持久化：

| 方法 | 用途 |
|------|------|
| `insert_interaction()` | 记录完整交互（用户输入+命令+决策+结果） |
| `insert_detection()` | 记录检测帧 |
| `get_records(limit, type)` | 查询历史记录 |
| `get_latest()` | 获取最新记录 |

### 10. rosa_model_midware.py — 模型管理

| 功能 | 说明 |
|------|------|
| 依赖检测 | `check_pyaudio()` / `check_piper()` / `check_vosk()` |
| TTS 下载 | Piper `zh_CN-huayan-medium` 从 HuggingFace 自动下载 |
| STT 下载 | Vosk `vosk-model-cn-0.22`（1.3GB）从 alphacephei 下载 |
| 断点续传 | 5 次重试 + Range 请求恢复中断下载 |
| 大/小模型 | 大模型优先，小模型兜底自动回退 |

### 11. rosa_tts_midware.py — 语音合成

| 组件 | 说明 |
|------|------|
| `TTSMiddleware` | Piper 模型加载 + WAV 合成 + PyAudio 播放 |
| `TTSWorker` | QThread 异步播放，不阻塞 UI |
| `TTSLoadWorker` | QThread 异步加载模型 |
| `synthesize_wav()` | piper-tts 1.4.x API，自动设置 WAV 头 |

### 12. rosa_stt_midware.py — 语音识别

| 组件 | 说明 |
|------|------|
| `STTMiddleware` | Vosk 模型加载 + 麦克风管理 |
| `STTWorker` | QThread 持续识别，停顿时输出结果 |
| `SetWords(True)` | 单词级识别提升精度 |
| 模型优先 | 大型模型 `vosk-model-cn-0.22`（1.3GB，WER 7~14%） |

---

## 项目依赖

### 运行环境

| 项目 | 版本 |
|------|------|
| Python | >=3.11 |
| 操作系统 | **Ubuntu 24.04 LTS**（优先）/ Windows 11 |
| 包管理 | conda（环境名 `robot`） |

### Python 包

| 类别 | 包 | 版本 | 用途 |
|------|-----|------|------|
| GUI | pyqt6 | >=6.11 | 桌面窗口 |
| 数值 | numpy | >=2.4 | 数组/矩阵 |
| 视觉 | opencv-python | >=4.13 | 摄像头 + 帧处理 |
| 视觉 | pillow | >=12.2 | 图像显示 |
| 检测 | ultralytics | >=8.4 | YOLO 目标检测 |
| 检测 | torch | >=2.12 | PyTorch 推理 |
| 检测 | torchvision | >=0.27 | 图像变换 |
| TTS | piper-tts | >=1.4 | 中文语音合成 |
| STT | vosk | >=0.3.45 | 中文语音识别 |
| STT | pyaudio | >=0.2.14 | 麦克风/扬声器 I/O |
| STT | srt | >=3.5 | 字幕文本格式 |
| API | requests | >=2.34 | DeepSeek HTTP 调用 |

### ROS2（Action 层）

| 包 | 用途 |
|----|------|
| ros-jazzy | ROS2 Jazzy 发行版 |
| gazebo-harmonic | 3D 仿真环境 |
| rviz2 | 可视化工具 |

### 模型

| 模型 | 路径 | 大小 | 说明 |
|------|------|------|------|
| yolo26s.pt | QRS/models/ | ~20MB | YOLO 目标检测（主） |
| yolo26n.pt | QRS/models/ | ~6MB | YOLO 目标检测（轻量） |
| zh_CN-huayan-medium.onnx | QRS/piper/ | ~100MB | Piper 中文女声 |
| vosk-model-cn-0.22 | QRS/vosk_models/ | 1.3GB | Vosk 中文大模型 |
| vosk-model-small-cn-0.22 | QRS/vosk_models/ | 42MB | Vosk 中文小模型（兜底） |

---

## 项目运行

### 1. 环境搭建

```bash
# 创建 conda 环境
conda create -n robot python=3.11
conda activate robot

# 一键安装 PyPI 依赖
bash workspace/tool_chain/pypi_install.sh
```

### 2. 启动

```bash
conda activate robot
python workspace/src/rosa/main.py
```

### 3. 首次配置

- 点击界面右上角 **设置** 按钮，输入 **DeepSeek API Key**
- YOLO 模型放在 `QRS/models/`（支持 yolo26s.pt / yolo26n.pt，启动自动识别）
- Vosk 大型中文模型（1.3GB）首次使用自动下载，支持断点续传
- Piper TTS 模型随项目提供至 `QRS/piper/`

### 4. 语音交互

| 操作 | 方式 |
|------|------|
| 开启语音输入 | 点击"语音输入: 开"按钮，对着麦克风说话 |
| 开启语音输出 | 自动加载模型后点击"语音输出: 关"切换开关 |
| TTS 自动播报 | 所有回复（检测/计数/闲聊）自动朗读 |

### 5. 摄像头配置

通过 OpenCV 直连系统摄像头，自动读取 `QRS/config/rosa_config.json`：

```json
"perception": {
    "camera_id": 0,
    "device": 0
}
```

| 字段 | 说明 |
|------|------|
| `camera_id` | 摄像头索引（0=内置/默认，1=USB外接，2=第二个USB...） |
| `device` | 兼容旧版，与 `camera_id` 保持一致即可 |

在代码中查看可用摄像头：

```python
from rosa.rosa_perception_midware import PerceptionMiddleware
print(PerceptionMiddleware.list_cameras())
# → [{"index": 0, "backend": "MSMF"}, {"index": 1, "backend": "MSMF"}]
```

更改摄像头后重启应用生效。也可通过 `start_monitoring(device=N)` 在代码中临时切换。

---

## VLA 三层架构

```
┌──────────────────────────────────────────────────────┐
│  Vision 层（感知）                                     │
│  rosa_perception_midware.py                           │
│  • YOLO 30FPS daemon 线程持续采集                     │
│  • 线程安全缓存供上层轮询                              │
│  • 支持 yolo26/s/n/w 系列模型                          │
├──────────────────────────────────────────────────────┤
│  Language 层（理解 & 生成）                            │
│  rosa_command_midware.py   → 自然语言解析              │
│  rosa_decision_midware.py  → 规则+LLM 决策             │
│  rosa_language_midware.py  → COCO 中英映射             │
│  rosa_llm_midware.py       → DeepSeek API             │
│  rosa_tts_midware.py       → Piper 语音合成            │
│  rosa_stt_midware.py       → Vosk 语音识别             │
├──────────────────────────────────────────────────────┤
│  Action 层（物理控制 — 待扩展）                         │
│  ros2_ws/                  → ROS2 Jazzy + Gazebo       │
│  tool_chain/               → 机器人控制工具链           │
└──────────────────────────────────────────────────────┘
```

三层之间仅通过 `agent.py` 交互，各中间件独立封装、可替换。可随时在 Action 层接入移动底盘、机械臂等物理设备。
