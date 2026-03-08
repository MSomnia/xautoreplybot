# X Auto Reply Bot

一个基于 Python + X API v2 + Grok 的自动评论机器人。它在你手动触发 GitHub Actions 时读取主账号新推文，并使用 Bot 账号生成风格化回复。

## 功能

- 拉取主账号新推文（增量，基于 `since_id`）
- 通过 Grok 生成评论
- 进行内容过滤（长度、敏感词、重复度）
- 使用 Bot 账号回复原推文
- `state.json` 持久化运行状态，配合 GitHub Actions Artifact 跨运行保存

## 项目结构

- `main.py`：主入口（单次运行）
- `config.py`：环境变量与配置
- `fetcher.py`：读取新推文
- `generator.py`：生成回复
- `filter.py`：审核回复
- `replier.py`：发送回复
- `state.py`：状态读写
- `.github/workflows/reply-bot.yml`：手动触发工作流

## 环境变量

请在 GitHub Actions Secrets 中配置：

- `X_MAIN_USER_ID`
- `X_API_KEY`
- `X_API_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`
- `X_BEARER_TOKEN`
- `GROK_API_KEY`
- `BOT_SYSTEM_PROMPT`

可选环境变量：

- `GROK_MODEL`（默认 `grok-4.1`）
- `GROK_BASE_URL`（默认 `https://api.x.ai/v1`）

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 注意事项

- 仓库中不保存系统提示词；请始终通过 `BOT_SYSTEM_PROMPT` 注入。
- 初次运行 `state.json` 可保持默认空状态。
- 当前仅支持 `workflow_dispatch` 手动触发，不启用定时轮询。
