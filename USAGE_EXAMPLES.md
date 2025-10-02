# YouTube Chat Downloader - 使用示例

本文档提供详细的中文使用示例。

## 安装

```bash
# 克隆仓库
git clone https://github.com/litong-2017/youtube-chat-downloader.git
cd youtube-chat-downloader

# 使用 uv 安装依赖
uv sync
```

## 基础使用

### 1. 下载单个频道的所有历史直播聊天

```bash
# Windows
ytchat.bat download @频道名

# Linux/Mac
./ytchat.sh download @频道名

# 或直接使用 Python
source .venv/Scripts/activate  # Windows: .venv/Scripts/activate
python -m youtube_chat_downloader.cli.commands download @频道名
```

### 2. 验证频道是否存在

在下载前，建议先验证频道：

```bash
python -m youtube_chat_downloader.cli.commands validate @频道名
```

这将显示：
- 频道名称
- 频道 ID
- 频道 URL
- 最近的直播视频列表（前5个）

### 3. 增量下载（推荐）

默认情况下，工具会跳过已下载的视频（增量模式）：

```bash
# 只下载新的视频
python -m youtube_chat_downloader.cli.commands download @频道名 --skip-existing
```

如果需要重新下载所有视频：

```bash
# 重新下载所有视频（会覆盖现有数据）
python -m youtube_chat_downloader.cli.commands download @频道名 --no-skip-existing
```

## 高级过滤选项

### 按日期范围下载

下载特定时间段的直播：

```bash
# 下载2024年的所有直播
python -m youtube_chat_downloader.cli.commands download @频道名 \
    --start-date 2024-01-01 \
    --end-date 2024-12-31

# 下载2024年1月到3月的直播
python -m youtube_chat_downloader.cli.commands download @频道名 \
    --start-date 2024-01-01 \
    --end-date 2024-03-31
```

### 按索引范围下载

下载视频列表中的特定范围：

```bash
# 下载前50个视频（索引 0-49）
python -m youtube_chat_downloader.cli.commands download @频道名 \
    --start-index 0 \
    --end-index 50

# 下载第51到100个视频
python -m youtube_chat_downloader.cli.commands download @频道名 \
    --start-index 50 \
    --end-index 100
```

### 限制下载数量

```bash
# 只下载最新的10个视频
python -m youtube_chat_downloader.cli.commands download @频道名 --max-videos 10

# 只下载最新的50个视频
python -m youtube_chat_downloader.cli.commands download @频道名 --max-videos 50
```

### 组合使用多个过滤器

```bash
# 下载2024年的前20个视频
python -m youtube_chat_downloader.cli.commands download @频道名 \
    --start-date 2024-01-01 \
    --end-date 2024-12-31 \
    --max-videos 20

# 下载索引10-30之间，且在2024年的视频
python -m youtube_chat_downloader.cli.commands download @频道名 \
    --start-index 10 \
    --end-index 30 \
    --start-date 2024-01-01 \
    --end-date 2024-12-31
```

## 数据库管理

### 指定自定义数据库路径

```bash
# 为不同频道使用不同的数据库
python -m youtube_chat_downloader.cli.commands download @频道1 \
    --db-path data/channel1.db

python -m youtube_chat_downloader.cli.commands download @频道2 \
    --db-path data/channel2.db
```

### 查看已下载的视频

```bash
# 查看默认数据库中的视频
python -m youtube_chat_downloader.cli.commands list-videos

# 查看指定数据库中的视频
python -m youtube_chat_downloader.cli.commands list-videos --db-path data/channel1.db
```

## 数据分析

### 查看统计信息

```bash
# 显示数据库统计信息
python -m youtube_chat_downloader.cli.commands analyze

# 显示内容：
# - 总视频数
# - 总消息数
# - 消息最多的前5个视频
# - 最活跃的前10个用户
```

### 导出数据到CSV

```bash
# 导出所有数据
python -m youtube_chat_downloader.cli.commands export --output all_chats.csv

# 导出特定视频的聊天记录
python -m youtube_chat_downloader.cli.commands export \
    --video-id VIDEO_ID \
    --output video_chat.csv

# 导出到自定义路径
python -m youtube_chat_downloader.cli.commands export \
    --output exports/chat_$(date +%Y%m%d).csv
```

## 实际应用场景

### 场景1：定期更新多个频道的数据

创建一个批处理脚本 `update_all.sh`：

```bash
#!/bin/bash
# 每天运行此脚本，更新所有关注的频道

CHANNELS=(
    "@channel1"
    "@channel2"
    "@channel3"
)

for channel in "${CHANNELS[@]}"; do
    echo "Updating $channel..."
    python -m youtube_chat_downloader.cli.commands download "$channel" \
        --skip-existing \
        --db-path "data/${channel//[@\/]/_}.db"
    echo "Done: $channel"
    echo "---"
done

echo "All channels updated!"
```

### 场景2：下载特定时期的历史数据

```bash
# 下载2023年全年的数据
python -m youtube_chat_downloader.cli.commands download @频道名 \
    --start-date 2023-01-01 \
    --end-date 2023-12-31 \
    --db-path data/channel_2023.db

# 下载2024年全年的数据
python -m youtube_chat_downloader.cli.commands download @频道名 \
    --start-date 2024-01-01 \
    --end-date 2024-12-31 \
    --db-path data/channel_2024.db
```

### 场景3：批量处理和分析

```bash
# 1. 下载数据
python -m youtube_chat_downloader.cli.commands download @频道名 --max-videos 100

# 2. 查看统计
python -m youtube_chat_downloader.cli.commands analyze

# 3. 导出数据用于进一步分析
python -m youtube_chat_downloader.cli.commands export --output analysis_data.csv
```

### 场景4：处理大型频道（分批下载）

对于视频数量非常多的频道，建议分批下载：

```bash
# 第一批：视频 0-100
python -m youtube_chat_downloader.cli.commands download @大型频道 \
    --start-index 0 \
    --end-index 100

# 第二批：视频 100-200
python -m youtube_chat_downloader.cli.commands download @大型频道 \
    --start-index 100 \
    --end-index 200

# 第三批：视频 200-300
python -m youtube_chat_downloader.cli.commands download @大型频道 \
    --start-index 200 \
    --end-index 300
```

## 使用Python进行数据分析

下载完成后，可以使用Python直接分析数据库：

```python
import sqlite3
import pandas as pd

# 连接数据库
conn = sqlite3.connect('data/youtube_chat.db')

# 查询所有消息
df = pd.read_sql_query("""
    SELECT
        cm.*,
        v.title as video_title,
        v.channel_name,
        v.upload_date
    FROM chat_messages cm
    JOIN videos v ON cm.video_id = v.video_id
""", conn)

print(f"总消息数: {len(df)}")

# 分析最活跃的用户
top_users = df['author_name'].value_counts().head(10)
print("\n最活跃用户Top 10:")
print(top_users)

# 分析Super Chat
superchats = df[df['superchat_amount'].notna()]
print(f"\nSuper Chat总数: {len(superchats)}")
print(f"Super Chat总金额: ${superchats['superchat_amount'].sum():.2f}")

# 按视频统计消息数
messages_per_video = df.groupby('video_id').size().sort_values(ascending=False)
print("\n消息最多的视频Top 5:")
print(messages_per_video.head())

# 时间分析（如果timestamp_usec可用）
df['timestamp'] = pd.to_datetime(df['timestamp_usec'], unit='us')
df['hour'] = df['timestamp'].dt.hour
hourly_distribution = df['hour'].value_counts().sort_index()
print("\n按小时统计的消息分布:")
print(hourly_distribution)

conn.close()
```

## 故障排查

### 问题1：找不到频道

```bash
# 尝试使用不同格式
python -m youtube_chat_downloader.cli.commands validate @频道名
python -m youtube_chat_downloader.cli.commands validate 频道名
python -m youtube_chat_downloader.cli.commands validate UC开头的频道ID
```

### 问题2：没有找到聊天消息

某些情况下视频可能没有聊天记录：
- 视频太旧，聊天回放已过期
- 视频未启用聊天功能
- 视频是会员专属

使用 `--search-mode` 标志尝试其他查找方式：

```bash
python -m youtube_chat_downloader.cli.commands download @频道名 --search-mode
```

### 问题3：速率限制

工具自动在每个视频之间添加2秒延迟。如果仍然遇到问题：

```bash
# 分批下载，每批之间手动等待
python -m youtube_chat_downloader.cli.commands download @频道名 \
    --start-index 0 \
    --end-index 50

# 等待几分钟后继续
sleep 300

python -m youtube_chat_downloader.cli.commands download @频道名 \
    --start-index 50 \
    --end-index 100
```

## 最佳实践

1. **首次下载大型频道**：
   - 使用 `--max-videos` 限制数量
   - 或使用索引范围分批下载

2. **定期更新**：
   - 使用 `--skip-existing` 进行增量更新
   - 设置定时任务（cron/计划任务）

3. **数据备份**：
   - 定期备份 `data/` 目录
   - 导出重要数据到CSV

4. **性能优化**：
   - 对大型数据库，考虑添加额外的索引
   - 定期清理不需要的旧数据

## 命令速查表

```bash
# 验证频道
validate @频道名

# 下载（默认增量）
download @频道名

# 下载前10个
download @频道名 --max-videos 10

# 按日期下载
download @频道名 --start-date 2024-01-01 --end-date 2024-12-31

# 按索引下载
download @频道名 --start-index 0 --end-index 50

# 强制重新下载
download @频道名 --no-skip-existing

# 查看统计
analyze

# 列出视频
list-videos

# 导出数据
export --output data.csv
export --video-id VIDEO_ID --output video.csv
```
