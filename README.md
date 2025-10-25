# LiveRecorder

📺 多平台直播录制工具 - 支持命令行和Web界面两种模式

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ 特性

- 🎯 **多平台支持**: Bilibili, Douyu, Huya, Douyin, YouTube, Twitch 等 13+ 平台
- 🖥️ **双运行模式**: 命令行模式 / Web界面模式
- 🔄 **自动录制**: 检测直播状态，自动开始/停止录制
- 🌐 **Web管理**: 现代化的Web界面，实时监控录制状态
- ⚙️ **灵活配置**: 支持代理、格式转换、自定义参数
- 📝 **完善日志**: 详细的录制日志和错误提示

## 🎬 支持的平台

| 平台 | 状态 | 平台 | 状态 |
|------|------|------|------|
| Bilibili | ✅ | YouTube | ✅ |
| Douyu | ✅ | Twitch | ✅ |
| Huya | ✅ | Niconico | ✅ |
| Douyin | ✅ | Twitcasting | ✅ |
| Afreeca | ✅ | Pandalive | ✅ |
| Bigolive | ✅ | Pixivsketch | ✅ |
| Chaturbate | ✅ | | |

## 📦 快速开始

### 1. 安装依赖

```bash
# 运行安装脚本（自动创建虚拟环境并安装依赖）
./scripts/install.sh
```

### 2. 配置文件

**命令行模式** 使用 `config.json`:
```bash
cp config.sample.json config.json
# 编辑 config.json 添加主播信息
```

**Web模式** 通过Web界面配置，会自动创建 `web_config.json`

### 3. 启动程序

#### 命令行模式

```bash
# 使用脚本启动
./scripts/start.sh

# 或直接运行
python app.py --mode cli
```

#### Web界面模式

```bash
# 使用脚本启动
./scripts/start_web.sh

# 或直接运行
python app.py --mode web

# 访问 http://localhost:8888
```

## 📁 项目结构

```
LiveRecorder/
├── app.py                      # 统一启动入口
├── src/                        # 核心代码
│   ├── recorder.py
│   ├── config.py
│   ├── web_api.py
│   ├── platforms/              # 13个平台
│   └── utils/                  # 工具模块
├── scripts/                    # 脚本工具
├── web/                        # Web前端
├── output/                     # 录制文件
└── logs/                       # 日志文件
```

详细说明请查看 [STRUCTURE.md](STRUCTURE.md)

## 📄 许可证

本项目基于 MIT 许可证开源 - 详见 [LICENSE](LICENSE) 文件

---

💡 提示：首次使用建议使用Web模式，更直观易用！
