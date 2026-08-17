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
| 模型 | `stockManager/backend/models/` |
| 盈亏引擎 | `stockManager/backend/services/calculation/holdings/`（`calculator`、`overall`、`single_stock`、`single_metrics`、`money_weighted`、`stock_hold`） |
| 净值算法 | `stockManager/backend/services/calculation/nav/`（`replay`、`metrics`）；编排在 `services/app/nav.py` |
| 关注列表用例 | `stockManager/backend/services/app/watchlist.py`（`Watchlist.build` / `set_hidden`） |
| 交易结算口径（A 股 / 港股通） | `stockManager/backend/common/domain/settlement.py`（CNY 资金账 + 原币展示账） |
| 业务门面 | `stockManager/backend/services/app/integrate.py` |
| HTTP 装饰器/响应 | `stockManager/backend/common/web/`（`decorators`、`response`、`auth_user`） |
| 缓存门面 | `stockManager/backend/services/cache/repository.py`（`CacheRepository`） |
| 缓存 key/TTL | `stockManager/backend/services/cache/keys.py` |
| 缓存各 store（Redis） | `cache/user/store.py`、`user/codec.py`、`user/watchlist.py`、`cache/market/prices.py`、`fx.py`、`valuation.py`、`hist_high.py`、`meta.py`、`cache/refresh.py` |
| 日频数据同步 | `services/data_sync/`（`daily_price.py`、`daily_fx.py`、`gaps.py`；外部源 → SQLite） |
| 缓存工具 | `stockManager/backend/common/cache.py`（`Cache` 类） |
| 市场抽象（CN/HK） | `stockManager/backend/common/domain/market.py` |
| 交易日历（CN/HK） | `stockManager/backend/common/domain/calendar.py` |
| 行情数据源 | `backend/datasource/`：`realtimePrice.py`(`fetch_prices`)、`baostock_source.py`、`baiduValuation.py`、`exchangeRate.py`、`historicalHigh.py`、`historicalDaily.py`、`http_client.py` |
| 持仓推算 | `stockManager/backend/services/calculation/holdings/stock_hold.py` |
| 除权 | `stockManager/backend/services/app/dividend.py` |
| 缓存文档 | `.agents/skills/stockmanager-project/references/cache.md` |
| 外部数据文档 | `.agents/skills/stockmanager-project/references/external-data.md` |
| Umi 配置 | `stockManager/front/config/config.ts`、`routes.ts`、`proxy.ts` |
| API 客户端 | `stockManager/front/src/services/api.ts` |
| 布局/鉴权 | `stockManager/front/src/app.tsx`、`access.ts` |
| 主页面 | `front/src/pages/StockList/`、`ProfitAnalysis/`、`Transaction/`、`Watch/`、`NavAnalysis/`、`Account/`、`Login/` |
| 交易状态 UI | `front/src/components/RightContent/TradingTime.tsx`（仅渲染，数据 `GET /api/tradingStatus`；后端逻辑 `common/domain/calendar.py:get_trading_time_statuses`） |
| 环境模板 | `stockManager/stockManager/.env.example`、`docker/.env.example` |

## 数据库与迁移

- 引擎：SQLite；路径 `SQLITE_PATH` 或默认 `stockManager/db.sqlite3`
- 模型：`Operation`、`Info`、`CashFlow`、`StockMeta`、`WatchItem`、`PortfolioNavDaily`、`StockDailyPrice`、`HkdCnyDailyRate`（FK 到 Django `User`；`StockMeta` / 日频价 / 日频汇率全局共享）
- 迁移目录：`backend/migrations/`（0001 初始 → … → 0017 Operation 金额 Decimal → 0018 HkdCnyDailyRate）
- 命令：`python manage.py makemigrations` / `migrate`
- Docker 默认 `RUN_MIGRATIONS_ON_START=false`，需时 `docker compose exec backend python manage.py migrate`

## 前端路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/list` | StockList | 持仓盈亏（默认首页） |
| `/profit-analysis` | ProfitAnalysis | 盈亏归因 |
| `/transaction` | Transaction | 交易数据 |
| `/watch` | Watch | 关注列表（icon `star`） |
| `/nav-analysis` | NavAnalysis | 组合净值 |
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
- 实现集中在 `services/calculation/holdings/`（`calculator` / `overall` / `single_*`），类型在 `common/types.py`（`StockData`、`OverallData`）

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
| `models/` | 迁移文件、Admin 展示、缓存失效信号（`cache/user/store.py`、`cache/market/meta.py`、`cache/user/watchlist.py`） |
| `calculation/holdings/`（`calculator` / `overall` / `single_*`） | `common/types.py`、`/api/stocks` 输出、`/list`/`/profit-analysis`/`/transaction` 前端展示；港股结算同时检查 `common/domain/settlement.py` |
| `calculation/nav/` / `app/nav.py` | `/api/nav`、`/api/nav/refresh`、前端 `pages/NavAnalysis/`、`services/data_sync/` |
| `app/watchlist.py` | `/api/watchlist`、`/api/watchlist/hidden`、前端 `pages/Watch/` |
| `backend/datasource/realtimePrice.py` | `cache/market/prices.py` / `cache/refresh.py` 缓存时间戳与分市场判断、CN/HK 拆分、失败兜底 |
| `common/domain/calendar.py` | `refresh.should_refresh_market`、`is_in_trading_hours`、`get_trading_time_statuses`（`/api/tradingStatus`）；交易时段/日历逻辑改动前后端自动一致 |
| `common/domain/market.py`（CN/HK 抽象） | `cache/market/prices.py` / `fx.py` / `valuation.py`、估值与汇率换算口径 |
| `WatchItem` / `cache/user/watchlist.py` | `/api/watchlist`、前端 `pages/Watch/`、`market/valuation.py` / `hist_high.py` |
| `front/config/routes.ts` | 权限 `access.ts`、菜单展示、默认重定向 |
| `docker/nginx.conf` | `/api` 转发、静态资源路径、frontend 重建 |

## backend 依赖（requirements.txt 摘要）

Django、python-dotenv、baostock、pandas、numpy、exchange_calendars、pytz、pyxirr、easyquotation、requests、django-cors-headers、django-extensions、django-werkzeug-debugger-runserver、django-redis、whitenoise、gunicorn

依赖文件：`stockManager/requirements.txt`（应用根，非 `backend/`）。

## Admin 模块

`backend/admin/`：`operation`、`cashflow`、`stockmeta`、`info`、`watchitem`、`session`、`base`；注册在 `admin/__init__.py`。
