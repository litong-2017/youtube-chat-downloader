# YouTube Chat Downloader - Quick Reference Card

## 快速开始 (Quick Start)

```bash
# 1. 安装 (Install)
uv sync

# 2. 激活环境 (Activate)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. 下载聊天记录 (Download)
python -m youtube_chat_downloader.cli.commands download @channelname
```

## 命令速查 (Command Reference)

### 基础命令 (Basic Commands)

| 命令 | 说明 | 示例 |
|------|------|------|
| `download` | 下载聊天记录 | `download @channel` |
| `validate` | 验证频道 | `validate @channel` |
| `analyze` | 分析数据 | `analyze` |
| `export` | 导出CSV | `export --output data.csv` |
| `list-videos` | 列出视频 | `list-videos` |

### Download 命令选项 (Download Options)

| 选项 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--max-videos` | `-m` | 最大视频数 | `--max-videos 10` |
| `--db-path` | `-d` | 数据库路径 | `--db-path data/my.db` |
| `--search-mode` | `-s` | 搜索模式 | `--search-mode` |
| `--skip-existing` | - | 跳过已下载 (默认) | `--skip-existing` |
| `--no-skip-existing` | - | 重新下载 | `--no-skip-existing` |
| `--start-date` | - | 开始日期 | `--start-date 2024-01-01` |
| `--end-date` | - | 结束日期 | `--end-date 2024-12-31` |
| `--start-index` | - | 开始索引 | `--start-index 0` |
| `--end-index` | - | 结束索引 | `--end-index 50` |

## 常用场景 (Common Scenarios)

### 1. 首次完整下载 (First-time Download)
```bash
python -m youtube_chat_downloader.cli.commands download @channel
```

### 2. 增量更新 (Incremental Update)
```bash
# 默认行为，跳过已下载
python -m youtube_chat_downloader.cli.commands download @channel
```

### 3. 按日期下载 (Date Range)
```bash
# 下载2024年的视频
python -m youtube_chat_downloader.cli.commands download @channel \
    --start-date 2024-01-01 --end-date 2024-12-31
```

### 4. 分批下载 (Batch Download)
```bash
# 第一批: 0-100
python -m youtube_chat_downloader.cli.commands download @channel \
    --start-index 0 --end-index 100

# 第二批: 100-200
python -m youtube_chat_downloader.cli.commands download @channel \
    --start-index 100 --end-index 200
```

### 5. 限量测试 (Limited Test)
```bash
# 只下载最新5个视频测试
python -m youtube_chat_downloader.cli.commands download @channel \
    --max-videos 5
```

### 6. 验证后下载 (Validate then Download)
```bash
# 先验证
python -m youtube_chat_downloader.cli.commands validate @channel

# 确认后下载
python -m youtube_chat_downloader.cli.commands download @channel
```

### 7. 查看和导出 (View and Export)
```bash
# 查看统计
python -m youtube_chat_downloader.cli.commands analyze

# 列出视频
python -m youtube_chat_downloader.cli.commands list-videos

# 导出数据
python -m youtube_chat_downloader.cli.commands export --output data.csv
```

## 过滤器组合 (Filter Combinations)

```bash
# 组合1: 日期 + 数量限制
download @channel --start-date 2024-01-01 --max-videos 20

# 组合2: 索引 + 日期
download @channel --start-index 10 --end-index 50 --start-date 2024-01-01

# 组合3: 所有过滤器
download @channel \
    --start-date 2024-01-01 \
    --end-date 2024-06-30 \
    --start-index 0 \
    --end-index 100 \
    --max-videos 50 \
    --skip-existing
```

## 数据库操作 (Database Operations)

```bash
# 默认数据库: data/youtube_chat.db
# 查看数据
python -m youtube_chat_downloader.cli.commands list-videos

# 使用自定义数据库
python -m youtube_chat_downloader.cli.commands download @channel \
    --db-path custom.db

python -m youtube_chat_downloader.cli.commands analyze --db-path custom.db
```

## 启动脚本 (Launcher Scripts)

### Windows
```cmd
ytchat.bat download @channel
ytchat.bat validate @channel
ytchat.bat analyze
```

### Linux/Mac
```bash
./ytchat.sh download @channel
./ytchat.sh validate @channel
./ytchat.sh analyze
```

## Python API 使用 (Python API)

```python
from youtube_chat_downloader.core.downloader import YouTubeChatDownloader
from youtube_chat_downloader.core.analyzer import ChatAnalyzer

# 下载
downloader = YouTubeChatDownloader(db_path="data/my.db")
downloader.download_channel_chat_history(
    channel_id="@channel",
    max_videos=10,
    skip_existing=True,
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# 分析
analyzer = ChatAnalyzer(db_path="data/my.db")
stats = analyzer.get_statistics()
top_chatters = analyzer.get_top_chatters(limit=10)
analyzer.export_to_csv(output_file="export.csv")
```

## 故障排查 (Troubleshooting)

| 问题 | 解决方案 |
|------|----------|
| 找不到频道 | 尝试 `@channel`, `channel`, `UC...` 格式 |
| 没有聊天记录 | 使用 `--search-mode` 标志 |
| 速率限制 | 使用索引范围分批下载 |
| 数据库锁定 | 确保只有一个进程访问数据库 |

## 性能提示 (Performance Tips)

1. **大型频道**: 使用 `--start-index` 和 `--end-index` 分批下载
2. **定期更新**: 使用 `--skip-existing` (默认启用)
3. **测试先行**: 先用 `--max-videos 5` 测试
4. **并行处理**: 不同频道使用不同数据库可并行运行

## 文件结构 (File Structure)

```
youtube-chat-downloader/
├── data/                    # 数据库文件夹
│   └── youtube_chat.db     # 默认数据库
├── examples/               # 示例代码
│   └── example_usage.py   # Python API 示例
├── src/                    # 源代码
├── ytchat.bat             # Windows 启动脚本
├── ytchat.sh              # Linux/Mac 启动脚本
├── README.md              # 英文文档
├── USAGE_EXAMPLES.md      # 中文详细示例
└── QUICK_REFERENCE.md     # 本文件
```

## 数据库表结构 (Database Schema)

### videos 表
- `video_id` (主键)
- `title`, `upload_date`, `duration`
- `channel_id`, `channel_name`
- `is_live`, `was_live`

### chat_messages 表
- `id` (主键)
- `video_id`, `message_id`
- `author_name`, `author_id`, `message`
- `timestamp_usec`, `message_type`
- `superchat_amount`, `superchat_currency`

## 获取帮助 (Get Help)

```bash
# 查看命令帮助
python -m youtube_chat_downloader.cli.commands --help
python -m youtube_chat_downloader.cli.commands download --help
python -m youtube_chat_downloader.cli.commands validate --help
```

## 相关文档 (Related Documentation)

- `README.md` - 完整英文文档
- `USAGE_EXAMPLES.md` - 详细中文使用示例
- `CLAUDE.md` - 代码架构说明
- `PROJECT_SUMMARY.md` - 项目功能总结
- `examples/example_usage.py` - Python API 示例

---

**提示**: 替换 `@channel` 为实际的YouTube频道名或ID
