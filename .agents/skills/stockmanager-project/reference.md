# stockManager 详细参考

SKILL.md 的扩展材料；改缓存、部署时按需阅读。

## 关键文件索引

| 用途 | 路径 |
|------|------|
| Django 配置 | `stockManager/stockManager/settings.py` |
| 根路由 | `stockManager/stockManager/urls.py`（`^api/` → backend） |
| API 路由 | `stockManager/backend/urls.py` |
| 模型 | `stockManager/backend/models.py` |
| 盈亏引擎 | `stockManager/backend/services/calculation/`（`calculator`、`overall`、`single_stock`、`single_metrics`、`money_weighted`、`constants`） |
| 业务门面 | `stockManager/backend/services/integrate.py` |
| 缓存门面 | `stockManager/backend/services/cache/repository.py`（`CacheRepository`） |
| 缓存 key/TTL | `stockManager/backend/services/cache/keys.py` |
| 缓存各 store | `cache/user_store.py`、`price_store.py`、`meta_store.py`、`fx_store.py`、`valuation_store.py`、`hist_high_store.py`、`watch_store.py`、`refresh_policy.py`、`operation_codec.py` |
| 缓存工具 | `stockManager/backend/common/cache.py`（`Cache` 类） |
| 市场抽象（CN/HK） | `stockManager/backend/common/market.py` |
| 行情数据源 | `market/realtimePrice.py`(`fetch_prices`)、`baostock_source.py`、`baiduValuation.py`、`exchangeRate.py`、`historicalHigh.py`、`http_client.py` |
| 持仓推算 | `stockManager/backend/services/calculation/stockHold.py` |
| 除权 | `stockManager/backend/services/dividend.py` |
| 缓存文档 | `stockManager/backend/docs/缓存机制分析.md` |
| Umi 配置 | `stockManager/front/config/config.ts`、`routes.ts`、`proxy.ts` |
| API 客户端 | `stockManager/front/src/services/api.ts` |
| 布局/鉴权 | `stockManager/front/src/app.tsx`、`access.ts` |
| 主页面 | `front/src/pages/StockList/`、`Data/`、`Watch/`、`Admin/` |
| 交易时间 UI | `front/src/components/RightContent/TradingTime.tsx` |
| 环境模板 | `stockManager/stockManager/.env.example`、`docker/.env.example` |
| 备份脚本 | `stockManager/backup/backup.py` |

## 缓存逻辑 key（见 `cache/keys.py`）

| 逻辑 key | 用途 |
|----------|------|
| `user:{id}:operations` | 用户操作列表 |
| `user:{id}:cash_info` | 收益现金 + 出入金流水 |
| `user:{id}:calculated_target` | 计算结果 |
| `user:{id}:watchlist` | 用户关注列表 |
| `stock:price:{code}` | 单股现价 |
| `stock:price:timestamp:{market}` | 各市场价格刷新时间（CN/HK 分开） |
| `stock:meta:all` | 全量 StockMeta |
| `stock:name:sync:mark` | 名称同步标记 |
| `fx:hkd_cny` | 港币兑人民币汇率 |
| `stock:valuation:{code}` | 单股估值（PE/PB 原料） |
| `stock:hist_high:{code}` | 单股历史高价 |

TTL 集中在 `keys.py`（多数 `TTL_DAY=86400`，用户数据 `TTL_USER_DATA=36000`）。

分层：业务门面 `CacheRepository`（聚合编排）→ 各 `*_store`（逻辑 key + TTL + 失效）→ `common/cache.py` 的 `Cache` 类（`get_many`/`set_many`/`delete_pattern`）→ Django Redis。

刷新策略（`refresh_policy.py`，按市场）：`should_refresh_market` 判断各市场是否需刷新（交易时段强制刷新；非交易时段看 `stock:price:timestamp:{market}`）。`price_store` 写价后 `refresh_policy.set_price_timestamp(market)` 并 `user_store.clear_all_calculated_targets()`（`delete_pattern("user:*:calculated_target")`）。交易时段内 `set_calculated_target` 会跳过写缓存。

管理端：`POST /api/clearCache` → `CacheRepository.clear_all()` → `delete_pattern("*")`。

## 数据库与迁移

- 引擎：SQLite；路径 `SQLITE_PATH` 或默认 `stockManager/db.sqlite3`
- 模型：`Operation`、`Info`、`CashFlow`、`StockMeta`、`WatchItem`（FK 到 Django `User`；`StockMeta` 全局共享）
- 迁移目录：`backend/migrations/`（0001 初始 → 0004–0006 CashFlow 与 originCash 迁移 → 0007 日期 → 0008 StockMeta.name → 0009 Operation.sortOrder → 0010 StockMeta.HK 类型 → 0011 WatchItem → 0012 移除 WatchItem.sortOrder）
- 命令：`python manage.py makemigrations` / `migrate`
- Docker 默认 `RUN_MIGRATIONS_ON_START=false`，需时 `docker compose exec backend python manage.py migrate`

## 前端路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/list` | StockList | 持仓盈亏（默认首页） |
| `/data` | Data | 数据分析 |
| `/watch` | Watch | 关注列表（icon `star`） |
| `/admin` | Admin | 需 `canAdmin` |
| `/login` | Login | 无布局 |
| `/account` | Account | 账户 |

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
3. 登录后 `/list`、`/data` 有数据
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
| `models.py` | 迁移文件、Admin 展示、缓存失效信号（`cache/user_store.py`、`cache/watch_store.py`） |
| `calculator.py` / `overall.py` / `single_*.py` | `common/types.py`、`/api/stocks` 输出、`/list`/`/data` 前端展示 |
| `market/realtimePrice.py` | `price_store`/`refresh_policy` 缓存时间戳与分市场判断、CN/HK 拆分、失败兜底 |
| `common/market.py`（CN/HK 抽象） | `price_store`/`fx_store`/`valuation_store`、估值与汇率换算口径 |
| `WatchItem` / `watch_store.py` | `/api/watchlist`、前端 `pages/Watch/`、`valuation_store`/`hist_high_store` |
| `front/config/routes.ts` | 权限 `access.ts`、菜单展示、默认重定向 |
| `docker/nginx.conf` | `/api` 转发、静态资源路径、frontend 重建 |

## backend 依赖（requirements.txt 摘要）

Django、python-dotenv、baostock、pandas、numpy、exchange_calendars、pytz、pyxirr、easyquotation、requests、django-cors-headers、django-extensions、django-werkzeug-debugger-runserver、django-redis、whitenoise、gunicorn

依赖文件：`stockManager/requirements.txt`（应用根，非 `backend/`）。

## Admin 模块

`backend/admin/`：`operation`、`cashflow`、`stockmeta`、`info`、`watchitem`、`session`、`base`；注册在 `admin/__init__.py`。
