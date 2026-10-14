# 自动化测试

改业务代码后的回归入口。给 Agent 看；不改 README。

## 命令

仓库根：

```bash
# 一次性装后端测试依赖（已有 .venv 时）
.venv/bin/pip install -r stockManager/requirements-dev.txt

# 全量（无 Redis、无外网）
./scripts/test.sh

# 仅当 backend / front/src / tests 有改动时跑全量
./scripts/test.sh --if-dirty
```

分开跑：

```bash
# 后端
cd stockManager && ../.venv/bin/python -m pytest
# 或仓库根
.venv/bin/python -m pytest

# 前端
cd stockManager/front && ut run test
```

生产依赖仍是 `stockManager/requirements.txt`。测试包只在 `requirements-dev.txt`（`pytest`、`pytest-django`）。前端 Jest **钉在 29.x**（与 `@umijs/max/test` 配套；不要升到 Jest 30）。

## 目录（不要写进业务代码）

| 层 | 用例位置 | 被测代码 |
|----|----------|----------|
| 后端 | `stockManager/tests/unit/`、`stockManager/tests/api/` | `backend/` |
| 前端 | `stockManager/front/tests/` | `front/src/` |

禁止 `backend/**/test_*.py`、`front/src/**/*.test.ts`。

后端 Django 配置是 `stockManager/tests/django_settings.py`（内存 SQLite + LocMem 缓存 + 固定 `SECRET_KEY`）。API 测在 `tests/api/conftest.py` mock 行情/汇率/估值，**禁止打腾讯/新浪**。

前端 `jest.config.ts` 使用 `@umijs/max/test` 的 `createConfig` / `configUmiAlias`，`testMatch` 仅 `tests/**/*.test.ts`。

## 何时跑全量

改了下面任一路径，结束前应跑 `./scripts/test.sh`：

- `stockManager/backend/`
- `stockManager/front/src/`
- `stockManager/tests/`
- `stockManager/front/tests/`

只改 `.agents/`、`docker/`、README 不必跑测试。

不要测（依赖外网或时钟）：baostock 除权、`nav/refresh` 日频补拉、真实 Redis TTL、「此刻是否开盘」。

## 结束前跑测试

改完代码、准备结束前执行（无匹配改动时脚本自己退出，不跑测试）：

```bash
./scripts/test.sh --if-dirty
```

失败则读输出、修根因，再跑一次。仍失败就停下来说明原因。

临时跳过：创建 `.agents/skip-test-loop`（已 gitignore，不要提交）。

没有 GitHub Actions。
