# stockManager 详细参考

SKILL.md 的扩展材料；改部署、查路径时按需阅读。

## 深度文档

- 缓存机制全文：[cache.md](cache.md)
- 外部数据全文：[external-data.md](external-data.md)
- 前端主题系统：[theme.md](theme.md)

## 关键文件索引

| 用途 | 路径 |
|------|------|
| Django 配置 | `stockManager/stockManager/settings.py` |
| 根路由 | `stockManager/stockManager/urls.py`（`^api/` → backend） |
| API 路由 | `stockManager/backend/urls.py` |
| 模型 | `stockManager/backend/models.py` |
| 盈亏引擎 | `stockManager/backend/services/calculation/`（`calculator`、`overall`、`single_stock`、`single_metrics`、`money_weighted`、`constants`） |
| 交易结算口径（A 股 / 港股通） | `stockManager/backend/common/settlement.py`（CNY 资金账 + 原币展示账） |
| 业务门面 | `stockManager/backend/services/integrate.py` |
| 缓存门面 | `stockManager/backend/services/cache/repository.py`（`CacheRepository`） |
| 缓存 key/TTL | `stockManager/backend/services/cache/keys.py` |
| 缓存各 store | `cache/user_store.py`、`price_store.py`、`meta_store.py`、`fx_store.py`、`valuation_store.py`、`hist_high_store.py`、`watch_store.py`、`refresh_policy.py`、`operation_codec.py` |
| 缓存工具 | `stockManager/backend/common/cache.py`（`Cache` 类） |
| 市场抽象（CN/HK） | `stockManager/backend/common/market.py` |
| 交易日历（CN/HK） | `stockManager/backend/common/tradingCalendar.py` |
| 行情数据源 | `market/realtimePrice.py`(`fetch_prices`)、`baostock_source.py`、`baiduValuation.py`、`exchangeRate.py`、`historicalHigh.py`、`http_client.py` |
| 持仓推算 | `stockManager/backend/services/calculation/stockHold.py` |
| 除权 | `stockManager/backend/services/dividend.py` |
| 缓存文档 | `.agents/skills/stockmanager-project/references/cache.md` |
| 外部数据文档 | `.agents/skills/stockmanager-project/references/external-data.md` |
| Umi 配置 | `stockManager/front/config/config.ts`、`routes.ts`、`proxy.ts` |
| API 客户端 | `stockManager/front/src/services/api.ts` |
| 布局/鉴权 | `stockManager/front/src/app.tsx`、`access.ts` |
| 主页面 | `front/src/pages/StockList/`、`ProfitAnalysis/`、`Transaction/`、`Watch/`、`Account/`、`Login/` |
| 交易状态 UI | `front/src/components/RightContent/TradingTime.tsx`（仅渲染，数据 `GET /api/tradingStatus`；后端逻辑 `common/tradingCalendar.py:get_trading_time_statuses`） |
| 环境模板 | `stockManager/stockManager/.env.example`、`docker/.env.example` |

## 数据库与迁移

- 引擎：SQLite；路径 `SQLITE_PATH` 或默认 `stockManager/db.sqlite3`
- 模型：`Operation`、`Info`、`CashFlow`、`StockMeta`、`WatchItem`（FK 到 Django `User`；`StockMeta` 全局共享）
- 迁移目录：`backend/migrations/`（0001 初始 → 0002 模型选项 → 0003 用户数据迁移 → 0004–0006 CashFlow 与 originCash → 0007 日期 → 0008 StockMeta.name → 0009 Operation.sortOrder → 0010 StockMeta.HK → 0011 WatchItem → 0012 移除 WatchItem.sortOrder → 0013 WatchItem.hidden → 0014 Operation/WatchItem 改关联 StockMeta → 0015 Operation.amount（港股通实际 CNY 成交额））
- 命令：`python manage.py makemigrations` / `migrate`
- Docker 默认 `RUN_MIGRATIONS_ON_START=false`，需时 `docker compose exec backend python manage.py migrate`

## 前端路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/list` | StockList | 持仓盈亏（默认首页） |
| `/profit-analysis` | ProfitAnalysis | 盈亏归因 |
| `/transaction` | Transaction | 交易数据 |
| `/watch` | Watch | 关注列表（icon `star`） |
| `/login` | Login | 无布局 |
| `/account` | Account | 账户 |

管理后台无前端路由；`canAdmin` 用户从头像菜单打开 Django Admin `/sys/admin/`（新窗口）。

生产 `API_BASE_URL = ''`（同源 `/api/...`），无 carSales 式 `VITE_*` 运行时注入。

## Dev vs Prod

| 项 | 开发 | 生产（Docker） |
|----|------|----------------|
| 前端 publicPath | `/` | `/static/` |
| Django DEBUG | 常为 true | false |
| CORS | DEBUG 时允许全部 | 显式 origins + `CSRF_TRUSTED_ORIGINS_EXTRA` |
| 静态资源 | Umi dev server | Nginx + backend `collectstatic`（仅 Admin） |
| 构建 | 本地 `ut run dev` | **仅** `Dockerfile.frontend` 内 `ut run build` |

## 雪球指标（摘录）

完整公式见根目录 `README.md`。要点：

- **持仓成本**：清仓后重新买入会重置成本基数（README 有说明）
- **浮动盈亏**：`(当前价 - 持仓成本) × 持股数`
- **当日盈亏**：有昨市值与无昨市值两套公式
- 实现集中在 `calculator.py`，类型在 `common/types.py`（`StockData`、`OverallData`）

## Docker 手动验证清单

1. `docker compose -f docker/docker-compose.yml --env-file docker/.env ps` 三服务 healthy
2. 浏览器打开 `http://localhost:${FRONTEND_PUBLISH_PORT}`（默认 8080）
3. 登录后 `/list`、`/profit-analysis`、`/transaction` 有数据
4. 改前端后：`docker compose build frontend && docker compose up -d frontend`

## 常用排障命令（按场景）

- Django 配置体检：`cd stockManager && python manage.py check`
- 查看 URL 映射：`cd stockManager && python manage.py show_urls`（若安装 django-extensions）
- 前端类型检查：`cd stockManager/front && ut run type-check`
- 前端代理确认：`cd stockManager/front && cat config/proxy.ts`
- Redis key 抽查：`redis-cli --scan --pattern 'user:*:calculated_target' | head`
- Docker 服务状态：`docker compose -f docker/docker-compose.yml --env-file docker/.env ps`

## 变更影响面速查

| 你改了什么 | 还要联动检查 |
|-----------|----------------|
| `models.py` | 迁移文件、Admin 展示、缓存失效信号（`cache/user_store.py`、`cache/meta_store.py`、`cache/watch_store.py`） |
| `calculator.py` / `overall.py` / `single_*.py` | `common/types.py`、`/api/stocks` 输出、`/list`/`/profit-analysis`/`/transaction` 前端展示；港股结算同时检查 `common/settlement.py` |
| `market/realtimePrice.py` | `price_store`/`refresh_policy` 缓存时间戳与分市场判断、CN/HK 拆分、失败兜底 |
| `common/tradingCalendar.py` | `refresh_policy.should_refresh_market`、`is_in_trading_hours`、`get_trading_time_statuses`（`/api/tradingStatus`）；交易时段/日历逻辑改动前后端自动一致 |
| `common/market.py`（CN/HK 抽象） | `price_store`/`fx_store`/`valuation_store`、估值与汇率换算口径 |
| `WatchItem` / `watch_store.py` | `/api/watchlist`、前端 `pages/Watch/`、`valuation_store`/`hist_high_store` |
| `front/config/routes.ts` | 权限 `access.ts`、菜单展示、默认重定向 |
| `docker/nginx.conf` | `/api` 转发、静态资源路径、frontend 重建 |

## backend 依赖（requirements.txt 摘要）

Django、python-dotenv、baostock、pandas、numpy、exchange_calendars、pytz、pyxirr、easyquotation、requests、django-cors-headers、django-extensions、django-werkzeug-debugger-runserver、django-redis、whitenoise、gunicorn

依赖文件：`stockManager/requirements.txt`（应用根，非 `backend/`）。

## Admin 模块

`backend/admin/`：`operation`、`cashflow`、`stockmeta`、`info`、`watchitem`、`session`、`base`；注册在 `admin/__init__.py`。
