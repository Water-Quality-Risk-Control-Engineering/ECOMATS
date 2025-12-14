# Windows 兼容性指南 / Windows Compatibility Guide

## 已知问题 / Known Issues

### 1. signal.SIGHUP AttributeError

**问题描述 / Problem Description:**
```
AttributeError: module 'signal' has no attribute 'SIGHUP'
```

**原因 / Root Cause:**
- `signal.SIGHUP` 是 Unix/Linux 专有信号，Windows 系统不支持
- CrewAI 1.7.0 的某些依赖库（如 `chromadb` 或 `opentelemetry`）可能在初始化时尝试使用此信号
- Windows only supports limited signals: `SIGABRT`, `SIGFPE`, `SIGILL`, `SIGINT`, `SIGSEGV`, `SIGTERM`

**解决方案 / Solutions:**

#### 方案 1: 使用 WSL2 (推荐 / Recommended)
在 Windows 上安装 WSL2 (Windows Subsystem for Linux) 并在 Linux 环境中运行项目：

```bash
# 安装 WSL2
wsl --install

# 在 WSL2 Ubuntu 中安装项目
cd /path/to/ECOMATS
pip install -r requirements.txt
python scripts/main_async.py
```

**优势**：
- ✅ 完全兼容所有 Unix 信号
- ✅ 与 Linux 生产环境一致
- ✅ 性能接近原生 Linux

#### 方案 2: 修改依赖库代码
如果必须在原生 Windows 上运行，需要 patch 依赖库：

```python
# 在项目入口添加 monkey patch
import signal
import sys

if sys.platform == 'win32':
    # Windows 不支持 SIGHUP，创建一个占位符
    if not hasattr(signal, 'SIGHUP'):
        signal.SIGHUP = None
```

**位置**：在 `scripts/main.py` 和 `scripts/main_async.py` 文件顶部添加

#### 方案 3: 使用虚拟化
使用 Docker Desktop for Windows：

```dockerfile
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "scripts/main_async.py"]
```

### 2. 路径分隔符差异

**问题**：Windows 使用 `\`，Linux 使用 `/`

**解决方案**：项目已使用 `os.path.join()` 和 `pathlib.Path`，应该兼容

### 3. 编码问题

**问题**：Windows 默认使用 GBK/CP936 编码，可能导致中文乱码

**解决方案**：
```python
# 在脚本开头添加
import sys
import locale

# 设置默认编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
```

---

## 环境要求 / Environment Requirements

### Windows 系统 / Windows Platform
- Windows 10/11 (64-bit)
- Python 3.10-3.12
- 推荐使用 Anaconda/Miniconda

### WSL2 (推荐 / Recommended)
- WSL2 with Ubuntu 20.04/22.04
- Python 3.10+
- 完全兼容，无需额外配置

---

## 测试状态 / Test Status

| 功能 / Feature | Windows Native | WSL2 | Linux |
|---------------|---------------|------|-------|
| 同步模式 / Sync Mode | ⚠️ 需要 patch | ✅ | ✅ |
| 异步模式 / Async Mode | ⚠️ 需要 patch | ✅ | ✅ |
| 工具调用 / Tool Calling | ✅ | ✅ | ✅ |
| API 连接 / API Connectivity | ✅ | ✅ | ✅ |
| 文件 I/O | ✅ | ✅ | ✅ |

**图例**：
- ✅ 完全支持
- ⚠️ 需要额外配置
- ❌ 不支持

---

## 推荐配置 / Recommended Setup

### 最佳方案：WSL2 + VS Code
1. 安装 WSL2 和 Ubuntu
2. 安装 VS Code 和 WSL 扩展
3. 在 WSL 环境中打开项目
4. 使用 WSL 终端运行

**优势**：
- 完美兼容 Linux 环境
- 与生产环境一致
- 无需任何 patch

### 备选方案：Windows + Patch
仅当无法使用 WSL2 时考虑：
1. 应用 monkey patch（见方案 2）
2. 测试所有功能
3. 注意编码问题

---

## 常见问题 / FAQ

**Q: 为什么会有 SIGHUP 问题？**
A: CrewAI 依赖的某些库（如 chromadb）在初始化时注册信号处理器，Windows 不支持 Unix 信号。

**Q: 是否影响核心功能？**
A: 不影响。SIGHUP 主要用于日志轮转和优雅重启，对材料设计功能无影响。

**Q: 生产环境建议？**
A: 强烈建议使用 Linux 服务器或 WSL2，避免 Windows 特有问题。

**Q: 是否有官方修复计划？**
A: 这是上游依赖库的问题，等待 CrewAI 或 chromadb 官方修复。

---

## 相关资源 / Related Resources

- [WSL2 安装指南](https://docs.microsoft.com/en-us/windows/wsl/install)
- [Python signal 模块文档](https://docs.python.org/3/library/signal.html)
- [CrewAI GitHub Issues](https://github.com/crewAIInc/crewAI/issues)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)

---

**最后更新 / Last Updated**: 2025-12-14  
**状态 / Status**: 已知问题，有解决方案 / Known Issue with Workarounds
